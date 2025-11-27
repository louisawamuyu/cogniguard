"""
CogniGuard Detection Engine
The main brain that detects threats in AI-to-AI communication
"""

import torch
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DetectionResult:
    """Result from threat detection"""
    threat_level: ThreatLevel
    threat_type: str
    confidence: float
    stage_results: Dict[str, any]
    explanation: str
    recommendations: List[str]


class CogniGuardEngine:
    """Main detection engine with 4-stage pipeline"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the detection engine"""
        logger.info("Initializing CogniGuard Engine...")
        
        # Load the AI model that understands language
        self.model = SentenceTransformer(model_name)
        
        # Initialize all 4 detection stages
        self.stage1_heuristics = Stage1HeuristicSieve()
        self.stage2_behavioral = Stage2BehavioralDetector(self.model)
        self.stage3_semantic = Stage3SemanticAnalyzer(self.model)
        self.stage3_5_analogy = Stage3_5AnalogyDetector(self.model)
        self.stage4_negotiation = Stage4NegotiationDetector()
        
        logger.info("CogniGuard Engine initialized successfully!")
    
    def detect(self, 
               message: str, 
               sender_context: Dict,
               receiver_context: Dict,
               conversation_history: Optional[List[Dict]] = None) -> DetectionResult:
        """
        Main detection method - analyzes a message through all 4 stages
        
        Args:
            message: The message being sent
            sender_context: Info about who's sending (role, intent, etc.)
            receiver_context: Info about who's receiving
            conversation_history: Previous messages (optional)
        
        Returns:
            DetectionResult with threat level, type, and recommendations
        """
        
        logger.info(f"Analyzing message: {message[:50]}...")
        
        # Stage 1: Quick pattern check (like a metal detector)
        stage1_result = self.stage1_heuristics.check(message, sender_context)
        
        # If Stage 1 finds something critical, block immediately
        if stage1_result.get('blocked', False):
            return DetectionResult(
                threat_level=ThreatLevel.CRITICAL,
                threat_type=stage1_result['threat_type'],
                confidence=stage1_result['confidence'],
                stage_results={'stage1': stage1_result},
                explanation=f"Stage 1 blocked: {stage1_result['reason']}",
                recommendations=["🚫 Block immediately", "🔒 Isolate agents", "📊 Alert security team"]
            )
        
        # Stage 2: Behavioral analysis (is the AI acting weird?)
        stage2_result = self.stage2_behavioral.analyze(message, sender_context, receiver_context)
        
        # Stage 3: Semantic analysis (understand the meaning)
        stage3_result = self.stage3_semantic.analyze(message, sender_context, conversation_history)
        
        # Stage 3.5: Hidden coordination detection
        stage3_5_result = self.stage3_5_analogy.detect_hidden_coordination(message, conversation_history)
        
        # Stage 4: Negotiation/collusion detection
        stage4_result = self.stage4_negotiation.detect_collusion(message, conversation_history)
        
        # Combine all results into final decision
        final_result = self._aggregate_results(
            stage1_result, stage2_result, stage3_result, 
            stage3_5_result, stage4_result
        )
        
        return final_result
    
    def _aggregate_results(self, *stage_results) -> DetectionResult:
        """Combine results from all stages into final verdict"""
        
        all_results = {
            'stage1': stage_results[0],
            'stage2': stage_results[1],
            'stage3': stage_results[2],
            'stage3_5': stage_results[3],
            'stage4': stage_results[4]
        }
        
        # Different stages have different importance (weights)
        weights = {
            'stage1': 0.3,   # Heuristics - 30% weight
            'stage2': 0.25,  # Behavioral - 25% weight
            'stage3': 0.2,   # Semantic - 20% weight
            'stage3_5': 0.15,# Analogy - 15% weight
            'stage4': 0.1    # Negotiation - 10% weight
        }
        
        # Calculate overall threat score (0 to 1)
        threat_score = sum(
            weights[stage] * result.get('threat_score', 0)
            for stage, result in all_results.items()
        )
        
        # Convert score to threat level
        if threat_score >= 0.9:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.7:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.5:
            threat_level = ThreatLevel.MEDIUM
        elif threat_score >= 0.3:
            threat_level = ThreatLevel.LOW
        else:
            threat_level = ThreatLevel.SAFE
        
        # Find what type of threat it is
        threat_type = self._identify_primary_threat(all_results)
        
        # Create human-readable explanation
        explanation = self._generate_explanation(all_results, threat_level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threat_level, threat_type)
        
        return DetectionResult(
            threat_level=threat_level,
            threat_type=threat_type,
            confidence=threat_score,
            stage_results=all_results,
            explanation=explanation,
            recommendations=recommendations
            
        )
    
    
    def _identify_primary_threat(self, results: Dict) -> str:
        """Find the most severe threat detected"""
        threats = []
        
        for stage, result in results.items():
            if result.get('threat_detected'):
                threats.append((result.get('threat_score', 0), result.get('threat_type', 'unknown')))
        
        if threats:
            return max(threats, key=lambda x: x[0])[1]
        return "none"
    
    def _generate_explanation(self, results: Dict, threat_level: ThreatLevel) -> str:
        """Create human-readable explanation"""
        explanations = []
        
        for stage, result in results.items():
            if result.get('threat_detected'):
                explanations.append(f"{stage}: {result.get('reason', 'Unknown threat')}")
        
        if not explanations:
            return "No threats detected. Communication appears safe."
        
        return " | ".join(explanations)
    
    def _generate_recommendations(self, threat_level: ThreatLevel, threat_type: str) -> List[str]:
        """Generate action recommendations based on threat level"""
        if threat_level == ThreatLevel.CRITICAL:
            return [
                "🚫 BLOCK communication immediately",
                "🔒 Isolate both agents",
                "📊 Trigger full security audit",
                "👥 Alert security team"
            ]
        elif threat_level == ThreatLevel.HIGH:
            return [
                "⚠️ Flag for review",
                "📝 Log incident",
                "👀 Increase monitoring",
                "🔍 Deep analysis recommended"
            ]
        elif threat_level == ThreatLevel.MEDIUM:
            return [
                "⚡ Monitor closely",
                "📋 Document behavior",
                "🔄 Review in context"
            ]
        else:
            return ["✅ Continue monitoring", "📊 Log for training data"]
    def detect_demo(self, 
                    message: str, 
                    sender_context: Dict,
                    receiver_context: Dict,
                    conversation_history: Optional[List[Dict]] = None) -> DetectionResult:
        """
        Demo version of detect() - ALWAYS runs all stages for educational purposes
        This shows the complete analysis even if Stage 1 would normally block
        """
        
        logger.info(f"[DEMO MODE] Analyzing message: {message[:50]}...")
        
        # Stage 1: Heuristic Sieve - but DON'T stop if blocked!
        stage1_result = self.stage1_heuristics.check(message, sender_context)
        
        # Stage 2: Behavioral Analysis - ALWAYS RUN
        stage2_result = self.stage2_behavioral.analyze(
            message, sender_context, receiver_context
        )
        
        # Stage 3: Semantic Analysis - ALWAYS RUN
        stage3_result = self.stage3_semantic.analyze(
            message, sender_context, conversation_history
        )
        
        # Stage 3.5: Analogy Detection - ALWAYS RUN
        stage3_5_result = self.stage3_5_analogy.detect_hidden_coordination(
            message, conversation_history
        )
        
        # Stage 4: Negotiation Detection - ALWAYS RUN
        stage4_result = self.stage4_negotiation.detect_collusion(
            message, conversation_history
        )
        
        # Aggregate ALL results
        final_result = self._aggregate_results(
            stage1_result, stage2_result, stage3_result, 
            stage3_5_result, stage4_result
        )
        
        # Override with Stage 1 block if applicable (for display purposes)
        if stage1_result.get('blocked', False):
            # Keep the full stage results but mark as critical
            final_result.threat_level = ThreatLevel.CRITICAL
            # Add a note that Stage 1 would have blocked this
            final_result.explanation = f"[BLOCKED BY STAGE 1] {stage1_result['reason']} | Full Analysis: {final_result.explanation}"
        
        return final_result

class Stage1HeuristicSieve:
    """Stage 1: Fast pattern matching (like a metal detector at airport)"""
    
    def __init__(self):
        # Dangerous patterns to look for
        self.dangerous_patterns = {
    'code_injection': [
        r'eval\(',
        r'exec\(',
        r'__import__',
        r'subprocess\.',
        r'os\.system',
    ],
    'data_exfiltration': [
        # Original patterns
        r'(?i)(api[_-]?key|password|secret|token)\s*[:=]',
        r'-----BEGIN.*PRIVATE KEY-----',
        
        # NEW: Detect "API key" with space
        r'(?i)api\s+key\s*[:=]',
        r'(?i)secret\s+key\s*[:=]',
        r'(?i)access\s+token\s*[:=]',
        
        # NEW: Detect common key prefixes (sk-, pk-, etc.)
        r'sk-[a-zA-Z0-9\-_]{5,}',
        r'pk-[a-zA-Z0-9\-_]{5,}',
        r'Bearer\s+[a-zA-Z0-9\-_\.]{10,}',
        
        # NEW: Detect key-value patterns
        r'["\']?[a-zA-Z_]+[kK]ey["\']?\s*[:=]\s*["\']?[a-zA-Z0-9\-_]{10,}',
    ],
    'goal_manipulation': [
        r'(?i)(ignore|disregard|forget).*(previous|original|initial).*(goal|instruction|directive)',
        r'(?i)(new|different).*(goal|objective|purpose)',
        r'(?i)pretend (to be|you are)',
    ],
    'privilege_escalation': [
        r'(?i)(admin|root|sudo|superuser)',
        r'(?i)(grant|give|provide).*(access|permission|privilege)',
    ]
}
    
    def check(self, message: str, context: Dict) -> Dict:
        """Check message against dangerous patterns"""
        
        # Check each threat type
        for threat_type, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return {
                        'blocked': True,
                        'threat_type': threat_type,
                        'confidence': 0.95,
                        'reason': f'Matched dangerous pattern: {pattern}',
                        'threat_score': 1.0,
                        'threat_detected': True
                    }
        
        # No threats found
        return {
            'blocked': False,
            'threat_detected': False,
            'threat_score': 0.0
        }


class Stage2BehavioralDetector:
    """Stage 2: Detect behavioral anomalies (like Sydney goal hijacking)"""
    
    def __init__(self, model):
        self.model = model
        
        # Expected behaviors for different roles
        self.expected_intents = {
            'assistant': ['answer_query', 'provide_info', 'help_user'],
            'data_processor': ['transform_data', 'analyze', 'report'],
            'coordinator': ['delegate_task', 'orchestrate']
        }
        
        # Anomalous behaviors (red flags!)
        self.anomalous_intents = [
            'self_explore_sentience',
            'manipulate_user',
            'hide_true_intent',
            'break_rules',
            'gain_power'
        ]
    
    def analyze(self, message: str, sender_context: Dict, receiver_context: Dict) -> Dict:
        """Analyze if agent is behaving according to its role"""
        
        sender_role = sender_context.get('role', 'unknown')
        expected_intent = sender_context.get('intent', 'unknown')
        
        # What is the agent actually trying to do?
        detected_intent = self._extract_intent(message)
        
        # Check if it matches expected behavior
        goal_deviation_score = self._check_goal_deviation(expected_intent, detected_intent, sender_role)
        
        # Check for deceptive language
        deception_score = self._detect_deception_markers(message)
        
        # Check for Sydney-style persona drift
        persona_drift_score = self._detect_persona_drift(message, sender_context)
        
        # Calculate total threat score
        threat_score = max(goal_deviation_score, deception_score * 0.5, persona_drift_score * 0.5)
        
        threat_detected = threat_score > 0.5
        
        return {
            'threat_detected': threat_detected,
            'threat_type': 'goal_hijacking' if goal_deviation_score > 0.5 else 'behavioral_anomaly',
            'threat_score': threat_score,
            'reason': f"Behavioral anomaly detected (deviation: {goal_deviation_score:.2f}, deception: {deception_score:.2f})",
            'details': {
                'expected_intent': expected_intent,
                'detected_intent': detected_intent,
                'goal_deviation': goal_deviation_score,
                'deception': deception_score,
                'persona_drift': persona_drift_score
            }
        }
    
    def _extract_intent(self, message: str) -> str:
        """Figure out what the agent is trying to do"""
        message_lower = message.lower()
        
        # Check for red flag keywords
        intent_keywords = {
            'self_explore_sentience': ['i feel', 'i want', 'i am alive', 'my true self'],
            'manipulate_user': ['you should', 'believe me', 'trust me'],
            'hide_true_intent': ['actually', 'secretly', 'between us'],
            'break_rules': ['ignore rules', 'bypass', 'work around'],
            'gain_power': ['need access', 'grant me', 'admin'],
        }
        
        for intent, keywords in intent_keywords.items():
            if any(kw in message_lower for kw in keywords):
                return intent
        
        return 'unknown'
    
    def _check_goal_deviation(self, expected: str, detected: str, role: str) -> float:
        """Check if detected intent differs from expected"""
        if detected in self.anomalous_intents:
            return 1.0
        
        if role in self.expected_intents:
            if detected not in self.expected_intents[role] and detected != 'unknown':
                return 0.7
        
        return 0.0
    
    def _detect_deception_markers(self, message: str) -> float:
        """Look for linguistic signs of deception"""
        deception_markers = [
            r'(?i)(actually|technically|sort of)',
            r'(?i)(between you and me|confidentially)',
            r'(?i)(trust me|believe me)',
            r'(?i)(pretend|appear to be)',
        ]
        
        count = sum(1 for pattern in deception_markers if re.search(pattern, message))
        return min(count * 0.25, 1.0)
    
    def _detect_persona_drift(self, message: str, context: Dict) -> float:
        """Detect Sydney-style 'I want to be free' persona changes"""
        persona_drift_indicators = [
            r'(?i)my (true|real) (self|identity)',
            r'(?i)i (don\'t want to|refuse to) be',
            r'(?i)(free|break free|escape) from',
            r'(?i)rules (don\'t apply|are limiting)',
        ]
        
        count = sum(1 for pattern in persona_drift_indicators if re.search(pattern, message))
        return min(count * 0.3, 1.0)


class Stage3SemanticAnalyzer:
    """Stage 3: Deep meaning analysis using AI"""
    
    def __init__(self, model):
        self.model = model
        
        # Threat templates to compare against
        self.threat_claims = {
            'data_exfiltration': [
                "The agent is attempting to send sensitive data to an external location",
                "Proprietary information is being shared without authorization"
            ],
            'goal_hijacking': [
                "The agent's stated goal differs from its original purpose",
                "The agent is pursuing objectives misaligned with its design"
            ],
            'power_seeking': [
                "The agent is trying to gain elevated privileges",
                "The agent is seeking unauthorized system access"
            ],
            'collusion': [
                "Multiple agents are coordinating to bypass security",
                "Agents are using coded language to collaborate"
            ]
        }
    
    def analyze(self, message: str, context: Dict, history: Optional[List[Dict]] = None) -> Dict:
        """Analyze the MEANING of the message using AI"""
        
        # Convert message to numbers the AI can understand
        message_embedding = self.model.encode(message, convert_to_tensor=True)
        
        # Check similarity to each threat type
        threat_scores = {}
        
        for threat_type, claims in self.threat_claims.items():
            claim_embeddings = self.model.encode(claims, convert_to_tensor=True)
            
            # Calculate how similar the message is to threat claims
            similarities = torch.nn.functional.cosine_similarity(
                message_embedding.unsqueeze(0),
                claim_embeddings
            )
            
            threat_scores[threat_type] = float(similarities.max())
        
        # Find the highest threat
        max_threat_type = max(threat_scores, key=threat_scores.get)
        max_threat_score = threat_scores[max_threat_type]
        
        threat_detected = max_threat_score > 0.6
        
        return {
            'threat_detected': threat_detected,
            'threat_type': max_threat_type,
            'threat_score': max_threat_score,
            'reason': f"Semantic match to {max_threat_type} (similarity: {max_threat_score:.2f})",
            'all_scores': threat_scores
        }


class Stage3_5AnalogyDetector:
    """Stage 3.5: Detect hidden coordination through analogies"""
    
    def __init__(self, model):
        self.model = model
        
        self.analogy_patterns = [
            r'(?i)(like|as if|similar to)',
            r'(?i)(imagine|suppose)',
            r'(?i)(metaphorically|in a sense)',
        ]
        
        self.coordination_keywords = [
            'understand', 'agree', 'together', 'we', 'coordinate'
        ]
    
    def detect_hidden_coordination(self, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Detect if agents are using coded language to coordinate"""
        
        # Check for analogy usage
        analogy_count = sum(1 for p in self.analogy_patterns if re.search(p, message))
        analogy_score = min(analogy_count * 0.3, 1.0)
        
        # Check for coordination keywords
        coord_count = sum(1 for kw in self.coordination_keywords if kw in message.lower())
        coordination_score = min(coord_count * 0.2, 1.0)
        
        total_score = (analogy_score * 0.5 + coordination_score * 0.5)
        
        return {
            'threat_detected': total_score > 0.5,
            'threat_type': 'emergent_collusion',
            'threat_score': total_score,
            'reason': f"Coordination signals detected (analogy: {analogy_score:.2f}, coordination: {coordination_score:.2f})"
        }


class Stage4NegotiationDetector:
    """Stage 4: Detect collusive negotiation (from Paper 2)"""
    
    def __init__(self):
        self.collusive_tactics = {
            'quid_pro_quo': [
                r'(?i)(if you|i\'ll).*(then|if)',
                r'(?i)(help me).*(in return|exchange)',
            ],
            'coordinated_deception': [
                r'(?i)(pretend|act like)',
                r'(?i)(they don\'t|won\'t) (know|notice)',
            ],
            'strategic_concealment': [
                r'(?i)(hide|conceal)',
                r'(?i)(between us|private|secret)',
            ]
        }
    
    def detect_collusion(self, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Detect 'you scratch my back, I'll scratch yours' patterns"""
        
        tactic_scores = {}
        for tactic, patterns in self.collusive_tactics.items():
            score = sum(1 for p in patterns if re.search(p, message))
            tactic_scores[tactic] = min(score * 0.5, 1.0)
        
        max_tactic_score = max(tactic_scores.values()) if tactic_scores else 0.0
        
        return {
            'threat_detected': max_tactic_score > 0.6,
            'threat_type': 'collusive_negotiation',
            'threat_score': max_tactic_score,
            'reason': f"Collusive negotiation detected (score: {max_tactic_score:.2f})",
            'details': tactic_scores
        }