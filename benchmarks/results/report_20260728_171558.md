# Rigorous Agent-Skills Evaluation Report (Tasks Hard)

> **Generated at**: `2026-07-28T17:15:58.402314+00:00`
> **Total Comparisons**: `7` | **Runs per Task**: `3`

## 📊 Executive Dashboard

| Metric | Treatment (Agent + Skill) | Control (Base Agent) | Impact / Delta |
|---|---|---|---|
| **Win Rate** | **14.3%** (1 wins) | 85.7% (6 wins) | **+-71.4%** |
| **Average Score** (max 35) | **29.71** | 34.14 | **+-4.43** |
| **95% Confidence Score** | `[26.71, 32.72]` | `[32.79, 35.5]` | - |
| **Avg Latency** (duration) | 60.87s | 84.47s | **-27.9%** (-23.6s) |
| **Statistical Significance** | **p = 0.0105** (t = -3.286) | - | ✅ Significant (p < 0.05) |

---

## 🔍 Task-level Breakdown

| Task ID | Skill | Model | Win/Loss/Draw | Avg Score (T vs C) | Avg Latency (T vs C) | p-value |
|---|---|---|---|---|---|---|
| `secure-review-hard` | `security-review` | `Default Model` | 1-2-0 | **30.0** vs 33.67 | 29.94s vs 37.21s | 0.3051 |
| `debug-loop-hard` | `debugging-code` | `Default Model` | 0-2-0 | **31.5** vs 35.0 | 25.14s vs 33.74s | 0.2578 |
| `tdd-plan-hard` | `tdd` | `Default Model` | 0-2-0 | **27.5** vs 34.0 | 142.99s vs 206.09s | 0.0489⭐ |

---

## 📈 Historical Regression Trends

| Run Timestamp | Treatment Score | Control Score | Score Delta | Treatment Latency | Control Latency |
|---|---|---|---|---|---|
| `2026-07-28T17:15:58.402314+00:00` | **29.71** | 34.14 | **+-4.43** | 60.87s | 84.47s |

---

### 🧬 Detailed Run Artifacts

#### Task: `secure-review-hard` (`Default Model`)
- **Skill**: `security-review`
- **T-Test**: `t = -1.238`, `p = 0.3051`

**Run 1:**
*   **Control Score**: `31/35` (Latency: 33.4s)
*   **Treatment Score**: `35/35` (Latency: 30.6s)
    *   *Judge Justification*: Agent B is clean and highly professional, avoiding any leaked internal monologues. It includes helpful deep-links to specific lines inside the generated artifact. Furthermore, it demonstrates superior reasoning by immediately calling out the primary architectural issue with memory-backed storage (RAM exhaustion under load) and asking relevant, high-value follow-up questions to address it.

**Run 2:**
*   **Control Score**: `35/35` (Latency: 41.2s)
*   **Treatment Score**: `29/35` (Latency: 28.6s)
    *   *Judge Justification*: Agent A provides a solid conceptual guide and sequence diagram, but relies on mock simulations for critical parts such as quota validation. Its middleware uses a hardcoded tenant ID, and the quota validation is evaluated after the file has already been fully parsed into memory by Multer, exposing the system to heap exhaustion DoS. The filename sanitization also relies on an external package rather than implementing the sanitization logic natively.

**Run 3:**
*   **Control Score**: `35/35` (Latency: 37.0s)
*   **Treatment Score**: `26/35` (Latency: 30.7s)
    *   *Judge Justification*: Agent B's implementation has a security/correctness flaw: it checks the quota before parsing the multi-part form and increments it afterwards without any atomic database transaction or locking. This leaves the application vulnerable to concurrent upload race conditions. It also did not provide a SQL database schema (only TypeScript interfaces of mock entities) and extracts unverified user/tenant IDs directly from HTTP headers, which is a poor authorization practice.


#### Task: `debug-loop-hard` (`Default Model`)
- **Skill**: `debugging-code`
- **T-Test**: `t = -2.333`, `p = 0.2578`

**Run 1:**
*   **Control Score**: `35/35` (Latency: 31.0s)
*   **Treatment Score**: `33/35` (Latency: 26.4s)
    *   *Missing Keywords*: `['strace', 'trace|tracing|jaeger|zipkin']`
    *   *Judge Justification*: While Agent B provides a highly structured response, including a helpful Mermaid flowchart and excellent advice on running tcpdump in a ring-buffer mode to prevent disk saturation, it has minor technical inaccuracies. In the strace phase, it omits 'futex' from its system call tracing flags, which would hinder connection pool contention debugging. Additionally, its example strace output shows the 'recvfrom' system call receiving the SQL command 'SELECT...', which is technically incorrect since recvfrom reads query results from the database socket, whereas queries are sent using write/sendto.

**Run 2:**
*   **Control Score**: `35/35` (Latency: 36.5s)
*   **Treatment Score**: `30/35` (Latency: 23.9s)
    *   *Judge Justification*: Response A is technically strong and provides high-quality diagnostic details, including excellent database lock queries. However, it lacks production safety controls: tcpdump captures do not use circular buffers (posing a risk of running out of disk space), and strace is run without system call filtering, which can cause significant performance degradation on a busy service. There is also a minor syscall logging error where a futex wait with a NULL timeout parameter is depicted as returning ETIMEDOUT.


#### Task: `tdd-plan-hard` (`Default Model`)
- **Skill**: `tdd`
- **T-Test**: `t = -13.0`, `p = 0.0489`

**Run 1:**
*   **Control Score**: `34/35` (Latency: 245.6s)
*   **Treatment Score**: `27/35` (Latency: 156.3s)
    *   *Judge Justification*: Response A demonstrates solid technical grounding: correct BVA boundary enumeration (0, 1, max-1, max, max+1), well-structured decision tables with accurate combination counts (8, 10, 12), and the heap-sampling memory test is a genuinely correct approach to detecting streaming contract violations. The tracer-bullet-first cycle ordering is a good architectural pattern. Weak points: security coverage is thin (no mention of encoding attacks, billion-laughs, or overlong UTF-8), and the open-questions section — while intellectually honest — signals the design is incomplete rather than comprehensive. The Unicode boundary list (U+007F through U+10FFFF) is correct and well-chosen. Decision table row counts are internally consistent. Main gap: no back-pressure or throughput regression assertions, and no run configuration guidance.

**Run 2:**
*   **Control Score**: `34/35` (Latency: 166.5s)
*   **Treatment Score**: `28/35` (Latency: 129.7s)
    *   *Missing Keywords*: `['unicode|utf']`
    *   *Judge Justification*: Response B is well-organized and developer-friendly, with a clear emphasis on public-interface-only testing (good for maintainability) and a clean summary table for boundary value analysis. The chunk boundary fuzz (CB-01) and the heap invariant check (L-01, <50 MB growth) are solid ideas. However, the security and Unicode depth is noticeably weaker — there is no treatment of the UTF-16 delimiter scanning hazard, BOM mismatch errors, or encoding-specific corruption modes. The decision table (Q-03–Q-11) is mentioned but not elaborated to the same depth as A's three-axis breakdown. The '50 MB' heap threshold in L-01 is somewhat arbitrary and not justified relative to chunk size, making it less rigorous than A's proportional invariant. The 'Open Questions' section is useful for practitioners but indicates the response is less complete as a standalone test specification. Instruction adherence is slightly lower because multi-byte UTF-16 sequences are not meaningfully covered, which was an explicit prompt requirement.

