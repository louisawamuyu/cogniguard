"""CogniGuard Core Module - Enhanced"""

# Original components
from .detection_engine import CogniGuardEngine, ThreatLevel, DetectionResult
from .claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget

# New enhanced components
try:
    from .semantic_engine import SemanticEngine, SemanticMatch
except ImportError:
    SemanticEngine = None

try:
    from .conversation_analyzer import ConversationAnalyzer, ConversationPattern
except ImportError:
    ConversationAnalyzer = None

try:
    from .threat_learner import ThreatLearner
except ImportError:
    ThreatLearner = None

try:
    from .enhanced_detection_engine import EnhancedCogniGuardEngine, EnhancedResult
except ImportError:
    EnhancedCogniGuardEngine = None

__all__ = [
    # Original
    'CogniGuardEngine', 'ThreatLevel', 'DetectionResult',
    'ClaimAnalyzer', 'PerturbationType', 'NoiseBudget',
    # Enhanced
    'SemanticEngine', 'SemanticMatch',
    'ConversationAnalyzer', 'ConversationPattern',
    'ThreatLearner',
    'EnhancedCogniGuardEngine', 'EnhancedResult',
]
"""
CogniGuard Core Module - Enhanced Version

This is the main entry point for the CogniGuard package.
Import components from here in your application.
"""

# ═══════════════════════════════════════════════════════════════════════════
# ORIGINAL COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

from .detection_engine import (
    CogniGuardEngine, 
    ThreatLevel, 
    DetectionResult
)

try:
    from .claim_analyzer import (
        ClaimAnalyzer, 
        PerturbationType, 
        NoiseBudget,
        ClaimAnalysisResult,
        PerturbationResult
    )
    CLAIM_AVAILABLE = True
except ImportError:
    CLAIM_AVAILABLE = False
    ClaimAnalyzer = None
    PerturbationType = None
    NoiseBudget = None

try:
    from .integrated_analyzer import (
        IntegratedAnalyzer, 
        OverallRiskLevel,
        IntegratedResult
    )
    INTEGRATED_AVAILABLE = True
except ImportError:
    INTEGRATED_AVAILABLE = False
    IntegratedAnalyzer = None
    OverallRiskLevel = None

# ═══════════════════════════════════════════════════════════════════════════
# ENHANCED COMPONENTS (NEW!)
# ═══════════════════════════════════════════════════════════════════════════

try:
    from .semantic_engine import SemanticEngine, SemanticMatch
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SemanticEngine = None
    SemanticMatch = None

try:
    from .conversation_analyzer import (
        ConversationAnalyzer, 
        ConversationPattern,
        ConversationMessage
    )
    CONVERSATION_AVAILABLE = True
except ImportError:
    CONVERSATION_AVAILABLE = False
    ConversationAnalyzer = None
    ConversationPattern = None

try:
    from .threat_learner import ThreatLearner, LearnedThreat
    LEARNER_AVAILABLE = True
except ImportError:
    LEARNER_AVAILABLE = False
    ThreatLearner = None
    LearnedThreat = None

try:
    from .enhanced_detection_engine import (
        EnhancedCogniGuardEngine, 
        EnhancedResult
    )
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    EnhancedCogniGuardEngine = None
    EnhancedResult = None

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Original
    'CogniGuardEngine',
    'ThreatLevel',
    'DetectionResult',
    'ClaimAnalyzer',
    'PerturbationType',
    'NoiseBudget',
    'IntegratedAnalyzer',
    'OverallRiskLevel',
    
    # Enhanced (New!)
    'SemanticEngine',
    'SemanticMatch',
    'ConversationAnalyzer',
    'ConversationPattern',
    'ThreatLearner',
    'LearnedThreat',
    'EnhancedCogniGuardEngine',
    'EnhancedResult',
    
    # Availability flags
    'SEMANTIC_AVAILABLE',
    'CONVERSATION_AVAILABLE',
    'LEARNER_AVAILABLE',
    'ENHANCED_AVAILABLE',
]

# ═══════════════════════════════════════════════════════════════════════════
# VERSION INFO
# ═══════════════════════════════════════════════════════════════════════════

__version__ = "2.0.0"
__author__ = "Louisa Wamuyu Saburi"