---
name: agent-reach
description: >
  MUST USE when user wants to research/search/look up/find anything on the
  internet — e.g. "research this topic", "do a deep dive on X", "search the
  web for X", "see what people say about X", "look this up".

  Also MUST USE when user mentions any platform or shares any URL/link:
  Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili, XiaoHongShu,
  Xiaoyuzhou Podcast, LinkedIn/jobs/recruiting, V2EX, Xueqiu (stocks), RSS.

  15 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: writing reports/analysis/translation (this skill only FETCHES
  internet content); posting/commenting/liking (write operations); platforms
  that already have a dedicated skill installed (prefer that skill).
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Standing rules (apply for the whole session)
- **Health-check before acting**: for multi-backend/login-backed platforms (XiaoHongShu /
- **Announce what you use**: say "using agent-reach, platform X via backend Y"
- **On failure, follow the retry chains in references/** — never guess
- **For broad research tasks**: combine platforms (Exa for web search +
- **Watch versions for the user**: after finishing a substantial
## Routing table
| User intent | Category | Details |
|---------|------|---------|
| Web / code search | search | [references/search.md](references/search.md) |
| XiaoHongShu / Twitter / Bilibili / V2EX / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| Jobs / LinkedIn | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| Web pages / articles / RSS | web | [references/web.md](references/web.md) |
| YouTube / Bilibili / podcast transcripts | video | [references/video.md](references/video.md) |
| Xueqiu / stock quotes | finance | [references/finance.md](references/finance.md) |
## Zero-config quick commands
```bash
# Exa web search
mcporter call exa.web_search_exa query="query" numResults=5
# Read any web page
curl -s "https://r.jina.ai/URL"
# GitHub search
gh search repos "query" --sort stars --limit 10
# YouTube subtitles (never use yt-dlp for Bilibili; retry chain in video.md)
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
# Bilibili search (bili-cli, no login needed)
bili search "query" --type video -n 5
```

## Login-backed platforms (pick by doctor's active_backend)
```bash
# Twitter search (twitter-cli preferred; retry chain in social.md)
twitter search "query" -n 10
# Reddit (NO zero-config path — OpenCLI or rdt-cli, login required)
opencli reddit search "query" -f yaml   # desktop
rdt search "query" --limit 10            # legacy/server
# XiaoHongShu (desktop prefers OpenCLI)
opencli xiaohongshu search "query" -f yaml
# Facebook / Instagram (desktop OpenCLI, browser session)
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # user search
opencli instagram user USERNAME -f yaml        # recent posts from one user
```

## Environment check
```bash
# Channel availability + which backend serves each platform
agent-reach doctor --json
```

## Workspace rules
**Never create files in the agent workspace.:** Use `/tmp/` for temporary
## Detailed references
- [Search](references/search.md) — Exa AI search
- [Social](references/social.md) — XiaoHongShu, Twitter, Bilibili, V2EX, Reddit, Facebook, Instagram (multi-backend/login-backed groups)
- [Career](references/career.md) — LinkedIn
- [Dev](references/dev.md) — GitHub CLI
- [Web](references/web.md) — Jina Reader, RSS
- [Video](references/video.md) — YouTube, Bilibili, Xiaoyuzhou
- [Finance](references/finance.md) — Xueqiu quotes, search and market content
