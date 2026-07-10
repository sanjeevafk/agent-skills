#!/usr/bin/env python3
"""
validate_skills.py — Validate YAML frontmatter in all SKILL.md files.
Checks for required fields (name, description) and name uniqueness.
"""

import sys
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

def strip_frontmatter(content: str) -> tuple[dict, str, str | None]:
    """Extract YAML frontmatter and return (meta dict, body content, error_msg)."""
    meta: dict = {}
    if not content.startswith('---'):
        return meta, content, "Front matter must start on the first line with ---"
    
    end = content.find('\n---', 3)
    if end == -1:
        return meta, content, "Front matter is missing closing ---"
        
    frontmatter_raw = content[3:end]
    body = content[end + 4:].lstrip('\n')

    if _HAS_YAML:
        try:
            parsed = yaml.safe_load(frontmatter_raw)
            if not isinstance(parsed, dict):
                return meta, body, "Front matter must be a YAML mapping"
            meta = parsed
        except Exception as e:
            return meta, body, f"YAML Syntax Error: {e}"
    else:
        # Fallback: simple line parser
        for line in frontmatter_raw.splitlines():
            if ':' in line and not line.startswith(' '):
                key, _, val = line.partition(':')
                meta[key.strip()] = val.strip()

    return meta, body, None

def main():
    repo_root = Path(__file__).parent.parent.resolve()
    
    # Locate all SKILL.md files under search directories
    search_dirs = [
        repo_root / 'skills'
    ]
    
    skill_mds = []
    for sdir in search_dirs:
        if sdir.exists():
            skill_mds.extend(sdir.rglob("SKILL.md"))
            
    # Sort files by path for deterministic validation order
    skill_mds = sorted(list(set(skill_mds)))
    
    if not skill_mds:
        print("No SKILL.md files found.", file=sys.stderr)
        sys.exit(0)
        
    errors = []
    seen_names = {}
    
    for path in skill_mds:
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            errors.append((path, f"Failed to read file: {e}"))
            continue
            
        meta, body, err = strip_frontmatter(content)
        if err:
            errors.append((path, err))
            continue
            
        # Check required fields
        for field in ['name', 'description']:
            val = meta.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append((path, f"Missing or empty non-string field: {field}"))
                
        skill_name = str(meta.get('name') or "").strip()
        if skill_name:
            rel_path = path.relative_to(repo_root)
            if skill_name in seen_names:
                errors.append((
                    path, 
                    f"Duplicate skill name '{skill_name}' also used by {seen_names[skill_name]}"
                ))
            else:
                seen_names[skill_name] = rel_path
                
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for path, err in errors:
            try:
                rel = path.relative_to(repo_root)
            except ValueError:
                rel = path
            print(f"  - {rel}: {err}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Validated {len(skill_mds)} skill(s) successfully.")
    sys.exit(0)

if __name__ == '__main__':
    main()
