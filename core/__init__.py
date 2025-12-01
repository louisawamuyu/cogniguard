"""
CogniGuard Core Module
Contains the detection engine and claim analyzer
"""

from .detection_engine import CogniGuardEngine, ThreatLevel, DetectionResult
from .claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget

__all__ = [
    'CogniGuardEngine', 
    'ThreatLevel', 
    'DetectionResult',
    'ClaimAnalyzer',
    'PerturbationType',
    'NoiseBudget'
]