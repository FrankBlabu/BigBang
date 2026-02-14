---
name: bigbang_coverage
description: Increase test coverage
agent: agent
---

# Objective

> Your goal is to increase the test coverage for unit tests in a balanced way.

The code coverage should be high enough to have a well tested software, but not pedantic so that runtime and maintenance effort can be kept reasonable.

# Workflow

- Execute the task `Coverage` in vscode to compute the test code coverage and generate all necessary files.
- The coverage result is written into the `build/coverage/` directory. Analyse it for coverage results.
- Make a plan about how to increase code coverage in a balanced way. Especially think about:
  - If a code path is critical and should be covered.
  - If a code path is complex and should be covered.
  - If a code path is simple and does not need to be covered.
  - If a code path is already covered by integration tests and does not need to be covered by unit tests.
  - If a code path is hard to cover by unit tests and if the effort is worth it.
  - If a code path should be covered so that the coding agent is able to 'experience' the result of its work better during testing.
- Implement additional tests or extend tests to increase the coverage in a balanced way.
- Repeat the coverage analysis until a balanced coverage is achieved.
