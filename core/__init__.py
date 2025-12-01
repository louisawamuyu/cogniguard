"""
CogniGuard Core Module
"""

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

__all__ = [
    'CogniGuardEngine', 
    'ThreatLevel', 
    'DetectionResult',
    'ClaimAnalyzer',
    'PerturbationType',
    'NoiseBudget',
]