[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Mode Selection
- **1-9 files**: Use native tools (Grep + Edit with replace_all)
- **10+ files**: Automatically use `code-execution` skill
**Execution example (50 files)**
### Rename Function
- Find: `Grep(pattern="getUserData", output_mode="files_with_matches")`
- Count: "Found 15 occurrences in 5 files"
- Replace in each file with `replace_all=true`
- Verify: Re-run Grep
- Suggest: Run tests
### Replace Deprecated Pattern
- Find: `Grep(pattern="\\bvar\\s+\\w+", output_mode="content", -n=true)`
- Analyze: Check if reassigned (let) or constant (const)
- Replace: `Edit(old_string="var count = 0", new_string="let count = 0")`
- Verify: `npm run lint`
### Update API Calls
- Find: `Grep(pattern="/api/auth/login", output_mode="content", -n=true)`
- Replace: `Edit(old_string="'/api/auth/login'", new_string="'/api/v2/authentication/login'", replace_all=true)`
- Test: Recommend integration tests
## Best Practices
**Planning**
- Find all instances first
- Review context of each match
- Inform user of scope
- Consider edge cases (strings, comments)
**Safe Process**
- Search → Find all
- Analyze → Verify appropriate
- Inform → Tell user scope
- Execute → Make changes
- Verify → Confirm applied
- Test → Suggest running tests
**Edge Cases**
- Strings/comments: Ask if should update
- Exported APIs: Warn of breaking changes
- Case sensitivity: Be explicit
## Tool Reference
**Edit with replace_all**
- `replace_all=true`: Replace all occurrences
- `replace_all=false`: Replace only first (or fail if multiple)
- Must match EXACTLY (whitespace, quotes)
**Grep patterns**
- `-n=true`: Show line numbers
- `-B=N, -A=N`: Context lines
- `-i=true`: Case-insensitive
- `type="py"`: Filter by file type
## Integration
- **test-fixing**: Fix broken tests after refactoring
- **code-transfer**: Move refactored code
- **feature-planning**: Plan large refactorings
