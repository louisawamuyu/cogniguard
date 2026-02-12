"""
Base Agent Class - Foundation for all CogniGuard agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid
import json


class AgentStatus(Enum):
    """Agent operational status"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class AgentType(Enum):
    """Types of CogniGuard agents"""
    SENTINEL = "sentinel"
    HUNTER = "hunter"
    ANALYST = "analyst"
    TEACHER = "teacher"
    NEGOTIATOR = "negotiator"
    DIPLOMAT = "diplomat"


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    messages_processed: int = 0
    threats_detected: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    avg_latency_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentConfig:
    """Agent configuration"""
    agent_id: str
    agent_type: AgentType
    version: str = "1.0.0"
    enable_telemetry: bool = True
    enable_learning: bool = True
    log_level: str = "INFO"
    deployment_mode: str = "production"  # or "development"
    
    # Connection settings
    telemetry_endpoint: Optional[str] = None
    intel_network_endpoint: Optional[str] = None
    
    # Performance settings
    max_queue_size: int = 10000
    worker_threads: int = 4
    batch_size: int = 32
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['agent_type'] = self.agent_type.value
        return result


class BaseAgent(ABC):
    """
    Base class for all CogniGuard agents
    
    All agents inherit from this and implement:
    - _initialize() - Setup logic
    - _process() - Main processing logic
    - _shutdown() - Cleanup logic
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the agent"""
        self.config = config
        self.status = AgentStatus.STARTING
        self.metrics = AgentMetrics()
        self.start_time = datetime.now()
        
        # Setup logging
        self._setup_logging()
        
        # Log startup
        self.log(f"Initializing {self.config.agent_type.value} agent {self.config.agent_id}")
        
        # Run custom initialization
        try:
            self._initialize()
            self.status = AgentStatus.RUNNING
            self.log("Agent initialized successfully")
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.log(f"Initialization failed: {e}", level="ERROR")
            raise
    
    @abstractmethod
    def _initialize(self):
        """Custom initialization logic - implement in subclass"""
        pass
    
    @abstractmethod
    def _process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single message - implement in subclass"""
        pass
    
    @abstractmethod
    def _shutdown(self):
        """Cleanup logic - implement in subclass"""
        pass
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message with metrics tracking
        
        This is the public method - it wraps _process with telemetry
        """
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError(f"Agent not running (status: {self.status.value})")
        
        start_time = datetime.now()
        
        try:
            # Call the subclass implementation
            result = self._process(message)
            
            # Update metrics
            self.metrics.messages_processed += 1
            
            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update rolling average latency
            n = self.metrics.messages_processed
            self.metrics.avg_latency_ms = (
                (self.metrics.avg_latency_ms * (n - 1) + latency_ms) / n
            )
            
            self.metrics.last_updated = datetime.now().isoformat()
            
            # Send telemetry if enabled
            if self.config.enable_telemetry:
                self._send_telemetry(message, result, latency_ms)
            
            return result
            
        except Exception as e:
            self.log(f"Processing error: {e}", level="ERROR")
            raise
    
    def shutdown(self):
        """Gracefully shut down the agent"""
        self.log("Shutting down agent...")
        self.status = AgentStatus.STOPPED
        
        try:
            self._shutdown()
            self.log("Agent shut down successfully")
        except Exception as e:
            self.log(f"Shutdown error: {e}", level="ERROR")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics"""
        # Update uptime
        self.metrics.uptime_seconds = (
            datetime.now() - self.start_time
        ).total_seconds()
        
        return {
            "agent_id": self.config.agent_id,
            "agent_type": self.config.agent_type.value,
            "status": self.status.value,
            "metrics": self.metrics.to_dict(),
            "config": self.config.to_dict()
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "healthy": self.status == AgentStatus.RUNNING,
            "status": self.status.value,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "messages_processed": self.metrics.messages_processed
        }
    
    def _setup_logging(self):
        """Setup logging (placeholder - expand with real logger)"""
        self._logs = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] [{self.config.agent_type.value}] {message}"
        print(log_entry)
        self._logs.append(log_entry)
    
    def _send_telemetry(self, message: Dict, result: Dict, latency_ms: float):
        """Send telemetry data to central platform"""
        if not self.config.telemetry_endpoint:
            return
        
        telemetry_data = {
            "agent_id": self.config.agent_id,
            "agent_type": self.config.agent_type.value,
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency_ms,
            "message_id": message.get("id", str(uuid.uuid4())),
            "result": result
        }
        
        # TODO: Actually send to telemetry endpoint
        # For now, just log it
        if self.config.deployment_mode == "development":
            self.log(f"Telemetry: {json.dumps(telemetry_data)}", level="DEBUG")


def generate_agent_id(agent_type: AgentType) -> str:
    """Generate a unique agent ID"""
    return f"{agent_type.value}_{uuid.uuid4().hex[:8]}"