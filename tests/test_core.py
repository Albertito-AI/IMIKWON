import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from imikwon import core
from imikwon.cli import main


def answer(content="def add(a, b):\n    return a + b\n"):
    return {"summary": "Correct addition", "changes": [{"path": "calc.py", "content": content}], "tests": ["Run unit tests"], "risks": ["Execution unverified"]}


class FakeClient:
    model = core.MODEL

    def __init__(self, replies=None):
        self.messages = []
        self.replies = list(replies or [answer(), answer()])

    def complete(self, messages, budget):
        self.messages.append(json.loads(json.dumps(messages)))
        return {"role": "assistant", "content": json.dumps(self.replies.pop(0)), "reasoning_content": "retained provider fixture", "custom_field": "preserved"}


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = "def add(a, b):\n    return a - b\n"
        (self.root / "calc.py").write_text(self.source)

    def proposal(self, names=None, client=None):
        return core.propose(self.root, names or ["calc.py"], "Fix addition", client or FakeClient(), core.Budget(2, 6, 15))

    def test_generate_does_not_write_source(self):
        p = self.proposal()
        self.assertEqual((self.root / "calc.py").read_text(), self.source)
        self.assertEqual(p["verification"], "not_run")

    def test_review_preserves_complete_assistant_message(self):
        client = FakeClient()
        self.proposal(client=client)
        previous = client.messages[1][-2]
        self.assertEqual(previous["reasoning_content"], "retained provider fixture")
        self.assertEqual(previous["custom_field"], "preserved")

    def test_review_can_correct_draft(self):
        client = FakeClient([answer("bad draft"), answer("corrected")])
        self.assertEqual(self.proposal(client=client)["changes"][0]["content"], "corrected")

    def test_single_pass_only_calls_once(self):
        client = FakeClient()
        p = core.propose(self.root, ["calc.py"], "Fix", client, core.Budget(1, 6, 15), review=False)
        self.assertEqual(len(client.messages), 1)
        self.assertFalse(p["reviewed_by_model"])

    def test_apply_and_diff(self):
        p = self.proposal()
        self.assertIn("+    return a + b", core.preview(self.root, p))
        core.apply_proposal(self.root, p)
        self.assertIn("return a + b", (self.root / "calc.py").read_text())

    def test_stale_file_refused(self):
        p = self.proposal()
        (self.root / "calc.py").write_text("user edit")
        with self.assertRaises(core.Problem):
            core.apply_proposal(self.root, p)
        self.assertEqual((self.root / "calc.py").read_text(), "user edit")

    def test_all_context_files_rechecked(self):
        (self.root / "other.py").write_text("original")
        p = self.proposal(["calc.py", "other.py"])
        (self.root / "other.py").write_text("changed")
        with self.assertRaises(core.Problem):
            core.apply_proposal(self.root, p)
        self.assertEqual((self.root / "calc.py").read_text(), self.source)

    def test_new_file(self):
        client = FakeClient([{"summary": "New", "changes": [{"path": "new.py", "content": "x = 1\n"}], "tests": [], "risks": []}])
        p = core.propose(self.root, ["new.py"], "New", client, core.Budget(1, 6, 15), review=False)
        core.apply_proposal(self.root, p)
        self.assertEqual((self.root / "new.py").read_text(), "x = 1\n")

    def test_path_guards(self):
        for name in ("../outside", "/tmp/evil", "a/../../b", "a\\b", ".git/config", ".github/workflows/x.yml", ".env", "a/.env.prod", "id_rsa", ".npmrc", "a//b", "./calc.py", "C:/x", "a\n.py", ".GIT/config", ".git./config", "CON.txt", "src/*", "file "):
            with self.subTest(name=name), self.assertRaises(core.Problem):
                core.collect(self.root, [name])

    @unittest.skipIf(os.name == "nt", "symlink privileges vary on Windows")
    def test_symlink_guards(self):
        (self.root / "linked.py").symlink_to(self.root / "calc.py")
        with self.assertRaises(core.Problem):
            core.collect(self.root, ["linked.py"])
        (self.root / "folder").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(core.Problem):
            core.collect(self.root, ["folder/new.py"])

    @unittest.skipIf(os.name == "nt", "hardlink support varies")
    def test_hardlink_rejected(self):
        os.link(self.root / "calc.py", self.root / "linked.py")
        with self.assertRaises(core.Problem):
            core.collect(self.root, ["calc.py"])

    def test_secrets_rejected(self):
        for secret in ("sk-" + "a" * 30, "-----BEGIN PRIVATE KEY-----", 'password = "realcredential987"'):
            (self.root / "calc.py").write_text(secret)
            with self.assertRaises(core.Problem):
                core.collect(self.root, ["calc.py"])

    def test_oversize_and_binary_rejected(self):
        for content in (b"x" * (core.MAX_FILE + 1), b"\0hello", b"\xff"):
            (self.root / "calc.py").write_bytes(content)
            with self.assertRaises(core.Problem):
                core.collect(self.root, ["calc.py"])

    def test_scope_duplicates_rejected(self):
        with self.assertRaises(core.Problem):
            core.collect(self.root, ["calc.py", "calc.py"])

    def test_out_of_scope_model_change_rejected(self):
        a = answer()
        a["changes"][0]["path"] = "other.py"
        with self.assertRaises(core.Problem):
            self.proposal(client=FakeClient([a]))

    def test_invalid_json_rejected(self):
        with self.assertRaises(core.Problem):
            core.validate_answer("not json", [])

    def test_duplicate_model_change_rejected(self):
        a = answer()
        a["changes"].append(a["changes"][0])
        with self.assertRaises(core.Problem):
            self.proposal(client=FakeClient([a]))

    def test_different_project_refused(self):
        p = self.proposal()
        p["project"] = "/another/project"
        with self.assertRaises(core.Problem):
            core.apply_proposal(self.root, p)

    def test_partial_io_failure_rolls_back(self):
        (self.root / "second.py").write_text("before")
        a = answer()
        a["changes"].append({"path": "second.py", "content": "after"})
        p = self.proposal(["calc.py", "second.py"], FakeClient([a, a]))
        original_write = core.atomic_write
        def fail_second(path, data, mode=0o600):
            if path.name == "second.py":
                raise OSError("simulated disk error")
            original_write(path, data, mode)
        with patch.object(core, "atomic_write", fail_second), self.assertRaises(OSError):
            core.apply_proposal(self.root, p)
        self.assertEqual((self.root / "calc.py").read_text(), self.source)

    def test_apply_requires_explicit_yes(self):
        path = self.root / "proposal.json"
        path.write_text(json.dumps(self.proposal()))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "apply", str(path)]), 2)
        self.assertEqual((self.root / "calc.py").read_text(), self.source)

    def test_check_records_failure(self):
        r = core.run_check(self.root, [sys.executable, "-c", "raise SystemExit(3)"])
        self.assertEqual(r["exit_code"], 3)
        self.assertEqual(r["verification"], "failed")

    def test_check_times_out(self):
        r = core.run_check(self.root, [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.1)
        self.assertEqual(r["verification"], "timeout")

    def test_check_removes_provider_key(self):
        with patch.dict(os.environ, {"MOONSHOT_API_KEY": "test-value"}):
            r = core.run_check(self.root, [sys.executable, "-c", "import os; print('MOONSHOT_API_KEY' in os.environ)"])
        self.assertEqual(r["output"].strip(), "False")

    def test_demo_end_to_end(self):
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            result = main(["demo"])
        self.assertEqual(result, 0, stream.getvalue())
        self.assertIn("Before: failed", stream.getvalue())
        self.assertIn("After: passed", stream.getvalue())

    @unittest.skipIf(os.name == "nt", "symlink privileges vary on Windows")
    def test_demo_canonicalises_temporary_directory(self):
        alias = self.root / "alias"
        target = self.root / "actual"
        target.mkdir()
        alias.symlink_to(target, target_is_directory=True)
        with patch.object(tempfile, "tempdir", str(alias)), contextlib.redirect_stdout(io.StringIO()) as stream:
            result = main(["demo"])
        self.assertEqual(result, 0, stream.getvalue())


class BudgetTests(unittest.TestCase):
    def test_budget_stops_before_network(self):
        client = core.Client("dummy-key")
        with patch.object(core, "build_opener") as opener:
            with self.assertRaises(core.Problem):
                client.complete([], core.Budget(0.00001, 6, 15))
            opener.assert_not_called()

    def test_reservations_accumulate(self):
        b = core.Budget(1, 6, 15)
        payload = {"messages": [], "max_completion_tokens": 8192}
        first = b.reserve(payload)
        b.reserve(payload)
        self.assertAlmostEqual(b.reserved, first * 2)

    def test_invalid_prices_rejected(self):
        for value in (None, "NaN", "inf", -1, 0):
            with self.subTest(value=value), self.assertRaises(core.Problem):
                core.Budget(1, value, 15)

    def test_unencrypted_and_credential_urls_rejected(self):
        for url in ("http://api.example.com/v1", "https://user:pass@api.example.com", "https://api.example.com?key=x"):
            with self.subTest(url=url), self.assertRaises(core.Problem):
                core.Client("dummy", url)

    def test_api_contract(self):
        response = {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(answer()), "reasoning_content": "fixture"}}], "usage": {"prompt_tokens": 120, "completion_tokens": 90}}
        class Response(io.BytesIO):
            pass
        with patch.object(core, "build_opener") as opener:
            opener.return_value.open.return_value = Response(json.dumps(response).encode())
            budget = core.Budget(1, 6, 15)
            result = core.Client("dummy-key").complete([], budget)
            request = opener.return_value.open.call_args.args[0]
            payload = json.loads(request.data)
        self.assertEqual(payload["model"], "kimi-k3.1-pro")
        self.assertEqual(payload["max_completion_tokens"], 8192)
        self.assertNotIn("temperature", payload)
        self.assertEqual(result["reasoning_content"], "fixture")
        self.assertEqual(budget.calls[0]["provider_usage"]["prompt_tokens"], 120)

    def test_truncated_output_rejected(self):
        response = {"choices": [{"finish_reason": "length", "message": {"role": "assistant", "content": "{}"}}]}
        with patch.object(core, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(json.dumps(response).encode())
            with self.assertRaises(core.Problem):
                core.Client("dummy-key").complete([], core.Budget(1, 6, 15))

    def test_redirect_refused(self):
        with self.assertRaises(core.Problem):
            core.NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere.example")


if __name__ == "__main__":
    unittest.main()
