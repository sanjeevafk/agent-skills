# Local CI Simulation & Push Protocol
1. **Simulate CI Locally**: Before declaring any change complete or pushing to remote, always execute the full CI suite locally (e.g., linter, static type checker, unit/integration test suite).
2. **Environment Isolation**: Ensure tests run cleanly in both local and isolated environments (e.g., without relying on uncommitted local system state or hardcoded personal database paths).
3. **Verification Before Push**: Only make final commits and push to remote after all linter, typecheck, and test commands return zero exit codes.
