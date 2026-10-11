#!/usr/bin/env python3
"""Shared helpers for skill tooling (single source of truth for frontmatter)."""

from __future__ import annotations


import yaml


def strip_frontmatter(content: str) -> tuple[dict, str, str | None]:
    """Extract YAML frontmatter, returning (meta, body, error).

    Error is None on success. Missing opening/closing fences and
    non-mapping YAML are errors; callers that need lenient behaviour
    can ignore the error and use the returned meta/body.
    """
    meta: dict = {}
    if not content.startswith("---"):
        return meta, content, "Front matter must start on the first line with ---"
    end = content.find("\n---", 3)
    if end == -1:
        return meta, content, "Front matter is missing closing ---"
    frontmatter_raw = content[3:end]
    body = content[end + 4 :].lstrip("\n")
    try:
        parsed = yaml.safe_load(frontmatter_raw)
        if parsed is None:
            return {}, body, None
        if not isinstance(parsed, dict):
            return meta, body, "Front matter must be a YAML mapping"
        return parsed, body, None
    except Exception as e:
        return meta, body, f"YAML Syntax Error: {e}"


def strip_frontmatter_lenient(content: str) -> tuple[dict, str]:
    """Lenient variant returning (meta, body), ignoring errors."""
    meta, body, _ = strip_frontmatter(content)
    return meta, body
