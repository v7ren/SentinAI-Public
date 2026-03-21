# Temp — unconnected / legacy files

These files are not imported by `backend/main_integrated.py` or `backend/worker/core/main.py`.

Moved here so the main codebase only contains code used by the two entry points. Restore by moving back to original paths if needed.

| File | Original path |
|------|----------------|
| main4.py | backend/main4.py |
| main_sql.py | backend/main_sql.py |
| LLMindexer.py | backend/LLMindexer.py |
| worker_core/LLMindexerv2.py | backend/worker/core/LLMindexerv2.py |
| worker_core/pr_formatter.py | backend/worker/core/pr_formatter.py |
| worker_core/github_action_scanner.py | backend/worker/core/github_action_scanner.py |
| worker_core/utils/verify_redis_keys.py | backend/worker/core/utils/verify_redis_keys.py |
