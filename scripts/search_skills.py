#!/usr/bin/env python3
"""
search_skills.py — High-precision weighted BM25 search engine for skills and capabilities.
Implements token-normalized BM25 retrieval (k1=1.2, b=0.75) with field weighting.
"""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
COMMANDS_DIR = REPO_ROOT / 'commands'


def tokenize_normalized(text: str) -> List[str]:
    """
    Normalize text: splits camelCase, snake_case, and kebab-case.
    Returns cleaned alphanumeric tokens (len >= 2).
    """
    if not text:
        return []
    # Split camelCase (e.g. dockerCompose -> docker Compose)
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    # Split snake_case and kebab-case
    text = text.replace('_', ' ').replace('-', ' ').replace('/', ' ')
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return [t for t in tokens if len(t) > 1]


class WeightedBM25:
    """
    Weighted Okapi BM25 implementation with document length normalization.
    Field Weights: Name=3.0, Tags=2.0, Description=1.0, Category=1.0.
    """
    def __init__(self, skills: Dict[str, Dict[str, Any]], k1: float = 1.2, b: float = 0.75):
        self.skills = skills
        self.k1 = k1
        self.b = b
        self.N = len(skills)
        self.corpus: Dict[str, Counter] = {}
        self.doc_lengths: Dict[str, float] = {}
        self.df: Counter = Counter()

        total_dl = 0.0
        for name, meta in skills.items():
            name_tokens = tokenize_normalized(name)
            tag_tokens = tokenize_normalized(" ".join(meta.get("tags", [])))
            desc_tokens = tokenize_normalized(meta.get("description", ""))
            cat_tokens = tokenize_normalized(meta.get("category", "") + " " + meta.get("category_label", ""))

            tf = Counter()
            for t in name_tokens:
                tf[t] += 3.0
            for t in tag_tokens:
                tf[t] += 2.0
            for t in desc_tokens:
                tf[t] += 1.0
            for t in cat_tokens:
                tf[t] += 1.0

            dl = len(name_tokens) * 3.0 + len(tag_tokens) * 2.0 + len(desc_tokens) * 1.0 + len(cat_tokens) * 1.0
            self.corpus[name] = tf
            self.doc_lengths[name] = dl
            total_dl += dl

            for term in tf:
                self.df[term] += 1

        self.avg_dl = (total_dl / max(self.N, 1)) if self.N > 0 else 1.0

    def query(self, query_str: str, top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
        q_tokens = tokenize_normalized(query_str)
        if not q_tokens:
            return []

        scores: Dict[str, float] = {}
        for qt in q_tokens:
            if qt not in self.df:
                continue
            n_q = self.df[qt]
            # Standard smoothed Robertson-Spärck Jones IDF
            idf = math.log(1.0 + (self.N - n_q + 0.5) / (n_q + 0.5))

            for doc_name, tf in self.corpus.items():
                f = tf.get(qt, 0.0)
                if f <= 0:
                    continue
                dl = self.doc_lengths[doc_name]
                # BM25 term saturation & document length normalization
                numerator = f * (self.k1 + 1.0)
                denominator = f + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_dl))
                term_score = idf * (numerator / denominator)

                scores[doc_name] = scores.get(doc_name, 0.0) + term_score

        # Exact match bonus on skill name
        q_lower = query_str.lower().strip()
        for doc_name in scores:
            if doc_name.lower() == q_lower:
                scores[doc_name] += 15.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for name, score in ranked[:top_k]:
            results.append((round(score, 2), self.skills[name]))
        return results


_INDEX_CACHE: Dict[str, WeightedBM25] = {}


def get_bm25_index() -> WeightedBM25:
    global _INDEX_CACHE
    if "index" in _INDEX_CACHE:
        return _INDEX_CACHE["index"]

    if not INDEX_FILE.exists():
        print(f"skills.json not found at {INDEX_FILE}. Run build_index.py first.", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skills = data.get('skills', {})
    index = WeightedBM25(skills)
    _INDEX_CACHE["index"] = index
    return index


def search(query: str, top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
    index = get_bm25_index()
    return index.query(query, top_k=top_k)


def generate_find_command():
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    find_cmd_file = COMMANDS_DIR / 'find.md'
    content = """<!-- AUTO-GENERATED SEARCH WRAPPER — DO NOT EDIT MANUALLY -->
---
description: "Search and discover skills by intent, tags, language, or framework"
namespace: "/find"
flat_command: "/find"
---

# Command: /find <keyword>

> **Usage**: Type `/find <keyword>` (e.g. `/find nextjs`, `/find debugging`, `/find security`) to search the 550+ registered skills and rules.

---

*(Executed via `python3 scripts/search_skills.py <query>` using weighted BM25.)*
"""
    find_cmd_file.write_text(content, encoding='utf-8')


def main():
    generate_find_command()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n🔍 Search results for '{query}' (Weighted BM25):\n")
        results = search(query)
        if not results:
            print("No matching skills found.")
            return
        for score, meta in results:
            cmd = meta.get('namespace_command', meta.get('name', ''))
            print(f"  • {meta['name']:<35} (Score: {score:>6.2f}) [{cmd}]")
            desc = meta.get('description', '')
            print(f"    {desc[:90]}...")
            print()
    else:
        print("Usage: python3 scripts/search_skills.py <query>")


if __name__ == '__main__':
    main()
