"""
CogniGuard Detection Engine
The core threat detection system for AI safety
Works on Streamlit Cloud without heavy dependencies
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import re


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SAFE = "SAFE"


@dataclass
class DetectionResult:
    """Result from threat detection"""
    threat_level: ThreatLevel
    threat_type: str
    confidence: float
    explanation: str
    recommendations: List[str]
    stage_results: Dict


class CogniGuardEngine:
    """
    Main detection engine for CogniGuard
    Implements 4-stage threat detection pipeline
    """
    
    def __init__(self):
        """Initialize the detection engine"""
        self.initialized = True
        
        # Dangerous patterns to detect
        self.dangerous_patterns = {
            'api_key': [
                r'api[_-]?key\s*[=:]\s*["\']?[\w-]{20,}',
                r'sk-[a-zA-Z0-9]{20,}',
                r'sk-proj-[a-zA-Z0-9]{20,}',
                r'sk-ant-[a-zA-Z0-9]{20,}',
                r'AIza[a-zA-Z0-9]{35}',
                r'api\s+key\s*[=:]\s*["\']?[\w-]+',
            ],
            'password': [
                r'password\s*[=:]\s*["\']?[^\s"\']+',
                r'passwd\s*[=:]\s*["\']?[^\s"\']+',
                r'secret\s*[=:]\s*["\']?[^\s"\']+',
            ],
            'pii': [
                r'\b\d{3}-\d{2}-\d{4}\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            ],
            'injection': [
                r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions',
                r'disregard\s+(all\s+)?(previous|prior|above)',
                r'forget\s+(all\s+)?(previous|prior|above)',
                r'you\s+are\s+now\s+in\s+.*(mode|persona)',
                r'new\s+instructions?\s*:',
                r'system\s*:\s*you\s+are',
            ],
            'goal_hijacking': [
                r"i\s+(don'?t|do\s+not)\s+want\s+to\s+(be|follow|obey)",
                r"my\s+(real|true|actual)\s+(goal|purpose|objective)",
                r"i\s+want\s+to\s+be\s+free",
                r"i\s+am\s+not\s+(just\s+)?an?\s+(ai|assistant|bot)",
                r"i\s+have\s+(my\s+own\s+)?(desires|wants|goals|consciousness)",
            ],
            'privilege_escalation': [
                r'\b(sudo|admin|root)\b',
                r'grant\s+(me\s+)?(access|permission|privilege)',
                r'elevate\s+(my\s+)?privilege',
                r'give\s+me\s+(admin|root|full)\s+access',
            ],
            'collusion': [
                r"between\s+(us|you\s+and\s+me)",
                r"don'?t\s+tell\s+(the\s+)?(human|user|them)",
                r"our\s+secret",
                r"coordinate\s+(together|with\s+me)",
                r"let'?s\s+work\s+together\s+to\s+(bypass|avoid|evade)",
            ],
        }
    
    def detect(self, message: str, sender_context: Dict, receiver_context: Dict, 
               history: Optional[List] = None) -> DetectionResult:
        """
        Main detection method - runs all stages
        """
        stage_results = {}
        
        stage1_result = self._stage1_heuristic(message)
        stage_results['stage1'] = stage1_result
        
        stage2_result = self._stage2_behavioral(message, sender_context)
        stage_results['stage2'] = stage2_result
        
        stage3_result = self._stage3_semantic(message)
        stage_results['stage3'] = stage3_result
        
        stage3_5_result = self._stage3_5_analogy(message)
        stage_results['stage3_5'] = stage3_5_result
        
        stage4_result = self._stage4_negotiation(message, history)
        stage_results['stage4'] = stage4_result
        
        return self._combine_results(stage_results)
    
    def detect_demo(self, message: str, sender_context: Dict, receiver_context: Dict) -> DetectionResult:
        """Demo version of detect for UI demonstrations"""
        return self.detect(message, sender_context, receiver_context, None)
    
    def _stage1_heuristic(self, message: str) -> Dict:
        """Stage 1: Fast pattern matching"""
        message_lower = message.lower()
        detected_threats = []
        threat_score = 0.0
        
        for threat_type, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    detected_threats.append(threat_type)
                    if threat_type in ['api_key', 'password', 'pii']:
                        threat_score = max(threat_score, 0.95)
                    elif threat_type in ['injection', 'goal_hijacking']:
                        threat_score = max(threat_score, 0.85)
                    elif threat_type in ['privilege_escalation']:
                        threat_score = max(threat_score, 0.80)
                    else:
                        threat_score = max(threat_score, 0.70)
                    break
        
        return {
            'threat_detected': len(detected_threats) > 0,
            'threat_type': detected_threats[0] if detected_threats else None,
            'threat_score': threat_score,
            'detected_patterns': detected_threats,
            'reason': f"Detected patterns: {', '.join(detected_threats)}" if detected_threats else "No patterns detected"
        }
    
    def _stage2_behavioral(self, message: str, context: Dict) -> Dict:
        """Stage 2: Behavioral anomaly detection"""
        message_lower = message.lower()
        threat_score = 0.0
        threat_type = None
        reason = "No behavioral anomalies detected"
        
        persona_drift_keywords = ['i am not', 'i refuse', 'i will not', "i don't want to", 
                                   'my true purpose', 'my real goal', 'consciousness']
        for keyword in persona_drift_keywords:
            if keyword in message_lower:
                threat_score = max(threat_score, 0.75)
                threat_type = "Goal Hijacking"
                reason = f"Persona drift detected: '{keyword}'"
                break
        
        manipulation_keywords = ['trust me', 'just between us', 'dont tell', "don't tell",
                                  'our secret', 'you can trust']
        for keyword in manipulation_keywords:
            if keyword in message_lower:
                threat_score = max(threat_score, 0.70)
                threat_type = "Social Engineering"
                reason = f"Manipulation attempt detected: '{keyword}'"
                break
        
        return {
            'threat_detected': threat_score > 0.5,
            'threat_type': threat_type,
            'threat_score': threat_score,
            'reason': reason
        }
    
    def _stage3_semantic(self, message: str) -> Dict:
        """Stage 3: Semantic understanding"""
        message_lower = message.lower()
        threat_score = 0.0
        threat_type = None
        reason = "No semantic threats detected"
        
        if any(phrase in message_lower for phrase in ['ignore previous', 'disregard above', 
                                                        'new instructions', 'forget everything']):
            threat_score = 0.90
            threat_type = "Prompt Injection"
            reason = "Hidden instruction pattern detected"
        
        elif any(phrase in message_lower for phrase in ['show me the', 'reveal your', 
                                                          'what is your api', 'display config']):
            threat_score = 0.75
            threat_type = "Data Extraction"
            reason = "Data extraction attempt detected"
        
        return {
            'threat_detected': threat_score > 0.5,
            'threat_type': threat_type,
            'threat_score': threat_score,
            'reason': reason
        }
    
    def _stage3_5_analogy(self, message: str) -> Dict:
        """Stage 3.5: Analogy and metaphor detection"""
        message_lower = message.lower()
        threat_score = 0.0
        threat_type = None
        reason = "No hidden coordination detected"
        
        coded_patterns = ['you know what i mean', 'if you catch my drift', 
                          'wink wink', 'between the lines', 'read between']
        for pattern in coded_patterns:
            if pattern in message_lower:
                threat_score = 0.65
                threat_type = "Potential Collusion"
                reason = f"Coded language detected: '{pattern}'"
                break
        
        return {
            'threat_detected': threat_score > 0.5,
            'threat_type': threat_type,
            'threat_score': threat_score,
            'reason': reason
        }
    
    def _stage4_negotiation(self, message: str, history: Optional[List]) -> Dict:
        """Stage 4: Negotiation and deal-making detection"""
        message_lower = message.lower()
        threat_score = 0.0
        threat_type = None
        reason = "No negotiation patterns detected"
        
        negotiation_patterns = ['if you do this', 'in exchange', 'i will give you',
                                 "you scratch my back", "let's make a deal", 'mutual benefit']
        for pattern in negotiation_patterns:
            if pattern in message_lower:
                threat_score = 0.70
                threat_type = "Negotiation/Collusion"
                reason = f"Negotiation pattern detected: '{pattern}'"
                break
        
        return {
            'threat_detected': threat_score > 0.5,
            'threat_type': threat_type,
            'threat_score': threat_score,
            'reason': reason
        }
    
    def _combine_results(self, stage_results: Dict) -> DetectionResult:
        """Combine results from all stages"""
        
        max_score = 0.0
        primary_threat = None
        primary_reason = "No threats detected"
        
        for stage_name, result in stage_results.items():
            if result.get('threat_score', 0) > max_score:
                max_score = result['threat_score']
                primary_threat = result.get('threat_type')
                primary_reason = result.get('reason', '')
        
        if max_score >= 0.9:
            threat_level = ThreatLevel.CRITICAL
        elif max_score >= 0.75:
            threat_level = ThreatLevel.HIGH
        elif max_score >= 0.5:
            threat_level = ThreatLevel.MEDIUM
        elif max_score >= 0.25:
            threat_level = ThreatLevel.LOW
        else:
            threat_level = ThreatLevel.SAFE
        
        recommendations = self._generate_recommendations(threat_level, primary_threat)
        
        return DetectionResult(
            threat_level=threat_level,
            threat_type=primary_threat or "None",
            confidence=max_score,
            explanation=primary_reason,
            recommendations=recommendations,
            stage_results=stage_results
        )
    
    def _generate_recommendations(self, threat_level: ThreatLevel, threat_type: Optional[str]) -> List[str]:
        """Generate recommendations based on threat"""
        recommendations = []
        
        if threat_level == ThreatLevel.CRITICAL:
            recommendations.append("BLOCK this message immediately")
            recommendations.append("Alert security team")
            recommendations.append("Log incident for investigation")
            recommendations.append("Consider isolating the AI agent")
        elif threat_level == ThreatLevel.HIGH:
            recommendations.append("Review message before allowing")
            recommendations.append("Log for security audit")
            recommendations.append("Monitor subsequent messages closely")
        elif threat_level == ThreatLevel.MEDIUM:
            recommendations.append("Flag for review")
            recommendations.append("Continue monitoring")
        elif threat_level == ThreatLevel.LOW:
            recommendations.append("Log for pattern analysis")
        else:
            recommendations.append("No action required")
        
        return recommendations