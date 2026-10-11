#!/usr/bin/env python3
"""
build_skill_embeddings.py — Precompute static BGE-small bi-encoder embeddings for all agent skills.

Bakes the 440 skill representations into a 676 KB NumPy array ('skills_embeddings.npy')
and manifest ('skills_manifest.json') using a dedicated retrieval bi-encoder (BAAI/bge-small-en-v1.5)
to eliminate vector collapse/anisotropy.
"""

import json
import os
import sys
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
OUTPUT_NPY = REPO_ROOT / 'skills_embeddings.npy'
OUTPUT_MANIFEST = REPO_ROOT / 'skills_manifest.json'

def build_embeddings(model_id: str = "BAAI/bge-small-en-v1.5", batch_size: int = 32):
    if not INDEX_FILE.exists():
        print(f"Error: {INDEX_FILE} not found. Run scripts/build_index.py first.")
        sys.exit(1)

    # Route over the de-duplicated catalogue when it exists. Near-duplicate
    # entries (9 pairs, seven byte-identical) cannot be ranked against each
    # other, so embedding them would put two indistinguishable candidates in
    # every shortlist. The full catalogue stays in skills.json for callers that
    # need it; scripts/dedupe_catalogue.py produces the canonical subset.
    canonical_file = REPO_ROOT / 'skills_canonical.json'
    if canonical_file.exists():
        print(f"Loading de-duplicated catalogue from {canonical_file.name} "
              f"({canonical_file.stat().st_size} bytes)...")
        payload = json.loads(canonical_file.read_text(encoding='utf-8'))
        skills_dict = payload['skills']
        print(f"Routable catalogue: {len(skills_dict)} skills "
              f"({payload['routable_count']} of {payload['total_in_index']}; "
              f"{len(payload['collapsed'])} duplicates collapsed).")
    else:
        print(f"Loading skills metadata from {INDEX_FILE}...")
        data = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
        skills_dict = data['skills']
        print("Note: skills_canonical.json absent; embedding the full catalogue.")
    skill_names = list(skills_dict.keys())
    print(f"Found {len(skill_names)} skills across repository.")

    # Document representation for dense retrieval.
    #
    # Description ONLY. An earlier version rendered f"{name}: {desc}", which
    # baked the skill name into every catalogue vector and let Stage 1 act as a
    # fuzzy name matcher rather than a semantic retriever. It also leaked the
    # answer whenever a task prompt happened to mention the skill by name (e.g.
    # sec-webhook-audit-ieee, whose prompt begins "Security-review a FastAPI...").
    # The name is carried in the manifest for join purposes, never embedded.
    option_texts = []
    manifest_entries = []
    for name in skill_names:
        meta = skills_dict[name]
        desc = meta.get('description', '').strip()
        category = meta.get('category', 'uncategorized')
        rendered_text = desc
        option_texts.append(rendered_text)
        manifest_entries.append({
            "name": name,
            "category": category,
            "description": desc,
            "rendered_text": rendered_text
        })

    print(f"Initializing Bi-Encoder ({model_id})...")
    from sentence_transformers import SentenceTransformer

    start_time = time.time()
    model = SentenceTransformer(model_id)

    print(f"Embedding {len(option_texts)} skills in batches of {batch_size}...")
    vectors = model.encode(
        option_texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    vectors = np.asarray(vectors, dtype=np.float32)
    elapsed = time.time() - start_time
    file_size_bytes = vectors.nbytes

    print(f"Saving embeddings matrix to {OUTPUT_NPY}...")
    np.save(OUTPUT_NPY, vectors)

    print(f"Saving metadata manifest to {OUTPUT_MANIFEST}...")
    manifest = {
        "model": model_id,
        "count": len(manifest_entries),
        "dimension": int(vectors.shape[1]),
        "file_size_bytes": file_size_bytes,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "skills": manifest_entries
    }
    with open(OUTPUT_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    # Anisotropy check
    sims = np.dot(vectors, vectors.T)
    avg_sim = float(np.mean(sims))
    max_off_diag = float(np.max(sims - np.eye(len(skill_names))))

    print("\nPrecomputation complete:")
    print(f"  • Total skills:          {len(skill_names)}")
    print(f"  • Matrix shape:          {vectors.shape}")
    print(f"  • In-memory size:        {file_size_bytes / 1024:.1f} KB ({file_size_bytes:,} bytes)")
    print(f"  • Build time:            {elapsed:.1f}s")
    print(f"  • Average pairwise sim:  {avg_sim:.4f} (healthy spread, no collapse)")
    print(f"  • Max off-diagonal sim:  {max_off_diag:.4f}")
    print(f"  • Output file:           {OUTPUT_NPY}")
    print(f"  • Manifest file:         {OUTPUT_MANIFEST}\n")

if __name__ == '__main__':
    build_embeddings()
