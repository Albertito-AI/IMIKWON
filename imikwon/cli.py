import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

from . import __version__
from .core import BASE_URL, MODEL, Budget, Client, Problem, apply_proposal, atomic_write, collect, digest, preview, propose, run_check


def print_safe(text):
    # Source, model output and subprocess output may contain terminal escapes.
    print("".join(c if c in "\n\t" or (ord(c) >= 32 and ord(c) != 127 and not 128 <= ord(c) <= 159) else "?" for c in str(text)))


def state_dir(root):
    path = root / ".imikwon"
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise Problem(".imikwon must be an ordinary local directory.")
    path.mkdir(mode=0o700, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def save_json(path, value):
    if path.is_symlink():
        raise Problem("Refusing to write through a symlink.")
    atomic_write(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), 0o600)


def load_proposal(name):
    path = Path(name)
    if path.stat().st_size > 4_000_000:
        raise Problem("Proposal file is too large.")
    return json.loads(path.read_text(encoding="utf-8"))


def demo():
    with tempfile.TemporaryDirectory(prefix="imikwon-demo-") as temp:
        root = Path(temp).resolve()
        before = "def add(a, b):\n    return a - b\n"
        (root / "calc.py").write_bytes(before.encode())
        (root / "test_calc.py").write_bytes(b"import unittest\nfrom calc import add\nclass TestAdd(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n")
        proposal = {"format": "imikwon.proposal.v1", "project": str(root), "model": "offline-fixture", "reviewed_by_model": False, "files": [{"path": "calc.py", "sha256": digest(before.encode())}], "summary": "Fix the synthetic addition bug.", "changes": [{"path": "calc.py", "content": "def add(a, b):\n    return a + b\n"}], "tests": ["python -m unittest discover"], "risks": [], "verification": "not_run"}
        print("Offline fixture. No AI call, API key or charge. This is a workflow demo, not a model benchmark.")
        before_check = run_check(root, [sys.executable, "-B", "-m", "unittest", "discover"])
        print("Before:", before_check["verification"])
        print_safe(preview(root, proposal))
        apply_proposal(root, proposal)
        after = run_check(root, [sys.executable, "-B", "-m", "unittest", "discover"])
        print("After:", after["verification"])
        print_safe(after["output"])
        return 0 if before_check["verification"] == "failed" and after["verification"] == "passed" else 1


def parser():
    p = argparse.ArgumentParser(description="IMIKWON: focused Kimi coding, inspectable changes and visible cost reservations.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--root", default=".", help="Project directory (before the subcommand)")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run a free, offline failing-test-to-passing-test fixture")
    sub.add_parser("doctor", help="Check configuration without contacting a provider")
    scope = sub.add_parser("scope", help="Inspect exact file paths and sizes before transmission")
    scope.add_argument("--file", action="append", required=True)
    plan = sub.add_parser("propose", help="Send selected files to the provider and save a reviewed proposal")
    plan.add_argument("task")
    plan.add_argument("--file", action="append", required=True, help="Exact relative path, repeatable; a missing path permits a new file")
    plan.add_argument("--budget", default="1.00", help="Local reservation limit in USD; not a provider billing guarantee")
    plan.add_argument("--input-ceiling", default=os.environ.get("IMIKWON_INPUT_CEILING"), help="USD/million: max(input miss, cache hit) PLUS highest possible cache-write rate")
    plan.add_argument("--output-price", default=os.environ.get("IMIKWON_OUTPUT_PRICE"), help="USD/million output tokens including reasoning")
    plan.add_argument("--base-url", default=os.environ.get("IMIKWON_BASE_URL", BASE_URL))
    plan.add_argument("--model", default=os.environ.get("IMIKWON_MODEL", MODEL))
    plan.add_argument("--effort", choices=("low", "high", "max"), default="high")
    plan.add_argument("--max-output", type=int, default=8192)
    plan.add_argument("--single-pass", action="store_true", help="Skip the model review pass to reduce API calls")
    for name in ("show", "apply"):
        s = sub.add_parser(name, help="Inspect a saved diff" if name == "show" else "Apply a previously reviewed proposal")
        s.add_argument("proposal")
        if name == "apply":
            s.add_argument("--yes", action="store_true", help="Confirm you reviewed this proposal; required")
    check = sub.add_parser("check", help="Run an explicit local test command and record its result")
    check.add_argument("--timeout", type=int, default=120)
    check.add_argument("argv", nargs=argparse.REMAINDER)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if not root.is_dir():
            raise Problem("Project directory does not exist.")
        if args.command == "demo":
            return demo()
        if args.command == "doctor":
            print(json.dumps({"version": __version__, "python": sys.version.split()[0], "model": os.environ.get("IMIKWON_MODEL", MODEL), "api_key_present": bool(os.environ.get("MOONSHOT_API_KEY")), "rates_configured": bool(os.environ.get("IMIKWON_INPUT_CEILING") and os.environ.get("IMIKWON_OUTPUT_PRICE")), "provider_contacted": False}, indent=2))
        elif args.command == "scope":
            print_safe(json.dumps([{k: v for k, v in f.items() if k != "content"} | {"bytes": len(f["content"].encode())} for f in collect(root, args.file)], indent=2))
            print("Only these exact files will be sent. Review their contents for confidential data; automated secret detection is incomplete.")
        elif args.command == "propose":
            budget = Budget(args.budget, args.input_ceiling, args.output_price)
            client = Client(os.environ.get("MOONSHOT_API_KEY"), args.base_url, args.model, args.effort, args.max_output)
            directory = state_dir(root)
            job = uuid.uuid4().hex[:12]
            print_safe(f"Provider: {client.base_url} | Model: {client.model} | Reservation limit: ${budget.limit:.2f}")
            print("Sending selected context. Model review:", "off" if args.single_pass else "on")
            try:
                proposal = propose(root, args.file, args.task, client, budget, review=not args.single_pass)
                out = directory / f"{job}.proposal.json"
                save_json(out, proposal)
            finally:
                save_json(directory / f"{job}.cost.json", budget.report())
            print_safe(proposal["summary"])
            print_safe(preview(root, proposal))
            print_safe(f"Saved: {out}\nInspect: imikwon --root {root} show {out}\nNo source files changed; tests have not run.")
        elif args.command in ("show", "apply"):
            proposal = load_proposal(args.proposal)
            print_safe(preview(root, proposal))
            if args.command == "show":
                print_safe(json.dumps({k: proposal.get(k) for k in ("summary", "tests", "risks", "cost", "verification")}, indent=2))
            else:
                if not args.yes:
                    raise Problem("Inspect the diff, then use apply PROPOSAL --yes to confirm it.")
                result = apply_proposal(root, proposal)
                result["proposal_sha256"] = digest(Path(args.proposal).read_bytes())
                save_json(state_dir(root) / f"{uuid.uuid4().hex[:12]}.apply.json", result)
                print_safe(json.dumps(result, indent=2))
                print("Run your tests with imikwon check -- <command>. Review changes before committing.")
        elif args.command == "check":
            if not 1 <= args.timeout <= 3600:
                raise Problem("Test timeout must be between 1 and 3600 seconds.")
            command = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv
            result = run_check(root, command, args.timeout)
            result["source_note"] = "Result for this command at execution time; subsequent edits invalidate it."
            out = state_dir(root) / f"{uuid.uuid4().hex[:12]}.check.json"
            save_json(out, result)
            print_safe(result["output"])
            print_safe(f"Check: {result['verification']} | Record: {out}")
            return 0 if result["verification"] == "passed" else 1
        return 0
    except (Problem, OSError, ValueError, KeyError, TypeError) as exc:
        print_safe(f"IMIKWON: {exc}")
        return 2
    except KeyboardInterrupt:
        print("IMIKWON: interrupted. Check the cost record; an in-flight API request may still be billed.")
        return 130
