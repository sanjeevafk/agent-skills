---
name: scrapling
description: Undetectable web scraping and data extraction with Cloudflare Turnstile bypass, anti-bot evasion, and self-healing adaptive parsers.
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

### 1. MCP Tools (Native Agent Calling)
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
