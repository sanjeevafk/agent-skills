---
name: suite-design-office-writing
description: >-
  Distilled rules for technical diagrams (4/10 density, orthogonal connectors, 1-2 accent colors),
  Office documents (python-pptx, openpyxl, 16/24/32pt scales), technical writing, and cognitive modes.
---

# Design, Office Documents & Technical Writing

## Diagrams & Visual Design
- Keep diagram density to ~4/10; avoid visual noise.
- Use orthogonal right-angle elbows for connectors; never slant diagonal lines.
- Restrict focal accent color to at most 1–2 key elements per diagram.

## Office Documents (Slides & Spreadsheets)
- Prefer `python-pptx` for presentations and `openpyxl` for spreadsheets.
- Run layout, text-fitting, and visual collision audits before saving files.
- Preserve typography scales: 16pt body, 24pt headers, 32pt slide titles.

## Technical Writing & Cognitive Modes
- Lead with the bottom line in the first sentence; use plain, direct English, active voice, and zero corporate jargon.
- Use scannable blocks: bold lead-ins, short paragraphs, strict structure.
- Adapt communication density to requested mode without ever sacrificing technical correctness or critical warnings; ground challenge modes in evidence, tradeoffs, and edge cases.
