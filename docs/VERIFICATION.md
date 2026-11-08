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

## Diff-preview correction, 8 November 2026

Files without a final newline previously joined removed and added lines together
in the preview, for example `-old+new`. They could also join the next file's
header. The preview now separates each record and marks the missing final
newline explicitly. File contents and apply behaviour are unchanged.

Four initial regression tests cover old and new final-newline combinations,
multiple files, creation and unchanged context. The original implementation
failed six assertions across these tests. Separate AI review identified that
diff records must split on LF only; two further tests cover lone CR, Unicode
separators and CRLF without false missing-newline markers. After the correction,
all 38 tests passed locally on Python 3.12.14 / Linux, and the offline demo still
failed before its fixture fix and passed afterwards. No provider was contacted.
Hosted matrix results remain separate evidence in the associated pull request
and Actions records.

## Next acceptance evidence

A live tester should use a disposable project and their own key, record provider/model/date, configured rates, task specification, source revision, proposal, local test results and actual token usage. Remove secrets and private code before sharing. Include failed tasks and all billed attempts when calculating cost per success. A model self-review must not be counted as an independent review.

The initial live smoke task should change `add(a, b)` from subtraction to addition and add tests for zero and negative arguments. Then test a small bug in a real project with a pre-existing failing test. No claimed success rate should be published until tasks, evaluation rules and outcomes can be inspected.

## Malformed-provider response correction, 8 November 2026

Null or scalar choices and messages could previously escape response validation
as an unhandled `AttributeError`. These shapes now produce a controlled error.
The existing reservation and returned usage remain recorded, with no retry,
saved proposal or source edits. A valid assistant message remains intact for
the subsequent model-review call.

Two mocked-HTTP regression tests cover malformed nested response types and the
complete CLI failure path, including its saved cost record. The original code
produced nine errors across those cases. After integrating the prior diff-preview
correction, all 40 tests passed locally on Python 3.12.14 / Linux against base
`a3dba4b1c763416801d5fbf0f35e9c524cce21f4` plus this correction; the offline
demo also passed. No live provider was contacted. Hosted checks are recorded in
the associated pull request.
