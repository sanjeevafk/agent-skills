---
name: saveetha-learner-ops
description: Saveetha Learner Portal automation workflows for Circular tasks, Daily Study Week reports, high-speed CIA exam slot booking/sniping, subject details, and discussion responders. Use when interacting with learner.saveetha.in.
metadata:
  origin: ECC-Saveetha
---

# Saveetha Learner Portal Operations

Operator workflow and CLI reference for the **Saveetha Engineering College Learner Portal** (`https://learner.saveetha.in/`).

---

## 1. Environment & Credentials

- **Script Repository**: `/home/sanjeev/saveetha-scripts/`
- **Config / Environment**: `/home/sanjeev/saveetha-scripts/.env`
- **Python Virtualenv**: `/home/sanjeev/.agent-reach-venv/bin/python3`

### Key Variables in `.env`:
```env
SAVEETHA_COOKIE="csrftoken=<64-char-token>;sessionid=<session_id>"
SAVEETHA_STUDENT_NAME="SANJEEV KUMAR S"
```

---

## 2. Core Python CLI Utilities

### A. Daily Planner & Circular Submitter (`saveetha_daily_planner.py`)

Automates drafting and submitting Bootstrap-styled HTML daily completion reports to circular tasks (e.g. Circular 125 Study Week).

```bash
# 1. Inspect live status of all circular tasks
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_daily_planner.py --status

# 2. Preview report table without submitting (Dry Run)
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_daily_planner.py --day 5 --type study --exam "Calculus & Matrix Algebra" --dry-run

# 3. Submit Day 5 (Friday) completion report
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_daily_planner.py --day 5 --type exam_morning --exam "Compiler Design (19CS409)" --venue "1852"
```

#### Task Mapping (Circular 125):
- **Day 1 (Mon)**: Task #48
- **Day 2 (Tue)**: Task #49
- **Day 3 (Wed)**: Task #50
- **Day 4 (Thu)**: Task #51
- **Day 5 (Fri)**: Task #52

---

### B. High-Speed Exam Slot Watcher & Sniper (`saveetha_slot_booker.py`)

Sub-100ms persistent slot watcher with connection jitter (±10%), adaptive backoff on HTTP 429, and automated booking upon seat drops.

```bash
# 1. Single check / Dry run (Lists matching slots & live capacities)
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_slot_booker.py --date "Aug 14,Aug 16" --filter "CIA" --dry-run

# 2. Continuous Sniper Mode (1.0s interval, auto-books up to 4 slots)
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_slot_booker.py --date "Aug 14,Aug 16" --filter "CIA" --max-slots 4 -w -i 1.0

# 3. Launch in background with logging
nohup /home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_slot_booker.py --date "Aug 14,Aug 16" --filter "CIA" --max-slots 4 -w -i 1.0 > /home/sanjeev/saveetha-scripts/watcher.log 2>&1 &
```

---

### C. Discussion Forum Responder (`saveetha_discussion_responder.py`)

Multi-course automated discussion forum answer generator with LLM failover.

```bash
/home/sanjeev/.agent-reach-venv/bin/python3 /home/sanjeev/saveetha-scripts/saveetha_discussion_responder.py
```

---

## 3. Discovered Portal Architecture & Endpoints

| Endpoint | HTTP Method | Purpose |
| :--- | :--- | :--- |
| `/academics/circulars/<cid>/?tab=tasks` | `GET` | Circular task listings and submission forms |
| `/academics/circulars/<cid>/tasks/<tid>/submission/` | `POST` | Submit daily completion reports |
| `/academicevents/event-booking/?event_term=...` | `GET / POST` | Live exam slot availability & booking |
| `/academics/studentsubjects/` | `GET` | Enrolled subjects, course codes & attendance |
| `/academics/studentsubjects/<slot_id>/` | `GET` | Subject details, sessions, and course outcomes |

---

## 4. Guardrails & Operational Rules

1. **CSRF Handling**: Always extract the fresh 64-character `csrftoken` from the GET response and update both `X-CSRFToken` and the `Cookie` header before POSTing to avoid HTTP 403 errors.
2. **Never Hardcode Secrets**: Session cookies must be read from `.env` dynamically.
3. **Verify State**: Always run `--status` before and after submissions to confirm `✅ SUBMITTED (200 OK)`.
