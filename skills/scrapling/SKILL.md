---
name: scrapling
description: Undetectable web scraping and data extraction with Cloudflare Turnstile bypass, anti-bot evasion, and self-healing adaptive parsers.
---

# Scrapling — Undetectable Web Scraping for AI Agents

Use Scrapling when fetching web pages that block standard HTTP clients, curl, or standard Playwright instances with Cloudflare, Akamai, Turnstile, or bot detection.

## When to Use

- Target website returns `403 Forbidden`, Cloudflare challenge screens, or CAPTCHAs.
- Scraping JavaScript-heavy dynamic web applications.
- Extracting elements with CSS selectors that change frequently across site redesigns (adaptive self-healing parsing).
- Large multi-page scraping runs requiring concurrent sessions and proxy rotation.

## Available Modalities

### 1. MCP Tools (Native Agent Calling)

The `scrapling` MCP server exposes three tools in `~/.claude.json`:

- `scrapling_scrape(url, stealth=True, max_chars=30000)`: Scrapes any page into clean Markdown. Set `stealth=True` for Cloudflare/anti-bot protected sites.
- `scrapling_css(url, selector, stealth=True, adaptive=True)`: Extracts specific elements matching a CSS selector with self-healing fallback.
- `scrapling_links(url, stealth=True)`: Extracts all hyperlinks from the target page.

### 2. Python Scripting Workflow

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# Standard fast fetch
res = Fetcher.get("https://news.ycombinator.com")
print(res.markdown())

# Undetectable fetch (Cloudflare Turnstile bypass)
stealth_res = StealthyFetcher.fetch("https://protected-site.com", headless=True)
print(stealth_res.css("h1::text").get())

# Adaptive parsing (survives UI/CSS layout updates)
products = stealth_res.css(".product-card", adaptive=True)
```

### 3. Quick CLI Helper

```bash
python3 -c 'from scrapling.fetchers import StealthyFetcher; res = StealthyFetcher.fetch("URL", headless=True); print(res.markdown())'
```
