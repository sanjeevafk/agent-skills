#!/usr/bin/env python3
"""
julia_router.py — Two-stage zero-token skill router for agent-skills.

Stage 1: bi-encoder (BAAI/bge-small-en-v1.5) vector dot product against the
         precomputed `skills_embeddings.npy` (~795 KB for 530 skills).
Stage 2: SupersonicLabs/Julia-1 (144.3M non-generative decision model) makes a
         calibrated single choice over the top-k shortlist.

Why Julia-1 replaced Laya as the Stage 2 decision head
------------------------------------------------------
The previous Stage 2 named `NandhaKishorM/laya` in the manuscript while the code
defaulted to `convaiinnovations/laya`, and neither Python package was importable
from the project environment — so the reported Stage 2 latency and accuracy could
not be reproduced by anyone, including the original authors. Julia-1 (Apache 2.0)
loads and runs on CPU from the local machine, is pinned to a transformers range
that is installable, and answers the same question shape (2-20 options, one
calibrated decision) as Laya. Swapping it in replaces a claimed-but-unverifiable
component with one that executes locally.

Measurement hygiene
-------------------
* Catalogue vectors embed **descriptions only**. An earlier build rendered
  "name: description", which let Stage 1 act as a name matcher and leaked the
  answer for any task prompt that mentioned the skill by name.
* The router refuses to run against a stale cache: the vector count, manifest
  count and index count must agree, otherwise a phantom catalogue is silently
  searched.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).parent.parent.resolve()
INDEX_FILE = REPO_ROOT / "skills.json"
NPY_FILE = REPO_ROOT / "skills_embeddings.npy"
MANIFEST_FILE = REPO_ROOT / "skills_manifest.json"

BI_ENCODER_ID = "BAAI/bge-small-en-v1.5"

# Julia-1 accepts 2-20 options natively; keep the shortlist inside that bound.
JULIA_MIN_OPTIONS = 2
JULIA_MAX_OPTIONS = 20

# Julia-1 rejects any option longer than 48 model tokens under
# strict_encoding. Word count approximates that closely enough for English
# skill descriptions and is verified by the runtime at call time.
MAX_OPTION_WORDS = 40


def find_julia_model_path() -> str:
    """Locate a local Julia-1 snapshot.

    The runtime's ``load_model`` takes a directory path, not a Hub id, so the
    snapshot must already be present. Resolve it from the HF cache, then from a
    couple of conventional local locations.
    """
    candidates: list[Path] = []

    hf_home = Path.home() / ".cache" / "huggingface" / "hub"
    snapshots = hf_home / "models--SupersonicLabs--Julia-1" / "snapshots"
    if snapshots.is_dir():
        for snap in sorted(snapshots.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if (snap / "model.safetensors").exists():
                candidates.append(snap)

    candidates.append(REPO_ROOT / "Julia-1")
    candidates.append(Path.home() / "Julia-1")

    for path in candidates:
        if (path / "model.safetensors").exists():
            return str(path)

    raise FileNotFoundError(
        "Julia-1 weights not found. Download them with:\n"
        "  uv run python -c \"from huggingface_hub import snapshot_download; "
        "snapshot_download('SupersonicLabs/Julia-1', local_dir='Julia-1')\""
    )


class JuliaSkillRouter:
    """Two-stage router: dense shortlist, then a Julia-1 decision over the shortlist."""

    def __init__(
        self,
        bi_encoder_id: str = BI_ENCODER_ID,
        julia_model_path: str | None = None,
        device: str = "cpu",
        strict_encoding: bool = True,
        max_length: int = 8192,
        head_length: int = 512,
        max_option_words: int = MAX_OPTION_WORDS,
    ):
        for f in (NPY_FILE, MANIFEST_FILE, INDEX_FILE):
            if not f.exists():
                raise FileNotFoundError(
                    f"Static cache missing ({f.name}). Run scripts/build_index.py "
                    "then scripts/build_skill_embeddings.py first."
                )

        t0 = time.perf_counter()
        self.vectors = np.load(NPY_FILE)
        self.manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        self.index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        self.skills = self.manifest["skills"]
        self.load_index_ms = (time.perf_counter() - t0) * 1000

        # Stale-cache guard. The original router validated only the model string
        # and happily searched a 440-entry index while skills.json held 413
        # entries, so 53 catalogue skills were unreachable and ~100 phantom ones
        # were reachable. Any disagreement is now a hard error.
        n_vec, n_manifest, n_index = self.vectors.shape[0], len(self.skills), len(self.index["skills"])
        if not n_vec == n_manifest == n_index:
            raise RuntimeError(
                "stale embedding cache: "
                f"{n_vec} vectors != {n_manifest} manifest entries != {n_index} indexed skills. "
                "Run scripts/build_skill_embeddings.py to rebuild from skills.json."
            )
        self.n_skills = n_vec

        cached_model = self.manifest.get("model")
        if cached_model and cached_model != bi_encoder_id:
            print(
                f"Warning: cached bi-encoder '{cached_model}' != '{bi_encoder_id}'. "
                "Rebuild embeddings.",
                file=sys.stderr,
            )

        # De-leak check: documents must not embed the skill name.
        self._assert_no_name_leak()

        try:
            from sentence_transformers import SentenceTransformer

            self.bi_encoder = SentenceTransformer(bi_encoder_id, device="cpu")
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "sentence-transformers is required for Stage 1. "
                "Install with: uv pip install sentence-transformers"
            ) from exc

        from julia import load_model

        self.max_option_words = max_option_words
        self.julia_path = julia_model_path or find_julia_model_path()
        t0 = time.perf_counter()
        self.julia = load_model(
            self.julia_path,
            device=device,
            strict_encoding=strict_encoding,
            max_length=max_length,
            head_length=head_length,
        )
        self.julia_load_ms = (time.perf_counter() - t0) * 1000

    def _assert_no_name_leak(self) -> None:
        """Fail if the build embedded the 'name: description' prefix.

        The earlier leaky build rendered f"{name}: {desc}", which made Stage 1 a
        name matcher and leaked the answer for prompts that mention the skill by
        name. A legitimate description can of course contain the same words
        ('agent-development' describes agent development), so matching on a bare
        substring is wrong. The reliable signature is that the document *starts*
        with the exact skill name followed by a colon.
        """
        offenders = [
            entry["name"]
            for entry in self.skills
            if entry.get("rendered_text", "").startswith(entry["name"] + ":")
        ]
        if offenders:
            raise RuntimeError(
                "embedded documents use the leaky 'name: description' rendering: "
                f"{offenders[:5]}. Rebuild embeddings with description-only rendering "
                "(scripts/build_skill_embeddings.py)."
            )

    def _decide(self, query: str, options: list[str]) -> dict:
        """One Julia-1 decision over `options`."""
        return self.julia.predict([
            {
                "state": query,
                "question": "Which engineering skill should handle this task?",
                "options": options,
                "type": "choice",
            }
        ])[0]

    def _fit_option_budget(self, criteria: list[str]) -> tuple[list[str], int]:
        """Clip options until Julia-1 accepts them.

        Deterministic: the same shortlist always yields the same clip, because
        the candidate word caps are a fixed descending ladder and the first
        accepted one is returned.
        """
        ladder = [self.max_option_words, 32, 24, 18, 12, 8]
        for cap in ladder:
            clipped = [" ".join(c.split()[:cap]) for c in criteria]
            try:
                self._decide("budget probe", clipped)
                return clipped, cap
            except ValueError:
                continue
        # Last resort: single-word options are always within any budget.
        clipped = [" ".join(c.split()[:1]) or c for c in criteria]
        return clipped, 1

    def route(self, query: str, top_k: int = 5) -> dict:
        if not (JULIA_MIN_OPTIONS <= top_k <= JULIA_MAX_OPTIONS):
            raise ValueError(
                f"top_k must be {JULIA_MIN_OPTIONS}..{JULIA_MAX_OPTIONS} "
                f"(Julia-1 native option bound), got {top_k}"
            )

        # Stage 1 — embed the query with the BGE retrieval instruction.
        t0 = time.perf_counter()
        q_vec = self.bi_encoder.encode(
            [f"Represent this sentence for searching relevant passages: {query}"],
            normalize_embeddings=True,
        )
        q_vec = np.asarray(q_vec, dtype=np.float32).reshape(1, -1)
        embed_ms = (time.perf_counter() - t0) * 1000

        # Stage 1 — single matrix dot product over the whole catalogue.
        t0 = time.perf_counter()
        sims = np.dot(self.vectors, q_vec.T).ravel()
        order = np.argsort(-sims)
        top_indices = order[:top_k]
        dot_ms = (time.perf_counter() - t0) * 1000

        shortlist = [self.skills[i] for i in top_indices]
        criteria = [s["description"] or s["name"] for s in shortlist]

        # Julia-1 enforces a 48-token limit per option under strict_encoding.
        # Skill descriptions routinely exceed it (corpus max is ~124 words), and
        # the relationship between word count and model tokens is too variable
        # for a fixed word cap to be reliable: at 24 words a residual 10 of 530
        # descriptions still overflow. So we degrade deterministically --
        # try progressively tighter clips until the runtime accepts -- rather
        # than guessing a bound up front.
        criteria, clip_words = self._fit_option_budget(criteria)

        # Stage 2 — Julia-1 picks one candidate and reports calibrated confidence.
        t0 = time.perf_counter()
        result = self._decide(query, criteria)
        decide_ms = (time.perf_counter() - t0) * 1000

        index = int(result["index"])
        probs = [float(p) for p in result["probabilities"]]
        chosen = shortlist[index]

        return {
            "query": query,
            "selected_skill": chosen["name"],
            "confidence": probs[index] if index < len(probs) else 0.0,
            "shortlisted": [
                {
                    "name": s["name"],
                    "stage1_cosine": float(sims[i]),
                    "stage2_probability": probs[j] if j < len(probs) else 0.0,
                    "category": s["category"],
                }
                for j, (s, i) in enumerate(zip(shortlist, top_indices))
            ],
            "stats": {
                "query_embed_ms": embed_ms,
                "shortlist_dot_ms": dot_ms,
                "julia_decide_ms": decide_ms,
                "option_clip_words": clip_words,
                "total_ms": embed_ms + dot_ms + decide_ms,
                "n_skills": self.n_skills,
            },
        }


def main() -> None:
    query = " ".join(sys.argv[1:]) or (
        "How do I secure Django REST framework endpoints against CSRF and injection?"
    )
    router = JuliaSkillRouter()
    print(f"catalogue: {router.n_skills} skills | vectors+manifest+index agree")
    print(f"index load: {router.load_index_ms:.2f} ms | julia load: {router.julia_load_ms:.0f} ms")
    print(f"\nquery: {query}\n")

    res = router.route(query, top_k=5)
    print(f"SELECTED: {res['selected_skill']}  (confidence {res['confidence']:.3f})\n")
    print("shortlist:")
    for cand in res["shortlisted"]:
        mark = " <- selected" if cand["name"] == res["selected_skill"] else ""
        print(
            f"  {cand['name']:<34} cos={cand['stage1_cosine']:.4f} "
            f"p={cand['stage2_probability']:.3f}{mark}"
        )

    s = res["stats"]
    print(f"\nlatency: embed {s['query_embed_ms']:.1f} ms | "
          f"dot {s['shortlist_dot_ms']:.2f} ms | "
          f"julia {s['julia_decide_ms']:.1f} ms | "
          f"total {s['total_ms']:.1f} ms")


if __name__ == "__main__":
    main()