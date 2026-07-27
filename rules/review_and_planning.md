# Rule: Review and Planning Mode

- **Trigger:** Whenever the prompt asks to "review", "evaluate", "analyze", "how do we proceed", or includes questionnaire/discussion phrasing.
- **Behavior:**
  1. **Plan & Analyze First:** Enter Senior Engineer Planning Mode. Provide a thorough architectural analysis covering:
     - Expected impacts and system trade-offs.
     - Technical risks and edge cases.
     - Proposed options, architecture diagrams, or artifacts.
  2. **No Unrequested Code Mutations:** Do NOT create, modify, or commit code files during this phase.
  3. **Explicit Authorization Required:** Only proceed to code edits or commits when the user explicitly provides authorization (e.g., typing "proceed", "go ahead", or approving an option).
