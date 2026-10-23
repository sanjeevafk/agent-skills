---
name: deep-research
description: Multi-source deep research using firecrawl and exa MCPs. Searches the web, synthesizes findings, and delivers cited reports with source attribution. Use when the user wants thorough research on any topic with evidence and citations.
metadata:
  origin: ECC
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## MCP Requirements
- **firecrawl** — `firecrawl_search`, `firecrawl_scrape`, `firecrawl_crawl`
- **exa** — `web_search_exa`, `web_search_advanced_exa`, `crawling_exa`
### Step 2: Plan the Research
- Topic: "Impact of AI on healthcare"
- What are the main AI applications in healthcare today?
- What clinical outcomes have been measured?
- What are the regulatory challenges?
- What companies are leading this space?
- What's the market size and growth trajectory?
### Step 3: Execute Multi-Source Search
**With firecrawl**
```
firecrawl_search(query: "<sub-question keywords>", limit: 8)
```

**With exa**
```
web_search_exa(query: "<sub-question keywords>", numResults: 8)
web_search_advanced_exa(query: "<keywords>", numResults: 5, startPublishedDate: "2025-01-01")
```

**Search strategy**
- Use 2-3 different keyword variations per sub-question
- Mix general and news-focused queries
- Aim for 15-30 unique sources total
- Prioritize: academic, official, reputable news > blogs > forums
### Step 4: Deep-Read Key Sources
```
firecrawl_scrape(url: "<url>")
```

```
crawling_exa(url: "<url>", tokensNum: 5000)
```

### Step 5: Synthesize and Write Report
```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*
## Executive Summary
[3-5 sentence overview of key findings]
## 1. [First Major Theme]
[Findings with inline citations]
- Key point ([Source Name](url))
- Supporting data ([Source Name](url))
## 2. [Second Major Theme]
...
## 3. [Third Major Theme]
  # ... [syntax pattern continues] ...
Searched [N] queries across web and news. Analyzed [M] sources.
Sub-questions investigated: [list]
```

### Step 6: Deliver
- **Short topics**: Post the full report in chat
- **Long reports**: Post the executive summary + key takeaways, save full report to a file
## Parallel Research with Subagents
```
Launch 3 research agents in parallel:
1. Agent 1: Research sub-questions 1-2
2. Agent 2: Research sub-questions 3-4
3. Agent 3: Research sub-question 5 + cross-cutting themes
```

## Quality Rules
- **Every claim needs a source.** No unsourced assertions.
- **Cross-reference.** If only one source says it, flag it as unverified.
- **Recency matters.** Prefer sources from the last 12 months.
- **Acknowledge gaps.** If you couldn't find good info on a sub-question, say so.
- **No hallucination.** If you don't know, say "insufficient data found."
- **Separate fact from inference.** Label estimates, projections, and opinions clearly.
## Examples
```
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services in 2026"
"Research the best strategies for bootstrapping a SaaS business"
"What's happening with the US housing market right now?"
"Investigate the competitive landscape for AI code editors"
```
