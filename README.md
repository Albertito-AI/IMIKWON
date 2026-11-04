# IMIKWON

**Build with Kimi. Keep control of the code and the cost.**

[![Checks](https://github.com/Albertito-AI/IMIKWON/actions/workflows/tests.yml/badge.svg)](https://github.com/Albertito-AI/IMIKWON/actions/workflows/tests.yml)
[![MIT licence](https://img.shields.io/badge/licence-MIT-a6d83d)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-6c35c4)](pyproject.toml)

IMIKWON is a free, MIT-licensed command-line coding assistant for **Kimi K3.1 Pro**. Select a small set of files, describe a task, receive a proposed fix and a model review, inspect the diff, then apply it and run your tests. The runtime uses only Python's standard library.

**Public alpha: 0.1.0a1.** Offline and mocked integration checks pass. Live Kimi inference, comparative coding quality and measured savings have **not** been validated for this release. The [verification record](docs/VERIFICATION.md) states exactly what was checked.

[Start on the website](https://www.alberttansinhon.com/imikwon/) · [How costs work](docs/COSTS.md) · [Model and source notes](docs/MODEL.md) · [Contribute](CONTRIBUTING.md)

## Try it in one minute, without an API key

Install [Python](https://www.python.org/downloads/) 3.10 or later and [Git](https://git-scm.com/downloads), then:

```sh
git clone https://github.com/Albertito-AI/IMIKWON.git
cd IMIKWON
python -m imikwon demo
```

On systems where Python is named `python3`, use that instead. The demo creates a temporary project, runs a failing test, shows a fixture patch, applies it, and reruns the test:

```text
Offline fixture. No AI call, API key or charge.
Before: failed
-    return a - b
+    return a + b
After: passed
```

This is a reproducible workflow demonstration. Its patch is predetermined and does not measure Kimi's ability.

## Use Kimi on your own project

Install the command in a virtual environment from your cloned checkout:

```sh
python -m venv .venv
# macOS / Linux:
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
imikwon doctor
```

Get your own API key from the [Kimi API Platform](https://platform.kimi.ai/). API billing is separate from Kimi app and Code subscriptions. IMIKWON has no subscription charge or API markup. The provider charges your account directly.

Set `MOONSHOT_API_KEY` in your environment. Avoid typing the actual key into a shell command that will remain in history. In Bash, enter it privately with:

```sh
read -rs -p 'Moonshot API key: ' MOONSHOT_API_KEY; echo
export MOONSHOT_API_KEY
```

PowerShell 7 users can use `$env:MOONSHOT_API_KEY = Read-Host -MaskInput 'Moonshot API key'`. Do not put keys into a repository or issue report.

Choose the source and test files explicitly, including any new file you want created:

```sh
cd /path/to/your/project
imikwon scope --file src/calculator.py --file tests/test_calculator.py
imikwon propose "Fix addition for negative numbers and add regression tests" \
  --file src/calculator.py --file tests/test_calculator.py \
  --input-ceiling 6 --output-price 10 --budget 1
```

The displayed rates were checked against official Kimi pages on **5 November 2026 (Singapore)**. For standard K3.1 Pro, the example uses an input ceiling of $6 per million tokens, covering the $2 uncached-input rate plus the higher $4 one-hour cache-write rate, and $10 per million output tokens. Recheck your actual provider's rates before use. These are conservative admission-control values, not a promised bill. [Calculation and limits](docs/COSTS.md).

The command sends **only the explicitly selected files and your task** to the configured provider. The review call also sends the first response, including the model's reasoning field as required by Kimi. File names, hashes and content are included. Review selected files for personal or confidential information first. No automatic repository crawl occurs.

Copy the proposal filename printed by the command:

```sh
imikwon show .imikwon/ACTUAL_JOB_ID.proposal.json
imikwon apply .imikwon/ACTUAL_JOB_ID.proposal.json --yes
imikwon check -- python -m unittest discover -s tests
git diff
```

Replace `ACTUAL_JOB_ID` with the printed value. `apply` requires a fresh, matching source hash for **every** file supplied as context. `check` runs only the command you specify. Test suggestions from the model are never executed automatically.

## What makes it useful

| Need | Implemented behaviour |
| --- | --- |
| Keep context affordable | Exact file selection; 24 files maximum; 64 KB/file; 160 KB combined context. |
| Control API spending | Explicit output limits, two calls maximum, conservative per-call reservations, no automatic retry, local usage records. |
| Improve proposed changes | A second model pass examines the draft for errors. This is self-review, not independent verification. |
| Inspect before changing | Unified diff and explicit application; stale inputs stop the write. |
| Keep credentials out | Common secret patterns and sensitive paths blocked; key stays in the process environment. Detection is incomplete. |
| Establish test evidence | Operator-selected local commands record exit status, timeout and bounded output. A passing check applies only to that command. |
| Reuse freely | MIT licence for IMIKWON's code and documentation, including commercial reuse. |

Use `--single-pass` to skip self-review for small tasks. Use `--effort low` to request less reasoning, or `--effort max` for difficult work. These choices can affect quality. There is no automatic substitution with a cheaper model.

## Scope and limits

This alpha handles bounded text-file creation and modification. It does not execute model-selected shell commands, install project dependencies, delete files, commit, push, run a background agent, or host free inference. It does not include a browser IDE. Run project tests only in a trusted environment: local tests execute with your user permissions. It is **not a sandbox**.

Use a Git branch and review all changes. The apply operation rolls back ordinary write failures but is not a crash-proof multi-file transaction. Do not edit the same files concurrently. Windows process-tree cleanup after a timed-out test has narrower coverage than POSIX process-group cleanup. The [security policy](SECURITY.md) explains the boundaries.

The default endpoint is `https://api.moonshot.ai/v1` and model is `kimi-k3.1-pro`. An alternative HTTPS endpoint and model can be selected with `--base-url` and `--model`; that endpoint receives the API key, code and task. It must support this API contract. Other providers and self-hosted engines are not acceptance-tested.

**IMIKWON is open-source. Kimi is a separate upstream model.** Moonshot describes K3.1 Pro as open-weight and announced a weights release by 4 November. We have not verified a downloadable K3.1 Pro checkpoint and its specific licence. No model weights are redistributed and no rights over Moonshot's model are claimed. This launch uses the documented API. [Evidence and attribution](docs/MODEL.md).

## Build with us

The purpose is practical access: let more people learn, inspect, adapt and build with capable coding models. Useful contributions include live API smoke-test reports, clearly specified coding tasks, measured cost records, accessibility improvements and reproducible bug reports.

```sh
python -m unittest discover -s tests -v
python -m imikwon demo
```

Created by **Albert Tan Sin Hon**. Engineering and documentation were developed with AI assistance. This is an independent project with no Moonshot endorsement. Please report reproducible issues without API keys, private code or personal information.
