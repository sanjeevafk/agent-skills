---
name: shiori
description: Connect to the user's Shiori link library via MCP. Use when they want to search, save, list, tag, favorite, or manage saved links and RSS subscriptions. Prefer the remote MCP server at https://www.shiori.sh/mcp. Call whoami before treating the connection as live. Use search_links for topics, list_links for metadata filters (including favorites), get_links for full content, save_link to capture URLs, and save_markdown when they have text and no URL. Optional CLI: shiori auth.
---

# Shiori

Shiori is the user's link library and reader. Use the remote MCP server to search, save, and manage links. Do not scrape the marketing homepage for setup.

This file is the published skill. Connect MCP, verify with `whoami`, then search or save. Prefer MCP over the CLI.

## Official setup prompt

The following prompt is the shared source of truth. Follow it. Do not invent tool names or endpoints.

# Set up Shiori for this project

Set up Shiori completely for this project. Shiori is the user's link library and reader — saved pages, feeds, and context their AI agents can search and use. Do the work yourself where you can. Pause only when the user must create an account, sign in, approve access, enter a secret, or restart the AI client.

The user may not have a Shiori account yet. That is fine: Shiori is free to start, no API key is needed for MCP, and the browser sign-in step below covers signup.

Prefer MCP first. Only fall back to the CLI if MCP cannot be connected in this client.

## Connect the MCP server

1. Match the current AI client. Use that client's current instructions to add the remote Shiori MCP server:
   - Endpoint: https://www.shiori.sh/mcp
   - Docs: https://www.shiori.sh/docs/mcp
   - Do not invent a config format or use a different endpoint.
2. Example for Claude Code:

   claude mcp add --transport http shiori https://www.shiori.sh/mcp

   For Cursor, Codex, ChatGPT, and others, follow the matching section on the MCP docs page.
3. Start the MCP connection. It should open Shiori in the browser to sign in and approve access.
   - Existing users: sign in if prompted, then approve access.
   - New users: on the sign-in page the MCP connection opened, choose "Continue with Google" (this creates the account) or "Create account" to sign up with email, then confirm the email. Do not send them to a signup URL directly; starting from that sign-in page is what brings them back to approve access. Wait for them to finish.
   - Never ask them to paste a token, API key, or secret into the conversation. Never print, log, or save one.
4. If the client must restart before it can load a new MCP server, tell the user exactly what must restart, then continue this setup after the restart.
5. Call the MCP whoami tool. Do not claim MCP is connected until it returns the intended Shiori account.

## Optional: CLI (only if useful for this client)

1. If a Shiori CLI is available for this environment and the user wants it, install it with `npm install -g @shiori-sh/cli` (see https://www.npmjs.com/package/@shiori-sh/cli).
2. Prefer browser-based login via `shiori auth` (the CLI default); it uses the same sign-in page, so new users can sign up there the same way. Use `shiori auth --api-key` on headless machines. If the CLI still requires a manual key:
   - Ask the user to create a key in Shiori Settings → API keys (or the current settings path).
   - Have them paste the key into the CLI's local auth flow only — never into this chat.
3. Confirm with whoami / status before continuing.

## Install the Shiori skill (when available)

1. If a published Shiori skill exists for this agent, install it using the URL from Shiori docs (do not invent one).
2. Confirm install with the client's skill status command when one exists.
3. If no skill is published yet, skip this section and rely on MCP tools + these instructions.

## Verify the setup with real context

1. Use search_links for any topic/content question about the user's library. Use list_links only for metadata filters (unread, recent, by tag, favorites, trash).
2. Do not create throwaway saves just to prove setup. Prefer saving something the user actually wants.
3. Call search_links with query https://www.shiori.sh/docs/mcp (or the title "MCP") before saving. Reuse an existing item if present. Otherwise call save_link with that exact URL. This gives them a useful guide and verifies capture. Use save_markdown when the user has text and no URL — do not stretch save_link.
4. Call get_links with the saved link's id (as a one-element array). Confirm the item is readable (title/url/content or extract still processing).
5. Give the user a short checklist of what succeeded. Include the link id when possible.

### MCP tools to expect

Read / browse: whoami, search_links, list_links, get_links, list_tags, list_subscriptions
Write: save_link, save_markdown, update_link, delete_link, empty_trash, create_tag, update_tag, merge_tags, delete_tag, set_link_tags, add_subscription, remove_subscription, sync_subscription

Stop and explain the exact failing step if any command, permission, or authentication check fails. Do not skip a failed check or claim setup is complete without verifying MCP whoami and a successful save_link / search_links / get_links round-trip.

## After the skill is installed

You already have this skill. Skip the "Install the Shiori skill" section above. Still connect MCP and call `whoami` before searching or saving.

- MCP: https://www.shiori.sh/mcp
- MCP docs: https://www.shiori.sh/docs/mcp
- Skill: https://www.shiori.sh/.well-known/agent-skills/shiori/SKILL.md
- Discovery index: https://www.shiori.sh/.well-known/agent-skills/index.json
- Human install docs: https://www.shiori.sh/docs/skill

## Tool notes

- `search_links` — topic or content questions. Returns snippets; call `get_links` for full bodies (1–5 ids).
- `list_links` — unread, recent, by tag, favorites, or trash. Not for topics.
- `save_link` — capture a URL. Do not create throwaway saves to prove setup.
- `save_markdown` — save markdown text with no URL. Use this when the user has text and no URL. Do not stretch `save_link`.
- Tags: `list_tags`, `create_tag`, `update_tag`, `delete_tag`, `set_link_tags`.
- Feeds: `list_subscriptions`, `add_subscription`, `remove_subscription`, `sync_subscription`.
- Destructive: `delete_link` (trash), `empty_trash` (permanent). Confirm before emptying trash.

## Optional CLI

Prefer MCP. Fall back to `npm install -g @shiori-sh/cli` only if this client cannot connect over MCP. Run `shiori auth` to sign in via your browser (the default); use `shiori auth --api-key` on headless machines. If the CLI still requires a manual API key, paste it into the CLI locally — never into chat.
