---
name: youtube-transcript-summarizer
description: Sub-30s video summarizer downloading official captions and generating structured takeaway bullets.
metadata:
  category: research
  stack: ["youtube-transcript-api", "openai"]
  source_reference: "web-scraping-agents/youtube-summary-agent"
---

# YouTube Fast Transcript Summarizer

## 1. Architectural Pattern & Core Intent

Sub-30s video summarizer downloading official captions and generating structured takeaway bullets.

### Key Characteristics:
- **Primary Domain:** `RESEARCH`
- **Core Technology Stack:** `youtube-transcript-api`, `openai`
- **Upstream Implementation:** [`web-scraping-agents/youtube-summary-agent`](file://web-scraping-agents/youtube-summary-agent)

Author: [Josh Stephens](https://github.com/josh-stephens/youtube-summary-agent) A Live Agent Studio agent that fetches and summarizes YouTube videos. The agent provides rich metadata including view counts, upload dates, top comments, and generates AI-powered summaries using GPT-4. - Supports multiple YouTube URL formats: - Full video URLs - Short video URLs (youtu.be) - Direct video IDs

---

## 2. Prerequisites & Environment Setup

Ensure the target execution environment contains the required dependencies:

```bash
# Core package installation
uv pip install youtube-transcript-api openai
```

### Essential Environment Variables:
```env
# Configure matching credentials based on active provider
OPENAI_API_KEY="your-api-key"
ANTHROPIC_API_KEY="your-api-key"
# Database / Vector store connections if applicable
NEO4J_URI="bolt://localhost:7687"
QDRANT_URL="http://localhost:6333"
```

---

## 3. Standard Execution Workflows

### Primary Invocation Pattern:
Refer to the upstream reference code in `web-scraping-agents/youtube-summary-agent` for concrete implementation templates:

```python
# Minimal execution idiom for youtube-transcript-summarizer
# Inspect web-scraping-agents/youtube-summary-agent for production class definitions
```

---

## 4. Operational Best Practices & Failure Modes

1. **Memory & Concurrency:** When running parallel scrapers or vector ingestions, bind worker concurrency to avoid HTTP 429 rate limits or host memory pressure.
2. **Schema Validation:** Always enforce typed response validation (e.g. via Pydantic models) to prevent unstructured model hallucinations from corrupting graph and vector stores.
3. **Graceful Fallbacks:** Implement retry policies with exponential backoff on network failures and proxy rotations.
