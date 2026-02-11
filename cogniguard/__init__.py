"""
CogniGuard - AI Security Detection Engine

This package provides multi-layered AI security threat detection.
"""
"""
CogniGuard - AI Security Platform
"""

__version__ = "1.0.0"
# Core detection (always try to load)
try:
    from .detection_engine import CogniGuardEngine, ThreatLevel, DetectionResult
except ImportError as e:
    print(f"Warning: Could not import detection_engine: {e}")
    CogniGuardEngine = None
    ThreatLevel = None
    DetectionResult = None

# Enhanced detection
try:
    from .enhanced_detection_engine import EnhancedCogniGuardEngine, EnhancedResult
except ImportError as e:
    print(f"Warning: Could not import enhanced_detection_engine: {e}")
    EnhancedCogniGuardEngine = None
    EnhancedResult = None

# Semantic engine (requires sentence-transformers)
try:
    from .semantic_engine import SemanticEngine, SemanticMatch
except ImportError as e:
    print(f"Note: Semantic engine not available: {e}")
    SemanticEngine = None
    SemanticMatch = None

# Conversation analyzer
try:
    from .conversation_analyzer import ConversationAnalyzer, ConversationPattern
except ImportError as e:
    print(f"Note: Conversation analyzer not available: {e}")
    ConversationAnalyzer = None
    ConversationPattern = None

# Threat learner
try:
    from .threat_learner import ThreatLearner, LearnedThreat
except ImportError as e:
    print(f"Note: Threat learner not available: {e}")
    ThreatLearner = None
    LearnedThreat = None

# Version
__version__ = "2.0.0"


"""
CogniGuard Core Module
"""

# Import with error handling
try:
    from .detection_engine import CogniGuardEngine, ThreatLevel, DetectionResult
except ImportError:
    CogniGuardEngine = None
    ThreatLevel = None
    DetectionResult = None

try:
    from .claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget
except ImportError:
    ClaimAnalyzer = None
    PerturbationType = None
    NoiseBudget = None

try:
    from .integrated_analyzer import IntegratedAnalyzer, OverallRiskLevel
except ImportError:
    IntegratedAnalyzer = None
    OverallRiskLevel = None

__all__ = [
    'CogniGuardEngine',
    'ThreatLevel',
    'DetectionResult',
    'ClaimAnalyzer',
    'PerturbationType',
    'NoiseBudget',
    'IntegratedAnalyzer',
    'OverallRiskLevel',
]

# Claim Generator (NEW!)
try:
    from .claim_generator import ClaimGenerator, GenerationResult
    from .claim_generator import PerturbationType as GenPerturbationType
    from .claim_generator import NoiseBudget as GenNoiseBudget
except ImportError as e:
    print(f"Note: Claim generator not available: {e}")
    ClaimGenerator = None

# Claim Constraint (NEW!)
try:
    from .claim_constraint import ClaimConstraint, ConstraintResult
except ImportError as e:
    print(f"Note: Claim constraint not available: {e}")
    ClaimConstraint = None

# Perturbation Pipeline (NEW!)
try:
    from .perturbation_pipeline import PerturbationPipeline, PipelineResult, RoundtripResult
except ImportError as e:
    print(f"Note: Perturbation pipeline not available: {e}")
    PerturbationPipeline = None