"""
Log Bridge — Connects AgentLogger to LogServer for real-time streaming.

This module provides a bridge between the file-based AgentLogger and the
WebSocket-based LogServer. When the log server is running, events are
broadcast in real-time to connected clients.

Usage:
    from backend.worker.core.log_bridge import LogBridge, get_log_bridge
    
    # Initialize bridge (call once at scan start)
    bridge = get_log_bridge()
    bridge.start_scan("scan-123", "python", "flask", 42)
    
    # During agent execution
    bridge.log_agent_start("InjectionSpecialist", "specialist", config={...})
    bridge.log_agent_prompt("InjectionSpecialist", prompt, tokens=500)
    bridge.log_agent_response("InjectionSpecialist", response, tokens=1200, latency_ms=3500)
    bridge.log_agent_findings("InjectionSpecialist", findings_list)
    bridge.log_agent_complete("InjectionSpecialist", exec_time_ms, tokens, errors, count)
"""

import asyncio
import json
import os
import sys
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Try to import the log server interface
try:
    from backend.worker.core.log_server import log_interface, LogServerInterface
    LOG_SERVER_AVAILABLE = True
except ImportError:
    LOG_SERVER_AVAILABLE = False
    log_interface = None
    LogServerInterface = None

# Import agent logger for file-based logging
from backend.worker.core.agents.agent_logger import AgentLogger


class LogBridge:
    """
    Bridge between AgentLogger (file-based) and LogServer (WebSocket streaming).
    
    When the log server is running, this broadcasts events in real-time.
    It also maintains the file-based AgentLogger for persistence.
    """
    
    def __init__(self, scan_id: str):
        """
        Initialize the log bridge.
        
        Args:
            scan_id: The scan identifier for this session
        """
        self.scan_id = scan_id
        self.file_logger: Optional[AgentLogger] = None
        self.server_interface: Optional[LogServerInterface] = None
        self._enabled = True
    
    def set_file_logger(self, logger: AgentLogger):
        """Set the file-based agent logger."""
        self.file_logger = logger
    
    def set_server_interface(self, interface: LogServerInterface):
        """Set the WebSocket log server interface."""
        self.server_interface = interface
    
    def enable(self):
        """Enable logging."""
        self._enabled = True
    
    def disable(self):
        """Disable logging (for testing)."""
        self._enabled = False
    
    # =========================================================================
    # Scan Lifecycle
    # =========================================================================
    
    def start_scan(self, language: str = "", framework: str = "", file_count: int = 0):
        """Log scan start event."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_scan_start(
                scan_id=self.scan_id,
                language=language,
                framework=framework,
                file_count=file_count,
            )
    
    def end_scan(self, total_findings: int = 0, total_time_ms: int = 0):
        """Log scan completion event."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_scan_complete(
                scan_id=self.scan_id,
                total_findings=total_findings,
                total_time_ms=total_time_ms,
            )
        
        if self.file_logger:
            self.file_logger.finalize({
                "total_findings": total_findings,
                "total_time_ms": total_time_ms,
            })
    
    # =========================================================================
    # Agent Lifecycle
    # =========================================================================
    
    def log_agent_start(
        self,
        agent_name: str,
        agent_type: str,
        context: Optional[Dict] = None,
        config: Optional[Dict] = None,
    ):
        """
        Log agent start event.
        
        Args:
            agent_name: Name of the agent (e.g., "InjectionSpecialist")
            agent_type: Type of agent ("pre-scan", "specialist", "synthesis", "validation")
            context: Agent context summary
            config: Agent configuration
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_agent_start(
                agent_name=agent_name,
                agent_type=agent_type,
                scan_id=self.scan_id,
                config=config or {},
            )
        
        if self.file_logger:
            self.file_logger.log_agent_start(
                agent_name=agent_name,
                agent_type=agent_type,
                context=context or {},
                config=config or {},
            )
    
    def log_agent_prompt(
        self,
        agent_name: str,
        prompt: str,
        prompt_tokens: Optional[int] = None,
    ):
        """
        Log the prompt sent to the LLM.
        
        Args:
            agent_name: Name of the agent
            prompt: The full prompt text
            prompt_tokens: Token count if available
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_agent_prompt(
                agent_name=agent_name,
                prompt=prompt,
                prompt_tokens=prompt_tokens,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_agent_prompt(
                agent_name=agent_name,
                prompt=prompt,
                prompt_tokens=prompt_tokens,
            )
    
    def log_agent_response(
        self,
        agent_name: str,
        response: str,
        response_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ):
        """
        Log the response from the LLM.
        
        Args:
            agent_name: Name of the agent
            response: The raw LLM response
            response_tokens: Token count if available
            latency_ms: Response time in milliseconds
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_agent_response(
                agent_name=agent_name,
                response=response,
                response_tokens=response_tokens,
                latency_ms=latency_ms,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_agent_response(
                agent_name=agent_name,
                response=response,
                response_tokens=response_tokens,
                latency_ms=latency_ms,
            )
    
    def log_tool_call(
        self,
        agent_name: str,
        tool_name: str,
        tool_args: Dict[str, Any],
    ):
        """
        Log a tool call made by the agent.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool/function called
            tool_args: Arguments passed to the tool
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_tool_call(
                agent_name=agent_name,
                tool_name=tool_name,
                tool_args=tool_args,
                scan_id=self.scan_id,
            )
        
        # Also log to file logger if available
        if self.file_logger:
            # Store as metadata in agent_findings-like entry
            self.file_logger._write_entry({
                "event_type": "tool_call",
                "agent_name": agent_name,
                "tool_name": tool_name,
                "tool_args": tool_args,
            })
    
    def log_tool_result(
        self,
        agent_name: str,
        tool_name: str,
        tool_result: Any,
    ):
        """
        Log the result from a tool call.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool
            tool_result: Result returned by the tool
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_tool_result(
                agent_name=agent_name,
                tool_name=tool_name,
                tool_result=tool_result,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger._write_entry({
                "event_type": "tool_result",
                "agent_name": agent_name,
                "tool_name": tool_name,
                "result_preview": str(tool_result)[:500],
            })
    
    def log_agent_findings(
        self,
        agent_name: str,
        findings: List[Dict[str, Any]],
        parsing_errors: Optional[List[str]] = None,
    ):
        """
        Log the findings produced by an agent.
        
        Args:
            agent_name: Name of the agent
            findings: List of finding dictionaries
            parsing_errors: Any errors during response parsing
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_agent_findings(
                agent_name=agent_name,
                findings=findings,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_agent_findings(
                agent_name=agent_name,
                findings=findings,
                parsing_errors=parsing_errors,
            )
    
    def log_agent_complete(
        self,
        agent_name: str,
        execution_time_ms: int,
        token_usage: int,
        errors: List[str],
        findings_count: int,
    ):
        """
        Log agent completion.
        
        Args:
            agent_name: Name of the agent
            execution_time_ms: Total execution time
            token_usage: Total tokens used
            errors: Any errors encountered
            findings_count: Number of findings produced
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_agent_complete(
                agent_name=agent_name,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage,
                errors=errors,
                findings_count=findings_count,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_agent_complete(
                agent_name=agent_name,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage,
                errors=errors,
                findings_count=findings_count,
            )
    
    # =========================================================================
    # Pipeline Events
    # =========================================================================
    
    def log_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        phase_data: Optional[Dict] = None,
    ):
        """
        Log a phase transition in the pipeline.
        
        Args:
            from_phase: Previous phase name
            to_phase: New phase name
            phase_data: Additional phase information
        """
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_phase_transition(
                from_phase=from_phase,
                to_phase=to_phase,
                data=phase_data or {},
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_phase_transition(
                from_phase=from_phase,
                to_phase=to_phase,
                phase_data=phase_data or {},
            )
    
    def log_deduplication(
        self,
        input_findings: int,
        output_findings: int,
        duplicates_found: int,
        merged_groups: List[Dict],
    ):
        """Log deduplication engine activity."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "deduplication",
                    "agent_name": "DeduplicationEngine",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "input_findings": input_findings,
                        "output_findings": output_findings,
                        "duplicates_found": duplicates_found,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_deduplication(
                input_findings=input_findings,
                output_findings=output_findings,
                duplicates_found=duplicates_found,
                merged_groups=merged_groups,
            )
    
    def log_consensus_scoring(
        self,
        findings_scored: int,
        confidence_adjustments: List[Dict],
    ):
        """Log consensus scoring activity."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "consensus_scoring",
                    "agent_name": "ConsensusScorer",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "findings_scored": findings_scored,
                        "adjustments": confidence_adjustments,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_consensus_scoring(
                findings_scored=findings_scored,
                confidence_adjustments=confidence_adjustments,
            )
    
    def log_skeptic_review(
        self,
        findings_reviewed: int,
        verdicts: List[Dict],
        rejection_rate: float,
    ):
        """Log SkepticAgent review results."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "skeptic_review",
                    "agent_name": "SkepticAgent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "findings_reviewed": findings_reviewed,
                        "verdicts": verdicts,
                        "rejection_rate": rejection_rate,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_skeptic_review(
                findings_reviewed=findings_reviewed,
                verdicts=verdicts,
                rejection_rate=rejection_rate,
            )
    
    def log_chain_combiner(
        self,
        chains_created: int,
        unchained_findings: int,
        chains: List[Dict],
    ):
        """Log ChainCombiner results."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "chain_combiner",
                    "agent_name": "ChainCombiner",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "chains_created": chains_created,
                        "unchained_findings": unchained_findings,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_chain_combiner(
                chains_created=chains_created,
                unchained_findings=unchained_findings,
                chains=chains,
            )
    
    def log_attack_paths(
        self,
        paths_simulated: int,
        paths: List[Dict],
    ):
        """Log AttackPathSimulator results."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "attack_paths",
                    "agent_name": "AttackPathSimulator",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "paths_simulated": paths_simulated,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_attack_paths(
                paths_simulated=paths_simulated,
                paths=paths,
            )
    
    def log_remediation(
        self,
        remediations_generated: int,
        remediations: List[Dict],
    ):
        """Log RemediationAgent results."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.broadcast_event(
                type("Event", (), {
                    "event_type": "remediation",
                    "agent_name": "RemediationAgent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "scan_id": self.scan_id,
                    "data": {
                        "remediations_generated": remediations_generated,
                    },
                })()
            )
        
        if self.file_logger:
            self.file_logger.log_remediation(
                remediations_generated=remediations_generated,
                remediations=remediations,
            )
    
    def log_error(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
    ):
        """Log an error during agent execution."""
        if not self._enabled:
            return
        
        if self.server_interface:
            self.server_interface.log_error(
                agent_name=agent_name,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                scan_id=self.scan_id,
            )
        
        if self.file_logger:
            self.file_logger.log_error(
                agent_name=agent_name,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
            )


# =============================================================================
# Global Instance Management
# =============================================================================

_current_bridge: Optional[LogBridge] = None


def create_log_bridge(scan_id: str, enable_file_logging: bool = True) -> LogBridge:
    """
    Create a new log bridge for a scan.
    
    Args:
        scan_id: The scan identifier
        enable_file_logging: Whether to also log to files
    
    Returns:
        A LogBridge instance
    """
    global _current_bridge
    
    bridge = LogBridge(scan_id)
    
    # Connect to log server if available
    if LOG_SERVER_AVAILABLE and log_interface:
        bridge.set_server_interface(log_interface)
    
    # Create file logger if requested
    if enable_file_logging:
        try:
            file_logger = AgentLogger(scan_id)
            bridge.set_file_logger(file_logger)
        except Exception as e:
            print(f"[LogBridge] Warning: Could not create file logger: {e}")
    
    _current_bridge = bridge
    return bridge


def get_log_bridge() -> Optional[LogBridge]:
    """Get the current log bridge instance."""
    return _current_bridge


def clear_log_bridge():
    """Clear the current log bridge instance."""
    global _current_bridge
    _current_bridge = None


# =============================================================================
# Convenience Functions for Direct Use
# =============================================================================

def log_tool_call(agent_name: str, tool_name: str, tool_args: Dict[str, Any]):
    """
    Convenience function to log a tool call.
    
    Use this when you don't have direct access to the LogBridge instance.
    """
    bridge = get_log_bridge()
    if bridge:
        bridge.log_tool_call(agent_name, tool_name, tool_args)


def log_tool_result(agent_name: str, tool_name: str, tool_result: Any):
    """
    Convenience function to log a tool result.
    
    Use this when you don't have direct access to the LogBridge instance.
    """
    bridge = get_log_bridge()
    if bridge:
        bridge.log_tool_result(agent_name, tool_name, tool_result)