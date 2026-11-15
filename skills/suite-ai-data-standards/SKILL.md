---
name: suite-ai-data-standards
description: >-
  Distilled engineering standards for AI/ML pipelines (model pinning, vLLM/TRL, RAG sanitization),
  Data Science & SQL (Polars >100k rows, parameterized queries, index/migration validation), and
  Google/NASA JPL defensive Python rules.
---

# AI, Data & Engineering Standards

## Machine Learning & AI
- Always pin model checkpoints and record evaluation metrics before deployment.
- Prefer batch inference and vLLM/TRL optimizations for LLM workloads.
- Guard against prompt injection and sanitize inputs in RAG pipelines.

## Data Science & Databases
- Prefer Polars over Pandas for tabular performance with >100k rows.
- Write parameterized SQL queries; never concatenate user input into queries.
- Validate schema migrations and index performance before production commits.

## Google Standards & Mission-Critical Python
- Follow language-specific Google Style Guides (naming, formatting, type hints, docstrings).
- Enforce clarity, small focused changes, and thorough code reviews.
- For mission-critical Python, follow NASA JPL defensive rules: bounded loops, assertions, minimal state.
