---
name: suite-product-qa-security
description: >-
  Distilled checklists for Product Architecture (ADRs, PRDs), Orchestration & Agent Harness,
  QA/Code Quality/Security, Web Research, Social/Messaging APIs, and Swift 6/SwiftUI.
---

# Product, Orchestration, QA, Security & Domain Checklists

## Product, Orchestration & Agent Harness
- Document architectural trade-offs, context, and alternatives in ADRs; break PRDs into user stories with acceptance criteria.
- Enforce delivery gates, RFC/intent-driven specs, bounded execution (stop conditions, timeouts), and clean context handoffs grounded in file/shell evidence.
- Test MCP servers and CLI tools in isolation before integrating; follow standard skill YAML frontmatter + actionable constraints.

## Code Quality, QA & Security
- Review for intent, maintainability, and domain boundaries; require automated tests & type-safety verification.
- Reproduce issues first, follow red-green-refactor TDD, and verify all fixes with automated tests.
- Enforce strict auth, session timeouts, and rate limits; check dependencies for CVEs/unpinned scripts; never store secrets in code or Git history.

## Web Research, Social APIs & Apple/Swift
- Web research: search-first retrieval, headless crawlers (`Scrapling`, `Ottomator`, `Exa`) with rate limiting & markdown parsing, cross-verify facts with source URLs.
- Social/messaging: rate-limit compliance with exponential backoff retries, sanitize inputs/webhooks, never log/commit tokens.
- Swift/Apple: Swift 6 concurrency (`actors`, `Sendable`), protocol-oriented DI, idiomatic SwiftUI state/view hierarchies.
