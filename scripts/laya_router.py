#!/usr/bin/env python3
"""
laya_router.py — Two-stage zero-token skill router for agent-skills.

Stage 1: Dedicated bi-encoder (BGE-small) vector dot product against precomputed 660 KB 'skills_embeddings.npy' (<0.1 ms).
Stage 2: Laya cross-encoder evaluation over top-5 candidates (~200 ms CPU / <25 ms GPU).
"""

import json
import sys
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / 'skills.json'
NPY_FILE = REPO_ROOT / 'skills_embeddings.npy'
MANIFEST_FILE = REPO_ROOT / 'skills_manifest.json'

class LayaSkillRouter:
    def __init__(self, bi_encoder_id: str = "BAAI/bge-small-en-v1.5", laya_model_id: str = "convaiinnovations/laya"):
        if not NPY_FILE.exists() or not MANIFEST_FILE.exists():
            raise FileNotFoundError(
                f"Static cache missing ({NPY_FILE.name}). Run scripts/build_skill_embeddings.py first."
            )

        # 1. Load static vector index (<2 ms)
        t0 = time.perf_counter()
        self.vectors = np.load(NPY_FILE)  # shape (440, 384), float32, normalized
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        self.skills = self.manifest['skills']
        self.load_index_ms = (time.perf_counter() - t0) * 1000

        # Validate cache model compatibility
        cached_model = self.manifest.get("model")
        if cached_model and cached_model != bi_encoder_id:
            print(f"Warning: Cached model '{cached_model}' differs from '{bi_encoder_id}'. Run scripts/build_skill_embeddings.py to re-sync.", file=sys.stderr)

        # 2. Initialize Stage 1 Bi-Encoder (explicitly on CPU)
        try:
            from sentence_transformers import SentenceTransformer
            self.bi_encoder = SentenceTransformer(bi_encoder_id, device="cpu")
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required for Stage 1 dense retrieval. Install with: pip install sentence-transformers"
            ) from e

        # 3. Initialize Stage 2 Laya Agent
        try:
            from laya import Agent
            self.agent = Agent(laya_model_id)
        except ImportError as e:
            raise ImportError(
                "laya is required for Stage 2 cross-encoder routing. Install with: pip install laya"
            ) from e

    def route(self, query: str, top_k: int = 5):
        stats = {}

        # Step 1: Embed single query string with BGE retrieval instruction
        t_embed_start = time.perf_counter()
        bge_query = f"Represent this sentence for searching relevant passages: {query}"
        q_vec = self.bi_encoder.encode([bge_query], normalize_embeddings=True)
        q_vec = np.asarray(q_vec, dtype=np.float32).reshape(1, -1)
        stats['query_embed_ms'] = (time.perf_counter() - t_embed_start) * 1000

        # Step 2: Dot product against all 440 candidates
        t_dot_start = time.perf_counter()
        sims = np.dot(self.vectors, q_vec.T).ravel()  # shape (440,)
        top_indices = np.argsort(-sims)[:top_k]
        stats['shortlist_dot_ms'] = (time.perf_counter() - t_dot_start) * 1000

        # Collect top-k candidate descriptions
        shortlisted = [self.skills[i] for i in top_indices]
        candidate_criteria = {
            s['name']: s['description'] for s in shortlisted
        }

        # Step 3: Laya cross-encoder final decision over top-5 candidates
        t_predict_start = time.perf_counter()
        questions = {
            "selected_skill": {
                "type": "choice",
                "instructions": "Select the single most applicable engineering skill for the given task.",
                "criteria": candidate_criteria
            }
        }
        res = self.agent.predict(query, questions)
        stats['laya_predict_ms'] = (time.perf_counter() - t_predict_start) * 1000

        answer = res['answers']['selected_skill']
        selected_name = answer['choice']
        confidence = answer.get('confidence', 0.0)

        return {
            "query": query,
            "selected_skill": selected_name,
            "confidence": confidence,
            "shortlisted_top_k": [
                {"name": s['name'], "score": float(sims[top_indices[idx]]), "category": s['category']}
                for idx, s in enumerate(shortlisted)
            ],
            "stats": stats
        }

def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How do I secure Django REST framework API endpoints against CSRF and injection?"
    print(f"\nInitializing LayaSkillRouter (BGE-small + Laya)...")
    router = LayaSkillRouter()
    print(f"Vector cache loaded in {router.load_index_ms:.2f} ms ({router.vectors.shape[0]} skills)\n")

    print(f"Routing query: \"{query}\"")
    result = router.route(query, top_k=5)

    print("\n" + "="*70)
    print(f"RECOMMENDED SKILL:  {result['selected_skill']}")
    print(f"CONFIDENCE:         {result['confidence']:.3f}")
    print("="*70)

    print("\nShortlisted Top-5 Candidates (Stage 1 BGE Cosine):")
    for idx, cand in enumerate(result['shortlisted_top_k'], 1):
        indicator = " ★ SELECTED" if cand['name'] == result['selected_skill'] else ""
        print(f"  {idx}. {cand['name']:<30} [{cand['category']:<9}] (cosine: {cand['score']:.4f}){indicator}")

    s = result['stats']
    print("\nLatency Profiling:")
    print(f"  • Stage 1 Query Embedding:     {s['query_embed_ms']:>6.2f} ms")
    print(f"  • Stage 1 Vector Dot Product:   {s['shortlist_dot_ms']:>6.2f} ms (across 440 skills)")
    print(f"  • Stage 2 Laya Cross-Encoder:   {s['laya_predict_ms']:>6.2f} ms (5 candidates)")
    total_ms = s['query_embed_ms'] + s['shortlist_dot_ms'] + s['laya_predict_ms']
    print(f"  • Total Pipeline Latency:       {total_ms:>6.2f} ms\n")

if __name__ == '__main__':
    main()
