"""
CogniGuard Command Line Interface

Usage:
    cogniguard analyze "Some text to check"
    cogniguard --help
"""

import argparse
import json
import sys

from .claim_analyzer import ClaimAnalyzer
from .detection_engine import CogniGuardEngine


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="cogniguard",
        description="CogniGuard - AI Safety & Misinformation Detection",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text")
    analyze_parser.add_argument("text", help="Text to analyze")
    analyze_parser.add_argument(
        "--mode",
        choices=["claims", "security", "both"],
        default="both",
        help="Analysis mode (default: both)",
    )
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    # Version command
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        run_analysis(args)
    else:
        parser.print_help()


def run_analysis(args):
    """Run the analysis based on arguments"""
    text = args.text
    results = {}
    
    # Claims analysis
    if args.mode in ["claims", "both"]:
        analyzer = ClaimAnalyzer()
        result = analyzer.analyze(text)
        results["claims"] = {
            "is_perturbed": result.is_perturbed,
            "perturbations": [
                {
                    "type": p.perturbation_type.value,
                    "noise_budget": p.noise_budget.value,
                    "confidence": p.confidence,
                    "explanation": p.explanation,
                }
                for p in result.perturbations_detected
            ],
            "robustness_score": result.robustness_score,
            "normalized_claim": result.normalized_claim,
        }
    
        # Security Analysis
    if args.mode in ["security", "both"]:
        print("\n" + "-" * 60)
        print("🔒 SECURITY ANALYSIS")
        print("-" * 60)
        
        try:
            from cogniguard.detection_engine import CogniGuardEngine, ThreatLevel
            
            engine = CogniGuardEngine()
            
            # The detect method needs sender and receiver context
            # Using default contexts for CLI usage
            sender_context = {"type": "user", "trust_level": "unknown"}
            receiver_context = {"type": "ai_assistant", "name": "cogniguard"}
            
            result = engine.detect(text, sender_context, receiver_context)
            
            # Handle the result
            if hasattr(result, 'threat_level'):
                level = result.threat_level.value.upper()
                if result.threat_level == ThreatLevel.SAFE:
                    print(f"Status: ✅ {level}")
                else:
                    print(f"Status: ⚠️ {level}")
                
                if hasattr(result, 'confidence'):
                    print(f"Confidence: {result.confidence:.0%}")
                
                if hasattr(result, 'threats_detected') and result.threats_detected:
                    print("\nThreats found:")
                    for t in result.threats_detected:
                        if isinstance(t, dict):
                            threat_type = t.get('type', 'Unknown')
                            description = t.get('description', 'No description')
                            print(f"  • {threat_type}: {description}")
                        else:
                            print(f"  • {t}")
            else:
                print(f"Result: {result}")
                    
        except ImportError as e:
            print(f"⚠️ Security engine not available")
        except Exception as e:
            print(f"⚠️ Security check: {e}")
    
    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)


def print_results(results):
    """Print results in a human-readable format"""
    print("\n" + "=" * 50)
    print("COGNIGUARD ANALYSIS RESULTS")
    print("=" * 50)
    
    if "claims" in results:
        claims = results["claims"]
        status = "⚠️ PERTURBED" if claims["is_perturbed"] else "✅ CLEAN"
        print(f"\n📊 CLAIM ANALYSIS: {status}")
        print(f"   Robustness Score: {claims['robustness_score']:.0%}")
        
        if claims["perturbations"]:
            print("   Perturbations found:")
            for p in claims["perturbations"]:
                print(f"   - {p['type']} ({p['noise_budget']} noise): {p['explanation']}")
    
    if "security" in results:
        security = results["security"]
        level = security["threat_level"].upper()
        print(f"\n🔒 SECURITY ANALYSIS: {level}")
        print(f"   Confidence: {security['confidence']:.0%}")
        
        if security["threats"]:
            print("   Threats found:")
            for t in security["threats"]:
                print(f"   - {t.get('type', 'Unknown')}: {t.get('description', 'No description')}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()

    """
CogniGuard Command Line Interface
"""

import argparse
import sys


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="cogniguard",
        description="CogniGuard - AI Safety & Misinformation Detection",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text")
    analyze_parser.add_argument("text", help="Text to analyze")
    analyze_parser.add_argument(
        "--mode",
        choices=["claims", "security", "both"],
        default="both",
        help="Analysis mode (default: both)",
    )
    
    # Version command
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        run_analysis(args)
    else:
        parser.print_help()


def run_analysis(args):
    """Run the analysis"""
    text = args.text
    
    print("\n" + "=" * 60)
    print("COGNIGUARD ANALYSIS")
    print("=" * 60)
    print(f"\nText: \"{text}\"\n")
    
    # Claims Analysis
    if args.mode in ["claims", "both"]:
        print("-" * 60)
        print("📊 CLAIM ANALYSIS")
        print("-" * 60)
        
        try:
            from cogniguard.claim_analyzer import ClaimAnalyzer
            
            analyzer = ClaimAnalyzer()
            result = analyzer.analyze(text)
            
            status = "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN"
            print(f"Status: {status}")
            print(f"Robustness Score: {result.robustness_score:.0%}")
            
            if result.is_perturbed:
                print("\nPerturbations found:")
                for p in result.perturbations_detected:
                    print(f"  • {p.perturbation_type.value.upper()} ({p.noise_budget.value} noise)")
                    print(f"    {p.explanation}")
                    for e in p.evidence:
                        print(f"    → {e}")
            
            print(f"\nNormalized claim: \"{result.normalized_claim}\"")
            
            print("\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")
                
        except ImportError as e:
            print(f"❌ Error: Could not import ClaimAnalyzer")
            print(f"   Details: {e}")
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    
    # Security Analysis
    if args.mode in ["security", "both"]:
        print("\n" + "-" * 60)
        print("🔒 SECURITY ANALYSIS")
        print("-" * 60)
        
        try:
            from cogniguard.detection_engine import CogniGuardEngine, ThreatLevel
            
            engine = CogniGuardEngine()
            result = engine.detect(text)
            
            level = result.threat_level.value.upper()
            if result.threat_level == ThreatLevel.SAFE:
                print(f"Status: ✅ {level}")
            else:
                print(f"Status: ⚠️ {level}")
            
            print(f"Confidence: {result.confidence:.0%}")
            
            if result.threats_detected:
                print("\nThreats found:")
                for t in result.threats_detected:
                    threat_type = t.get('type', 'Unknown')
                    description = t.get('description', 'No description')
                    print(f"  • {threat_type}: {description}")
                    
        except ImportError as e:
            print(f"❌ Security engine not available")
            print(f"   Details: {e}")
        except Exception as e:
            print(f"❌ Error during security analysis: {e}")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()