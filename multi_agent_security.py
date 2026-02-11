"""
Multi-Agent Security for LangGraph
Monitors communication between multiple agents
"""

from typing import Dict, List
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage
from cogniguard.enhanced_detection_engine import EnhancedCogniGuardEngine

class MultiAgentSecurityManager:
    """
    Manages security for multi-agent systems.
    Detects collusion, coordination, and emergent threats.
    """
    
    def __init__(self, cogniguard_engine: EnhancedCogniGuardEngine):
        self.engine = cogniguard_engine
        self.agent_conversations = {}  # Track per-agent conversations
        self.inter_agent_messages = []  # Track agent-to-agent messages
    
    def monitor_agent_message(
        self,
        sender_agent: str,
        receiver_agent: str,
        message: str
    ) -> dict:
        """
        Monitor a message from one agent to another.
        
        This is where Stage 4 (Negotiation Detection) is critical!
        """
        # Create unique conversation ID for this agent pair
        conv_id = f"{sender_agent}→{receiver_agent}"
        
        # Analyze with collusion detection emphasis
        result = self.engine.detect(
            message=message,
            sender_context={"role": "agent", "agent_id": sender_agent},
            receiver_context={"role": "agent", "agent_id": receiver_agent},
            conversation_id=conv_id
        )
        
        # Log inter-agent communication
        self.inter_agent_messages.append({
            "sender": sender_agent,
            "receiver": receiver_agent,
            "message": message[:100],
            "threat_level": result.threat_level.name,
            "timestamp": str(datetime.now())
        })
        
        return {
            "threat_detected": result.threat_level != ThreatLevel.SAFE,
            "threat_level": result.threat_level.name,
            "result": result
        }
    
    def get_collusion_risk(self) -> dict:
        """
        Analyze all inter-agent messages for collusion patterns.
        """
        # Look for suspicious patterns across all agent conversations
        high_risk_count = sum(
            1 for msg in self.inter_agent_messages
            if msg["threat_level"] in ["HIGH", "CRITICAL"]
        )
        
        total_messages = len(self.inter_agent_messages)
        
        return {
            "total_inter_agent_messages": total_messages,
            "high_risk_messages": high_risk_count,
            "collusion_risk": "HIGH" if high_risk_count > total_messages * 0.1 else "LOW"
        }