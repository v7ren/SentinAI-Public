"""
Multi-Agent Security Analysis Framework

This module provides a collaborative multi-agent platform for cross-file security analysis.
"""

from .base_agent import BaseAgent
from .coordinator import AgentCoordinator
from .models import AgentContext, AgentFinding, AgentResult

__all__ = [
    "BaseAgent",
    "AgentCoordinator",
    "AgentContext",
    "AgentFinding",
    "AgentResult",
]
