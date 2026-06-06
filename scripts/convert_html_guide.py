#!/usr/bin/env python3
"""
Convert Google Style Guide HTML files to clean Markdown.
Preserves heading hierarchy, code blocks, and list structure.
Strips XML/HTML tags, inline styles, and navigation cruft.

Usage:
    python scripts/convert_html_guide.py <input.html> <output.md>
    python scripts/convert_html_guide.py <input.html> <output.md> --split-sections
"""

import re
import sys
import html
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def strip_html_simple(content: str) -> str:
    """Fallback converter when BeautifulSoup is not installed."""
    # Preserve code blocks
    content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
                     lambda m: '\n```\n' + html.unescape(m.group(1)) + '\n```\n',
                     content, flags=re.DOTALL)
    content = re.sub(r'<code>(.*?)</code>',
                     lambda m: '`' + html.unescape(m.group(1)) + '`',
                     content)
    # Headings
    for i in range(1, 7):
        content = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>',
                         lambda m, level=i: '\n' + '#' * level + ' ' + html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() + '\n',
                         content, flags=re.DOTALL)
    # Bold / italic
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
    # Lists
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.DOTALL)
    # Links
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content)
    # Paragraphs / divs
    content = re.sub(r'<(p|div|section)[^>]*>', '\n', content)
    content = re.sub(r'</(p|div|section)>', '\n', content)
    # Strip remaining tags
    content = re.sub(r'<[^>]+>', '', content)
    content = html.unescape(content)
    # Normalise blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def node_to_md(node, indent=0) -> str:
    """Recursively convert a BeautifulSoup node to Markdown."""
    if isinstance(node, NavigableString):
        return str(node)

    tag = node.name
    if tag is None:
        return ''

    # Skip script / style / nav
    if tag in ('script', 'style', 'nav', 'head'):
        return ''

    children_text = ''.join(node_to_md(c, indent) for c in node.children)

    if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        level = int(tag[1])
        return f'\n\n{"#" * level} {children_text.strip()}\n\n'

    if tag == 'p':
        return f'\n\n{children_text.strip()}\n\n'

    if tag in ('strong', 'b'):
        return f'**{children_text}**'

    if tag in ('em', 'i'):
        return f'*{children_text}*'

    if tag == 'code':
        inner = children_text.strip()
        if '\n' in inner:
            lang = node.get('class', [''])[0].replace('language-', '') if node.get('class') else ''
            return f'\n```{lang}\n{inner}\n```\n'
        return f'`{inner}`'

    if tag == 'pre':
        # Look for nested code
        code = node.find('code')
        if code:
            lang_classes = code.get('class', [])
            lang = ''
            for c in (lang_classes or []):
                if c.startswith('language-') or c.startswith('lang-'):
                    lang = c.split('-', 1)[1]
                    break
            inner = code.get_text()
            return f'\n```{lang}\n{inner}\n```\n'
        return f'\n```\n{node.get_text()}\n```\n'

    if tag == 'a':
        href = node.get('href', '')
        text = children_text.strip()
        if not text:
            return ''
        if href and not href.startswith('#'):
            return f'[{text}]({href})'
        return text

    if tag in ('ul', 'ol'):
        return f'\n{children_text}\n'

    if tag == 'li':
        prefix = '- '
        lines = children_text.strip().split('\n')
        first = lines[0]
        rest = '\n  '.join(lines[1:])
        return f'\n{prefix}{first}\n  {rest}' if rest.strip() else f'\n{prefix}{first}'

    if tag in ('blockquote',):
        quoted = '\n'.join('> ' + l for l in children_text.strip().split('\n'))
        return f'\n\n{quoted}\n\n'

    if tag == 'hr':
        return '\n\n---\n\n'

    if tag == 'br':
        return '\n'

    if tag in ('table',):
        return f'\n\n{children_text}\n\n'

    if tag == 'tr':
        return f'|{children_text}|\n'

    if tag in ('td', 'th'):
        return f' {children_text.strip()} |'

    # Generic block-level passthrough
    if tag in ('div', 'section', 'article', 'main', 'body', 'html', 'span',
               'sub', 'sup', 'details', 'summary'):
        return children_text

    return children_text


def convert_html_to_md(html_content: str) -> str:
    if not HAS_BS4:
        print("[warn] BeautifulSoup not installed; falling back to regex converter.", file=sys.stderr)
        print("[info] Install with: pip install beautifulsoup4", file=sys.stderr)
        return strip_html_simple(html_content)

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove boilerplate navigation blocks
    for tag in soup.find_all(['nav', 'script', 'style', 'footer']):
        tag.decompose()

    # Try to find the main content container
    main = (soup.find('main') or soup.find(id='content') or
            soup.find(class_='content') or soup.body or soup)

    md = node_to_md(main)

    # Post-process
    md = re.sub(r'\n{3,}', '\n\n', md)
    md = re.sub(r'[ \t]+$', '', md, flags=re.MULTILINE)
    return md.strip()


def split_by_h2(md: str, base_path: Path):
    """Split a Markdown document into per-H2-section files."""
    parts = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    if len(parts) <= 1:
        base_path.write_text(md, encoding='utf-8')
        return

    base_path.parent.mkdir(parents=True, exist_ok=True)
    for i, part in enumerate(parts):
        slug_match = re.match(r'^#{1,2} (.+)', part.strip())
        slug = slug_match.group(1).lower() if slug_match else f'section_{i}'
        slug = re.sub(r'[^\w]+', '_', slug).strip('_')[:60]
        out = base_path.parent / f'{slug}.md'
        out.write_text(part.strip(), encoding='utf-8')
        print(f'  → {out}')


def main():
    if len(sys.argv) < 3:
        print('Usage: convert_html_guide.py <input.html> <output.md> [--split-sections]')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    split = '--split-sections' in sys.argv

    html_content = input_path.read_text(encoding='utf-8', errors='replace')
    md = convert_html_to_md(html_content)

    if split:
        print(f'Splitting {input_path.name} into sections under {output_path.parent}/')
        split_by_h2(md, output_path)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding='utf-8')
        print(f'Written: {output_path} ({len(md):,} chars)')


if __name__ == '__main__':
    main()
