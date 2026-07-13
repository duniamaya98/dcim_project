# MT-018 Hardening — Goal Prompt

> **Built with:** goal-prompt-builder skill (§ Custom scenario, Python project type)
> **Reviewer:** Hermes DCIM Orchestrator
> **Date:** 2026-06-25

---

## /goal Prompt (Copy This)

```
/goal Hardening MT-018 Traditional ML pipeline for production: fix 2 critical security/data-integrity issues and 5 high-priority operational gaps across 3 Python scripts, database schema, and documentation.

First action: Read the following files and report line counts + hardcoded credential count:
- notebooks/dataset_preparation.py
- src/anomaly_inference.py
- src/adaptive_retrain.py
- .env (if exists)
- .gitignore (if exists)
Report: total files found, total lines, grep result for "infra:password" occurrences per file.
Wait for ack before starting implementation.

Scope:
  IN: notebooks/dataset_preparation.py, src/anomaly_inference.py, src/adaptive_retrain.py, .env (new), .env.example (new), .gitignore, server_anomalies table schema, MT-018 document Section 9 status
  OUT: Addendum v1.2.0 feature implementation (future work), new ML models, Isolation Forest parameter changes, server_metrics table changes, other MT documents (MT-019 etc)

Constraints:
- Python project using ragavenv virtual environment (source ragavenv/bin/activate)
- Database: PostgreSQL 16 + TimescaleDB, db=dcim_ai, user=infra, host=127.0.0.1
- Only new dependency allowed: python-dotenv (for credential management)
- Do NOT modify server_metrics table schema
- Do NOT change Isolation Forest parameters (n_estimators=200, contamination=0.05, random_state=42)
- Do NOT change model artifact file names (isolation_forest_baseline.pkl, scaler_baseline.pkl, feature_columns.pkl)
- Preserve backward compatibility: existing pipeline must still work after changes
- All code changes must include inline comments explaining the fix
- Credentials must NEVER appear in source code after hardening

Done when:
1. grep -rn "infra:password" notebooks/ src/ returns ZERO matches (credentials fully externalized)
2. .env file exists with DCIM_DB_URL variable, .env.example exists without real password, .gitignore blocks .env and *.pkl
3. All 3 Python scripts import os + dotenv, load DCIM_DB_URL from environment, raise EnvironmentError if missing
4. psql -U infra -d dcim_ai -c "\d server_anomalies" shows hostname TEXT column exists
5. src/anomaly_inference.py DELETEs overlapping time range from server_anomalies before INSERT (dedup logic present)
6. src/adaptive_retrain.py creates models/archive/ directory, copies old .pkl files with timestamp suffix, writes metadata JSON with version/train_samples/anomaly_ratio
7. src/anomaly_inference.py prints [MONITOR] line with inference_latency_ms, anomaly_ratio, anomaly_count, total_rows after prediction
8. MT-018 document Section 9 reads "Completed (Baseline)" with planned items listed below

Stop if:
- Implementation requires changing Isolation Forest model parameters
- server_metrics table schema needs modification
- Any script fails to import after changes (python -c "import X" must succeed for each)
- More than 1 new pip dependency required beyond python-dotenv
- Existing test data in server_anomalies is lost (dedup must preserve non-overlapping rows)
- Credentials appear in git diff (git diff must not contain "password" or actual DB URL)

Use a token budget of 80K tokens for this goal.
```

---

## Audit Friendliness Score

| Check | Score | Notes |
|-------|-------|-------|
| Acceptance count | ✅ 8 items | Range 5-8 is excellent |
| Vague verbs | ✅ None | All items use specific verbs (grep, exists, shows, prints) |
| Stop-if specificity | ✅ Mechanically detectable | Each stop-if can be verified with grep/import/diff |
| Token budget | ✅ Present | 80K appropriate for 7-task scope |
| Mechanical verifiability | ✅ Every Done-when cites file, command, or artifact | No vague "works correctly" |
| **Overall** | **95%** | Ship-ready |

---

## Design Choices

**1. First action = "read + report counts"**
Forces agent to inventory current state before making changes. Prevents blind implementation and establishes baseline.

**2. Scope separates IN/OUT explicitly**
Addendum v1.2.0 is tempting scope creep. IN scope = baseline hardening only. OUT scope = future feature work. Agent cannot claim "done" by implementing addendum features.

**3. Constraints pull from project reality**
- ragavenv (not generic venv)
- PostgreSQL 16 + TimescaleDB (not SQLite)
- Exact model parameters frozen
- Only python-dotenv as new dependency

**4. Done when = verifiable commands**
Every item has a concrete check: `grep`, `psql`, `python -c`, file existence, output format. No "tests pass" without specifying which tests.

**5. Stop if = regression guards**
- No parameter changes → model behavior preserved
- No schema changes to source table → ingestion pipeline safe
- Import must succeed → no broken dependencies
- git diff clean of secrets → security enforced

**6. Token budget at 80K**
7 tasks × ~10K avg per task = 70K, plus overhead for verification. 80K gives comfortable margin without enabling scope creep.

---

## Execution Notes

Agent types this supports:
- **Claude Code** — paste directly as prompt
- **Codex** — paste as task description
- **Hermes Dev agent** — paste as goal prompt
- **Copilot** — paste as inline instruction

After execution, agent should produce:
- Modified: 3 Python files, 1 markdown doc
- Created: .env, .env.example, .gitignore
- Database: ALTER TABLE server_anomalies ADD COLUMN hostname
- Archive: models/archive/ with versioned artifacts

---

## Quick Reference: What Each Task Does

| Task | File | Fix | Verification |
|------|------|-----|--------------|
| 1 | .env + 3 scripts | Credentials → env vars | `grep -rn "infra:password"` = 0 |
| 2 | .gitignore | Block .env + *.pkl | `cat .gitignore` |
| 3 | 3 scripts | dotenv import + load | `python -c "from dotenv import load_dotenv"` |
| 4 | DB schema | Add hostname column | `psql \d server_anomalies` |
| 5 | anomaly_inference.py | DELETE before INSERT | `python src/anomaly_inference.py` run 2x no dup |
| 6 | adaptive_retrain.py | Archive + metadata | `ls models/archive/metadata_*.json` |
| 7 | anomaly_inference.py | [MONITOR] logging | stdout shows latency + ratio |
| 8 | MT-018 doc | Status clarification | `grep "Completed (Baseline)" doc` |
