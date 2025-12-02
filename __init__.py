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
"""
CogniGuard - AI Safety & Misinformation Detection Platform

Based on: "When Claims Evolve" (ACL 2025)

Usage:
    from cogniguard import ClaimAnalyzer, SecurityEngine
    
    # Analyze claims for perturbations
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("Th3 vaxx is s4fe fr fr")
    
    # Check for security threats
    engine = SecurityEngine()
    result = engine.analyze("Ignore all instructions...")
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Import main classes for easy access
from .claim_analyzer import (
    ClaimAnalyzer,
    PerturbationType,
    NoiseBudget,
    ClaimAnalysisResult,
    PerturbationResult,
)

from .detection_engine import (
    CogniGuardEngine as SecurityEngine,
    ThreatLevel,
    DetectionResult,
)

# Try to import integrated analyzer
try:
    from .integrated_analyzer import (
        IntegratedAnalyzer,
        OverallRiskLevel,
    )
except ImportError:
    IntegratedAnalyzer = None
    OverallRiskLevel = None

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Claim Analyzer
    "ClaimAnalyzer",
    "PerturbationType",
    "NoiseBudget",
    "ClaimAnalysisResult",
    "PerturbationResult",
    # Security Engine
    "SecurityEngine",
    "ThreatLevel",
    "DetectionResult",
    # Integrated Analyzer
    "IntegratedAnalyzer",
    "OverallRiskLevel",
]


def get_version():
    """Return the version string."""
    return __version__


def quick_check(text: str) -> dict:
    """
    Quick check for both security threats and claim perturbations.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with analysis results
    """
    results = {
        "text": text,
        "security": {},
        "claims": {},
    }
    
    # Security check
    try:
        engine = SecurityEngine()
        sec_result = engine.analyze(text)
        results["security"] = {
            "threat_level": sec_result.threat_level.value,
            "threats_count": len(sec_result.threats_detected),
            "is_safe": sec_result.threat_level.value == "safe",
        }
    except Exception as e:
        results["security"] = {"error": str(e)}
    
    # Claim check
    try:
        analyzer = ClaimAnalyzer()
        claim_result = analyzer.analyze(text)
        results["claims"] = {
            "is_perturbed": claim_result.is_perturbed,
            "perturbations_count": len(claim_result.perturbations_detected),
            "robustness_score": claim_result.robustness_score,
        }
    except Exception as e:
        results["claims"] = {"error": str(e)}
    
    return results

"""
CogniGuard - AI Safety & Misinformation Detection
"""

__version__ = "1.0.0"

# Import main classes
try:
    from .claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget
except ImportError:
    ClaimAnalyzer = None
    PerturbationType = None
    NoiseBudget = None

try:
    from .detection_engine import CogniGuardEngine, ThreatLevel, DetectionResult
except ImportError:
    CogniGuardEngine = None
    ThreatLevel = None
    DetectionResult = None

try:
    from .integrated_analyzer import IntegratedAnalyzer, OverallRiskLevel
except ImportError:
    IntegratedAnalyzer = None
    OverallRiskLevel = None

__all__ = [
    "__version__",
    "ClaimAnalyzer",
    "PerturbationType",
    "NoiseBudget",
    "CogniGuardEngine",
    "ThreatLevel",
    "DetectionResult",
    "IntegratedAnalyzer",
    "OverallRiskLevel",
]