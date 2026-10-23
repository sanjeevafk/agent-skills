# Manuscripts & Publication Artifacts

This directory houses the paper manuscripts, build tooling, figures, and reference literature for the empirical evaluation of agent skill delivery formats.

---

## 1. Active Manuscript: V2 (SANER 2027 RENE Track)
Targeting the **SANER 2027 Research, Evaluation, and Negative Results (RENE)** track in IEEE conference format (**strictly 6 pages**).

* **Source Manuscripts**:
  * [`MANUSCRIPT_SKILL_V2.md`](MANUSCRIPT_SKILL_V2.md) — Camera-ready identified version (Hemadharsana S, Sanjeev Kumar, Prajan SS).
  * [`MANUSCRIPT_SKILL_V2_ANON.md`](MANUSCRIPT_SKILL_V2_ANON.md) — Anonymized double-blind peer review submission (tracked in Git, asserted identity-leak free).
* **Rendered Builds**:
  * PDF: `MANUSCRIPT_SKILL_V2.pdf` / `MANUSCRIPT_SKILL_V2_ANON.pdf` (**6 pages**)
  * LaTeX: `MANUSCRIPT_SKILL_V2.tex` / `MANUSCRIPT_SKILL_V2_ANON.tex`
  * Word: `MANUSCRIPT_SKILL_V2.docx` / `MANUSCRIPT_SKILL_V2_ANON.docx`
* **Builder**: [`build_paper_v2.py`](build_paper_v2.py)
* **Bibliography**: [`REFERENCES_V2.bib`](REFERENCES_V2.bib)
* **Figures**:
  * `fig_v2_design.pdf` / `.png` — Delivery arms, tokenizer compression sensitivity, and attrition account.
  * `fig_v2_results.pdf` / `.png` — Results against the noise floor, domain deltas, ablations, and reversal replication.
  * `fig_v2_position.pdf` / `.png` — Judge slot-position bias deviations and permutation tests.
  * `fig_v2_retrieval.pdf` / `.png` — Routing recall, retrieval latency, and the self-audit correction record.

```bash
# Build V2 LaTeX and DOCX
uv run python paper/build_paper_v2.py
uv run python paper/build_paper_v2.py --anon

# Compile to PDF
tectonic paper/MANUSCRIPT_SKILL_V2.tex
tectonic paper/MANUSCRIPT_SKILL_V2_ANON.tex
```

---

## 2. Baseline Manuscript: V1 (Extended Study)
The initial 14-page comprehensive empirical paper.

* **Source Manuscripts**:
  * `MANUSCRIPT_SKILL.md` — Camera-ready identified baseline.
  * `MANUSCRIPT_SKILL_ANON.md` — Tracked anonymized version.
* **Rendered Builds**: `MANUSCRIPT_SKILL.pdf`, `.tex`, `.docx` (and `_ANON` variants).
* **Builder**: [`build_paper.py`](build_paper.py)
* **Bibliography**: [`REFERENCES.bib`](REFERENCES.bib)
* **Figures**: `fig_architecture.*`, `fig_arms.*`, `fig_correction.*`.

---

## 3. Warehouse Manuscript
* `MANUSCRIPT_WAREHOUSE.md` / `.pdf` / `.tex` / `.docx` — Offline cold-storage skills warehouse design.
* `PLAN_S2W_EMPIRICAL.md` — Empirical working plan.

---

## 4. Subdirectories
* [`refs/`](refs/) — Literature reference papers and structure templates:
  * `A_Hybrid_Vedic-Machine_Learning_Framework... (structure ref paper).pdf` (IEEE Conference Structure Template)
  * `Enhancing Sustainable Agriculture... (structure ref paper).pdf` (Procedia Structure Reference)
  * Published agent-skill papers: GitSkills, ACES, SkillZip, Skill RAG.
* [`archive/`](archive/) — Historical and superseded artifacts:
  * `archive/MANUSCRIPT.*` — Superseded initial draft.
  * `archive/coursework_212224040290/` — Archived coursework mini-project reports and presentations.

---

## 5. Verification & Testing
All numeric claims in the paper are CI-gated and pinned against frozen experimental logs:

```bash
uv run pytest -q tests/test_noise_floor.py tests/test_paper_claims.py
```
