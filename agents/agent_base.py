"""
=============================================================================
AGENT BASE CLASS - Foundation for All CogniGuard Agents
=============================================================================

Every agent in CogniGuard inherits from this base class.
It provides:
- Unified logging
- State management
- Communication between agents
- Performance tracking
- Error handling

=============================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import time
import traceback


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentAction:
    """Record of an action taken by an agent"""
    agent_name: str
    action_type: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Optional[Dict] = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class AgentMessage:
    """Message passed between agents"""
    from_agent: str
    to_agent: str
    message_type: str       # "threat_alert", "learning_update", "request", etc.
    payload: Dict
    priority: int = 5       # 1 = highest, 10 = lowest
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent:
    """
    Base class for all CogniGuard agents.
    
    Every agent has:
    - A name and description
    - Status tracking
    - Action logging
    - Inter-agent communication
    - Performance metrics
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.last_active = None
        
        # Action log
        self.action_log: List[AgentAction] = []
        self.max_log_size = 1000
        
        # Message inbox
        self.inbox: List[AgentMessage] = []
        
        # Performance metrics
        self.metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_runtime_ms": 0.0,
            "threats_found": 0,
            "last_error": None,
        }
        
        # Reference to other agents (set by coordinator)
        self.coordinator = None
        self.peer_agents: Dict[str, 'BaseAgent'] = {}
        
        print(f"   🤖 Agent '{self.name}' initialized")
    
    # =========================================================================
    # ACTION TRACKING
    # =========================================================================
    
    def log_action(self, action_type: str, description: str,
                   data: Dict = None, success: bool = True,
                   error: str = None, duration_ms: float = 0.0):
        """Log an action taken by this agent"""
        
        action = AgentAction(
            agent_name=self.name,
            action_type=action_type,
            description=description,
            data=data,
            success=success,
            error=error,
            duration_ms=duration_ms
        )
        
        self.action_log.append(action)
        
        # Trim log if too large
        if len(self.action_log) > self.max_log_size:
            self.action_log = self.action_log[-self.max_log_size:]
        
        # Update metrics
        self.metrics["total_actions"] += 1
        self.metrics["total_runtime_ms"] += duration_ms
        
        if success:
            self.metrics["successful_actions"] += 1
        else:
            self.metrics["failed_actions"] += 1
            self.metrics["last_error"] = error
        
        self.last_active = datetime.now()
    
    def timed_action(self, action_type: str, description: str):
        """Context manager for timing actions"""
        return TimedAction(self, action_type, description)
    
    # =========================================================================
    # INTER-AGENT COMMUNICATION
    # =========================================================================
    
    def send_message(self, to_agent: str, message_type: str,
                     payload: Dict, priority: int = 5):
        """Send a message to another agent"""
        
        msg = AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        # If we have a reference to the target agent, deliver directly
        if to_agent in self.peer_agents:
            self.peer_agents[to_agent].receive_message(msg)
        elif self.coordinator:
            self.coordinator.route_message(msg)
        
        return msg
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        self.inbox.append(message)
        # Sort by priority (lower number = higher priority)
        self.inbox.sort(key=lambda m: m.priority)
    
    def get_messages(self, message_type: str = None) -> List[AgentMessage]:
        """Get messages from inbox, optionally filtered by type"""
        if message_type:
            messages = [m for m in self.inbox if m.message_type == message_type]
        else:
            messages = list(self.inbox)
        
        # Clear retrieved messages
        for msg in messages:
            self.inbox.remove(msg)
        
        return messages
    
    # =========================================================================
    # STATUS AND METRICS
    # =========================================================================
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "metrics": self.metrics.copy(),
            "inbox_size": len(self.inbox),
            "log_size": len(self.action_log),
        }
    
    def get_recent_actions(self, limit: int = 10) -> List[Dict]:
        """Get recent actions as dictionaries"""
        recent = self.action_log[-limit:]
        return [
            {
                "action_type": a.action_type,
                "description": a.description,
                "success": a.success,
                "duration_ms": a.duration_ms,
                "timestamp": a.timestamp.isoformat(),
                "error": a.error
            }
            for a in reversed(recent)
        ]
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_runtime_ms": 0.0,
            "threats_found": 0,
            "last_error": None,
        }


class TimedAction:
    """Context manager for timing agent actions"""
    
    def __init__(self, agent: BaseAgent, action_type: str, description: str):
        self.agent = agent
        self.action_type = action_type
        self.description = description
        self.start_time = None
        self.data = {}
        self.success = True
        self.error = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.agent.status = AgentStatus.RUNNING
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        
        if exc_type is not None:
            self.success = False
            self.error = str(exc_val)
        
        self.agent.log_action(
            action_type=self.action_type,
            description=self.description,
            data=self.data,
            success=self.success,
            error=self.error,
            duration_ms=duration
        )
        
        self.agent.status = AgentStatus.IDLE
        
        # Don't suppress exceptions
        return False