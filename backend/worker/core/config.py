import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from backend.worker.core.desktop_config import desktop_get

load_dotenv()
# Load backend/worker/.env so LOG_SERVER_URL is set when running from any cwd
_worker_dir = Path(__file__).resolve().parent.parent
load_dotenv(_worker_dir / ".env")

OPENROUTER_API_KEY = desktop_get("OPENROUTER_API_KEY")  # deprecated
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- Models via OpenCode Go (OPENCODE_API_KEY) ---
OPENCODE_API_KEY = desktop_get("OPENCODE_API_KEY")
DEEPSEEK_API_KEY = OPENCODE_API_KEY or desktop_get("DEEPSEEK_API_KEY") or desktop_get("OPENROUTER_API_KEY")
DEFAULT_SCAN_MODEL = "deepseek-v4.1-flash"
_SCAN_MODEL_ALIASES = {
    "deepseek-flash": DEFAULT_SCAN_MODEL,
    "deepseek/deepseek-flash": DEFAULT_SCAN_MODEL,
    "deepseek-v4-flash": DEFAULT_SCAN_MODEL,
    "dsv4.1flash": DEFAULT_SCAN_MODEL,
    "dsv4.1-flash": DEFAULT_SCAN_MODEL,
    "deepseek-v4.1-flash": DEFAULT_SCAN_MODEL,
}
_raw_model = desktop_get("SCAN_MODEL") or DEFAULT_SCAN_MODEL
_normalized = _raw_model.split("/")[-1] if "/" in _raw_model else _raw_model
SCAN_MODEL = (
    _SCAN_MODEL_ALIASES.get(_normalized)
    or _SCAN_MODEL_ALIASES.get(_normalized.lower())
    or _normalized
)
OPENCODE_BRIDGE_URL = desktop_get("OPENCODE_BRIDGE_URL") or "http://127.0.0.1:5010"
OPENCODE_BASE_URL = desktop_get("OPENCODE_BASE_URL") or "http://127.0.0.1:4096"

# --- LLM roles (alias to SCAN_MODEL when bridge is used) ---
# Specialist / agentic loop (tool-use agents)
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", SCAN_MODEL)
AGENT_MODEL = os.getenv("AGENT_MODEL", SCAN_MODEL)

# DeepWiki / indexer (legacy names; all map to SCAN_MODEL)
INDEXER_MODEL = os.getenv("INDEXER_MODEL", SCAN_MODEL)

# Tier ladder model names (retargeted to deepseek_client; kept for compat)
CHEAP_MODEL = os.getenv("CHEAP_MODEL", SCAN_MODEL)
SMART_MODEL = os.getenv("SMART_MODEL", SCAN_MODEL)
TIER2_MODEL = os.getenv("OPENROUTER_TIER2_MODEL", SCAN_MODEL)

# Tier 1 (CHEAP_MODEL): explicit sock_read avoids spurious body-read timeouts on slow OpenRouter responses
TIER1_OPENROUTER_TIMEOUT_SECONDS = int(os.getenv("TIER1_OPENROUTER_TIMEOUT_SECONDS", "900"))

# Context compaction LLM arbitration (defaults to CHEAP_MODEL)
COMPACTION_CHEAP_MODEL = os.getenv("COMPACTION_CHEAP_MODEL", CHEAP_MODEL)

WORKER_SECRET = desktop_get("WORKER_SECRET")


DEEPWIKI_DOCS_DIR = "./deepwiki_docs"
os.makedirs(DEEPWIKI_DOCS_DIR, exist_ok=True)

MAX_WORKERS = 25

# Detection / filtering recall knobs
DETECTOR_MIN_CONFIDENCE = float(os.getenv("DETECTOR_MIN_CONFIDENCE", 6.0))
PHASE1_CONFIDENCE_THRESHOLD = float(os.getenv("PHASE1_CONFIDENCE_THRESHOLD", 6.0))
PHASE2_CONFIDENCE_THRESHOLD = float(os.getenv("PHASE2_CONFIDENCE_THRESHOLD", 6.0))
FREE_TIER_PHASE2_MAX_FINDINGS = int(os.getenv("FREE_TIER_PHASE2_MAX_FINDINGS", 8))
PHASE2_VALIDATION_MAX_PARALLEL = int(os.getenv("PHASE2_VALIDATION_MAX_PARALLEL", 20))
PHASE2_VALIDATION_TIMEOUT_SECONDS = int(os.getenv("PHASE2_VALIDATION_TIMEOUT_SECONDS", 90))
PHASE2_VALIDATION_MAX_RETRIES = int(os.getenv("PHASE2_VALIDATION_MAX_RETRIES", 2))
AGENTIC_CONFIDENCE_CEILING = float(os.getenv("AGENTIC_CONFIDENCE_CEILING", 8.5))
AGENTIC_TIER3_MAX_TOOL_CALLS_PER_FINDING = int(os.getenv("AGENTIC_TIER3_MAX_TOOL_CALLS_PER_FINDING", 3))
AGENTIC_TIER3_MAX_TOOL_CALLS_PER_SCAN = int(os.getenv("AGENTIC_TIER3_MAX_TOOL_CALLS_PER_SCAN", 60))
AGENTIC_TIER4_MAX_TOOL_CALLS_PER_FINDING = int(os.getenv("AGENTIC_TIER4_MAX_TOOL_CALLS_PER_FINDING", 5))
AGENTIC_TIER4_MAX_TOOL_CALLS_PER_SCAN = int(os.getenv("AGENTIC_TIER4_MAX_TOOL_CALLS_PER_SCAN", 120))
TIER4_AGENTIC_CONFIDENCE_FLOOR = float(os.getenv("TIER4_AGENTIC_CONFIDENCE_FLOOR", 7.0))
ENABLE_TIER23_SAFE_ESCALATION = os.getenv("ENABLE_TIER23_SAFE_ESCALATION", "true").lower() == "true"
TIER23_SAFE_ESCALATION_KEYWORD_COUNT = int(os.getenv("TIER23_SAFE_ESCALATION_KEYWORD_COUNT", 3))
# Set VALIDATOR_DEBUG=1 to log full raw LLM response when Phase 2 parse fails (for debugging)
VALIDATOR_DEBUG = os.getenv("VALIDATOR_DEBUG", "0").strip() in ("1", "true", "yes")

# SkepticPass (post-scan adversarial validation)
SKEPTIC_PASS_ENABLED = os.getenv("SKEPTIC_PASS_ENABLED", "true").lower() == "true"
SKEPTIC_CVSS_THRESHOLD = float(os.getenv("SKEPTIC_CVSS_THRESHOLD", "7.0"))
SKEPTIC_MAX_PARALLEL = int(os.getenv("SKEPTIC_MAX_PARALLEL", "6"))
# Set SKEPTIC_DEBUG=1 to log full request/response for skeptic_failed findings (for debugging)
SKEPTIC_DEBUG = os.getenv("SKEPTIC_DEBUG", "0").strip() in ("1", "true", "yes")
ENABLE_CONTEXT_COMPACTION = os.getenv("ENABLE_CONTEXT_COMPACTION", "true").lower() == "true"
COMPACTION_MIN_CHARS = int(os.getenv("COMPACTION_MIN_CHARS", 20000))
COMPACTION_USE_CHEAP_LLM = os.getenv("COMPACTION_USE_CHEAP_LLM", "true").lower() == "true"
COMPACTION_LLM_MAX_CANDIDATES = int(os.getenv("COMPACTION_LLM_MAX_CANDIDATES", 220))
COMPACTION_CHEAP_MODEL_TIMEOUT_SECONDS = int(os.getenv("COMPACTION_CHEAP_MODEL_TIMEOUT_SECONDS", 45))
COMPACTION_MAX_DROP_RATIO = float(os.getenv("COMPACTION_MAX_DROP_RATIO", 0.35))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# Set REDIS_OPTIONAL=1 to allow MockRedis fallback (unit tests, dev without Redis)
REDIS_OPTIONAL = os.getenv("REDIS_OPTIONAL", "0").strip() in ("1", "true", "yes")
SCAN_TTL = 3600
PROJECT_CACHE_TTL = int(os.getenv("PROJECT_CACHE_TTL", 21600))

# Multi-agent scan (Phase 1 expansion)
# Claude/Anthropic support intentionally removed.
AGENT_SCAN_ENABLED = os.getenv("AGENT_SCAN_ENABLED", "true").lower() == "true"
# When True, specialists receive metadata only and use tools (fetch_file, etc.) to request code on demand.
AGENT_AGENTIC_ENABLED = os.getenv("AGENT_AGENTIC_ENABLED", "true").lower() == "true"
AGENT_AGENTIC_MAX_ROUNDS = int(os.getenv("AGENT_AGENTIC_MAX_ROUNDS", "10"))
# Not yet applied to coordinator (import was unused); kept for future wall-clock cap on specialist phase
AGENT_PARALLEL_TIMEOUT_SECONDS = int(os.getenv("AGENT_PARALLEL_TIMEOUT", "120"))
# OpenRouter (Minimax etc.) can be slow; allow longer for agentic loop request+response body read
AGENT_OPENROUTER_TIMEOUT_SECONDS = int(os.getenv("AGENT_OPENROUTER_TIMEOUT_SECONDS", "240"))
AGENT_MAX_FILE_TOKENS = int(os.getenv("AGENT_MAX_FILE_TOKENS", "50000"))

# Optional agent pipeline (Phase 2/3): chain combiner, attack path simulator, remediation
AGENT_CHAIN_COMBINER_ENABLED = os.getenv("AGENT_CHAIN_COMBINER_ENABLED", "true").lower() == "true"
AGENT_ATTACK_PATH_SIMULATOR_ENABLED = os.getenv("AGENT_ATTACK_PATH_SIMULATOR_ENABLED", "true").lower() == "true"
AGENT_REMEDIATION_ENABLED = os.getenv("AGENT_REMEDIATION_ENABLED", "true").lower() == "true"

# Scan diff mode (Phase 4): incremental scan on changed files only
SCAN_DIFF_ENABLED = os.getenv("SCAN_DIFF_ENABLED", "true").lower() == "true"
SCAN_DIFF_EXPAND_DEPTH = int(os.getenv("SCAN_DIFF_EXPAND_DEPTH", "2"))

# Dependency scanner (Phase 4): OSV CVE correlation (enabled by default for SCA coverage)
DEPENDENCY_SCANNER_ENABLED = os.getenv("DEPENDENCY_SCANNER_ENABLED", "true").lower() == "true"
OSV_API_URL = os.getenv("OSV_API_URL", "https://api.osv.dev/v1/query")

# Git context (Phase 4): churn, recent files
GIT_CONTEXT_ENABLED = os.getenv("GIT_CONTEXT_ENABLED", "true").lower() == "true"

# LLM security specialist (Phase 5): prompt injection, etc.
AGENT_LLM_SECURITY_ENABLED = os.getenv("AGENT_LLM_SECURITY_ENABLED", "true").lower() == "true"

# High-Recall Mode: When enabled, the scanner keeps low-confidence findings
# and uncertain items as "informational" instead of hard-dropping them.
# This improves recall at the cost of potentially more noise.
# Default: False (strict filtering for production use)
HIGH_RECALL_MODE = os.getenv("HIGH_RECALL_MODE", "false").lower() in ("1", "true", "yes")

# FP Filter Strictness: Controls how aggressively to filter potential false positives
# "strict" = hard-drop most uncertain findings (default for production)
# "balanced" = keep uncertain items with reduced confidence
# "permissive" = keep almost everything, mark with confidence levels
FP_FILTER_STRICTNESS = os.getenv("FP_FILTER_STRICTNESS", "strict").lower()

# Live log server: if set, AgentLogger will POST each event to this URL for real-time dashboard
# Example: http://127.0.0.1:5003 (no trailing slash)
LOG_SERVER_URL = (os.getenv("LOG_SERVER_URL") or "").rstrip("/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScannerWorker-Py3.14")
