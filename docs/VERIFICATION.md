# Release verification: 0.1.0a1

Checked locally on 5 November 2026 (Singapore), Python 3.12.14 on Linux.

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 32 tests passed locally, including canonical temporary paths. See CI for the exact release revision. |
| `python -m imikwon demo` | Synthetic test failed before application and passed afterwards. No API used. |
| Documented Kimi request shape | Mocked HTTP transport verifies model, output cap, schema and preserved reasoning. |
| Scope and write guards | Tests cover traversal, symlinks, hardlinks, credential patterns, binary/large files, duplicate paths, stale context and rollback after a simulated write failure. |
| Spending guard | Test proves an over-budget request is refused before the mocked network transport is called. |
| Local test runner | Passing/failing results, timeout and removal of named credential environment variables checked. |
| Live Kimi call | **Not run: no Moonshot key configured in the launch environment.** |
| Real coding quality / savings | **Not measured.** |
| Independent security audit | **Not performed.** |

The public Actions workflow runs tests, the offline demo and installation on Linux, Windows and macOS with Python 3.10 and 3.12. A workflow definition is not a passing run; inspect [Actions](https://github.com/Albertito-AI/IMIKWON/actions) for current results.

## Next acceptance evidence

A live tester should use a disposable project and their own key, record provider/model/date, configured rates, task specification, source revision, proposal, local test results and actual token usage. Remove secrets and private code before sharing. Include failed tasks and all billed attempts when calculating cost per success. A model self-review must not be counted as an independent review.

The initial live smoke task should change `add(a, b)` from subtraction to addition and add tests for zero and negative arguments. Then test a small bug in a real project with a pre-existing failing test. No claimed success rate should be published until tasks, evaluation rules and outcomes can be inspected.
