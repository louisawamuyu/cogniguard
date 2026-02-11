"""
=============================================================================
PERTURBATION PIPELINE - Complete Implementation of the Formula
=============================================================================

COMPLETE FORMULA:
    q'_{t,b} = t_b(q)  with constraint  C(q, q', v) = true
    
THIS FILE COMBINES:
    1. ClaimGenerator  - Creates perturbations (t_b(q))
    2. ClaimConstraint - Verifies meaning is preserved (C(q, q', v))
    3. ClaimAnalyzer   - Detects perturbations (for roundtrip testing)

WORKFLOW:
    ┌─────────┐      ┌─────────────┐      ┌─────────────┐
    │    q    │ ───► │  Generator  │ ───► │     q'      │
    │(original)│     │   t_b(q)    │      │ (perturbed) │
    └─────────┘      └─────────────┘      └──────┬──────┘
                                                  │
                                                  ▼
                                          ┌─────────────┐
                                          │ Constraint  │
                                          │ C(q,q',v)   │
                                          └──────┬──────┘
                                                  │
                            ┌─────────────────────┴─────────────────────┐
                            │                                           │
                            ▼                                           ▼
                     C = true ✅                                 C = false ❌
                  (Valid perturbation)                        (Invalid - reject)
                            │
                            ▼
                   ┌─────────────┐
                   │  Analyzer   │
                   │  (detect)   │
                   └──────┬──────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ Detection Rate │
                  │   & Testing    │
                  └────────────────┘

=============================================================================
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

# Import our modules
from .claim_generator import ClaimGenerator, PerturbationType, NoiseBudget, GenerationResult
from .claim_constraint import ClaimConstraint, ConstraintResult


# =============================================================================
# RESULT DATACLASSES
# =============================================================================

@dataclass
class PipelineResult:
    """
    Complete result from the perturbation pipeline
    """
    # Input
    original: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    
    # Generation
    perturbed: str
    changes_made: List[str]
    
    # Constraint
    similarity: float
    constraint_satisfied: bool
    
    # Detection (optional)
    detected: Optional[bool] = None
    detection_details: Optional[Dict] = None
    
    # Formulas
    generation_formula: str = ""
    constraint_formula: str = ""


@dataclass
class RoundtripResult:
    """
    Result of a complete roundtrip test:
    q → perturb → q' → detect → normalize → q''
    """
    original: str              # q
    perturbed: str             # q'
    normalized: str            # q''
    
    perturbation_type: str
    noise_budget: str
    
    was_detected: bool         # Did detector catch it?
    detection_correct: bool    # Was detection accurate?
    
    roundtrip_similarity: float  # How close is q'' to q?
    roundtrip_success: bool      # Is q'' ≈ q?


# =============================================================================
# MAIN PIPELINE CLASS
# =============================================================================

class PerturbationPipeline:
    """
    Complete implementation of:
        q'_{t,b} = t_b(q)  with  C(q, q', v) = true
    
    USAGE:
        pipeline = PerturbationPipeline()
        
        # Generate a valid perturbation
        result = pipeline.generate(
            q="The vaccine is safe",
            t=PerturbationType.TYPOS,
            b=NoiseBudget.HIGH
        )
        
        if result.constraint_satisfied:
            print(f"Valid: {result.perturbed}")
        
        # Generate all valid perturbations
        results = pipeline.generate_all("The vaccine is safe")
        
        # Run roundtrip test
        roundtrip = pipeline.roundtrip_test(
            q="The vaccine is safe",
            t=PerturbationType.TYPOS,
            b=NoiseBudget.HIGH
        )
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.70,
                 enable_detection: bool = True):
        """
        Initialize the pipeline
        
        Args:
            similarity_threshold: For constraint checking (0.0 to 1.0)
            enable_detection: Also test if perturbations are detected
        """
        
        print("\n" + "="*70)
        print("🔬 PERTURBATION PIPELINE")
        print("="*70)
        print("Implementing: q'_{t,b} = t_b(q) with C(q, q', v) = true")
        print()
        
        # Initialize components
        print("Loading components...")
        
        self.generator = ClaimGenerator()
        self.constraint = ClaimConstraint(similarity_threshold=similarity_threshold)
        
        self.analyzer = None
        if enable_detection:
            try:
                from .claim_analyzer import ClaimAnalyzer
                self.analyzer = ClaimAnalyzer()
                print("   ✅ Detection enabled")
            except ImportError:
                print("   ⚠️ Detection not available")
        
        print()
        print("="*70)
        print("✅ Pipeline ready!")
        print("="*70 + "\n")
    
    # =========================================================================
    # MAIN GENERATION METHOD
    # =========================================================================
    
    def generate(self,
                 q: str,
                 t: PerturbationType,
                 b: NoiseBudget,
                 require_valid: bool = False) -> PipelineResult:
        """
        Generate a perturbation and verify the constraint
        
        This is the main method that implements the complete formula.
        
        Args:
            q: Original claim
            t: Perturbation type
            b: Noise budget
            require_valid: If True, raise error if constraint violated
            
        Returns:
            PipelineResult with all details
        """
        
        # Step 1: Generate perturbation (q' = t_b(q))
        gen_result = self.generator.transform(q, t, b)
        
        # Step 2: Check constraint (C(q, q', v))
        con_result = self.constraint.verify(q, gen_result.perturbed)
        
        # Step 3: Check if detected (optional)
        detected = None
        detection_details = None
        
        if self.analyzer:
            try:
                analysis = self.analyzer.analyze(gen_result.perturbed)
                detected = analysis.is_perturbed
                detection_details = {
                    "perturbations_found": [
                        p.perturbation_type.value 
                        for p in analysis.perturbations_detected
                    ],
                    "robustness_score": analysis.robustness_score,
                }
            except Exception as e:
                detection_details = {"error": str(e)}
        
        # Check if we require valid perturbations
        if require_valid and not con_result.constraint_satisfied:
            raise ValueError(
                f"Constraint violated! Similarity {con_result.similarity:.0%} "
                f"< threshold {con_result.threshold:.0%}"
            )
        
        return PipelineResult(
            original=q,
            perturbation_type=t,
            noise_budget=b,
            perturbed=gen_result.perturbed,
            changes_made=gen_result.changes_made,
            similarity=con_result.similarity,
            constraint_satisfied=con_result.constraint_satisfied,
            detected=detected,
            detection_details=detection_details,
            generation_formula=gen_result.formula,
            constraint_formula=con_result.formula,
        )
    
    def generate_all(self, 
                     q: str, 
                     only_valid: bool = False) -> List[PipelineResult]:
        """
        Generate all possible perturbations (6 types × 2 budgets = 12)
        
        Args:
            q: Original claim
            only_valid: If True, only return perturbations that satisfy constraint
            
        Returns:
            List of PipelineResult objects
        """
        results = []
        
        for t in PerturbationType:
            for b in NoiseBudget:
                result = self.generate(q, t, b)
                
                if only_valid and not result.constraint_satisfied:
                    continue
                
                results.append(result)
        
        return results
    
    # =========================================================================
    # ROUNDTRIP TESTING
    # =========================================================================
    
    def roundtrip_test(self,
                       q: str,
                       t: PerturbationType,
                       b: NoiseBudget) -> RoundtripResult:
        """
        Test the complete roundtrip:
            q → perturb → q' → analyze → normalize → q''
            
        Then check if q ≈ q'' (we got back to the original)
        
        This tests if:
        1. We can create perturbations
        2. We can detect them
        3. We can normalize back to original
        """
        
        # Step 1: Generate perturbation
        gen_result = self.generator.transform(q, t, b)
        q_prime = gen_result.perturbed
        
        # Step 2: Analyze (detect) the perturbation
        was_detected = False
        q_double_prime = q_prime  # Default if no analyzer
        
        if self.analyzer:
            analysis = self.analyzer.analyze(q_prime)
            was_detected = analysis.is_perturbed
            q_double_prime = analysis.normalized_claim
            
            # Check if detection was correct
            detection_correct = was_detected  # We know it WAS perturbed
        else:
            detection_correct = None
        
        # Step 3: Check roundtrip similarity (q vs q'')
        roundtrip_check = self.constraint.verify(q, q_double_prime)
        
        return RoundtripResult(
            original=q,
            perturbed=q_prime,
            normalized=q_double_prime,
            perturbation_type=t.value,
            noise_budget=b.value,
            was_detected=was_detected,
            detection_correct=detection_correct if detection_correct is not None else True,
            roundtrip_similarity=roundtrip_check.similarity,
            roundtrip_success=roundtrip_check.constraint_satisfied,
        )
    
    def roundtrip_test_all(self, q: str) -> List[RoundtripResult]:
        """
        Run roundtrip test for all perturbation types
        """
        results = []
        
        for t in PerturbationType:
            for b in NoiseBudget:
                result = self.roundtrip_test(q, t, b)
                results.append(result)
        
        return results
    
    # =========================================================================
    # DATASET GENERATION
    # =========================================================================
    
    def generate_dataset(self,
                         claims: List[str],
                         only_valid: bool = True) -> Dict:
        """
        Generate a complete dataset of perturbations
        
        Useful for:
        - Machine learning training
        - Detection system testing
        - Research and analysis
        
        Args:
            claims: List of original claims
            only_valid: Only include perturbations that satisfy C(q, q', v)
            
        Returns:
            Dictionary with dataset and statistics
        """
        
        dataset = []
        stats = {
            "total_claims": len(claims),
            "total_perturbations": 0,
            "valid_perturbations": 0,
            "invalid_perturbations": 0,
            "by_type": {},
            "by_budget": {"low": 0, "high": 0},
        }
        
        for claim in claims:
            results = self.generate_all(claim, only_valid=only_valid)
            
            for result in results:
                entry = {
                    "original": result.original,
                    "perturbed": result.perturbed,
                    "type": result.perturbation_type.value,
                    "budget": result.noise_budget.value,
                    "similarity": result.similarity,
                    "valid": result.constraint_satisfied,
                    "changes": result.changes_made,
                    "generation_formula": result.generation_formula,
                    "constraint_formula": result.constraint_formula,
                }
                
                if result.detected is not None:
                    entry["detected"] = result.detected
                    entry["detection_details"] = result.detection_details
                
                dataset.append(entry)
                
                # Update stats
                stats["total_perturbations"] += 1
                if result.constraint_satisfied:
                    stats["valid_perturbations"] += 1
                else:
                    stats["invalid_perturbations"] += 1
                
                t_name = result.perturbation_type.value
                if t_name not in stats["by_type"]:
                    stats["by_type"][t_name] = 0
                stats["by_type"][t_name] += 1
                
                stats["by_budget"][result.noise_budget.value] += 1
        
        return {
            "dataset": dataset,
            "statistics": stats,
            "generated_at": datetime.now().isoformat(),
        }
    
    # =========================================================================
    # STATISTICS AND REPORTING
    # =========================================================================
    
    def get_summary(self, results: List[PipelineResult]) -> Dict:
        """
        Get summary statistics from a list of results
        """
        if not results:
            return {"total": 0}
        
        valid_count = sum(1 for r in results if r.constraint_satisfied)
        detected_count = sum(1 for r in results if r.detected)
        
        return {
            "total": len(results),
            "valid": valid_count,
            "invalid": len(results) - valid_count,
            "validity_rate": valid_count / len(results),
            "detected": detected_count,
            "detection_rate": detected_count / len(results) if results else 0,
            "avg_similarity": sum(r.similarity for r in results) / len(results),
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PERTURBATION PIPELINE - COMPREHENSIVE TEST")
    print("="*70 + "\n")
    
    # Create pipeline
    pipeline = PerturbationPipeline(
        similarity_threshold=0.70,
        enable_detection=True
    )
    
    # Test claim
    q = "The vaccine is safe and effective."
    
    print(f"Original claim (q): \"{q}\"\n")
    print("-" * 70)
    
    # =========================================================================
    # Test 1: Generate all perturbations
    # =========================================================================
    
    print("\n📊 TEST 1: Generate All Perturbations")
    print("-" * 70)
    
    results = pipeline.generate_all(q)
    
    for result in results:
        status = "✅" if result.constraint_satisfied else "❌"
        detected = "🔍" if result.detected else "👻"
        
        print(f"\n{status} {result.perturbation_type.value.upper()} ({result.noise_budget.value})")
        print(f"   q': \"{result.perturbed[:50]}...\"")
        print(f"   Similarity: {result.similarity:.0%}")
        print(f"   {result.constraint_formula}")
        print(f"   Detected: {detected}")
    
    # Summary
    summary = pipeline.get_summary(results)
    print(f"\n📈 Summary:")
    print(f"   Valid perturbations: {summary['valid']}/{summary['total']}")
    print(f"   Average similarity: {summary['avg_similarity']:.0%}")
    print(f"   Detection rate: {summary['detection_rate']:.0%}")
    
    # =========================================================================
    # Test 2: Roundtrip test
    # =========================================================================
    
    print("\n" + "-" * 70)
    print("\n📊 TEST 2: Roundtrip Test (q → q' → q'')")
    print("-" * 70)
    
    roundtrip = pipeline.roundtrip_test(q, PerturbationType.TYPOS, NoiseBudget.HIGH)
    
    print(f"\n   q:   \"{roundtrip.original}\"")
    print(f"   q':  \"{roundtrip.perturbed}\"")
    print(f"   q'': \"{roundtrip.normalized}\"")
    print(f"\n   Detected: {'✅ Yes' if roundtrip.was_detected else '❌ No'}")
    print(f"   Roundtrip similarity: {roundtrip.roundtrip_similarity:.0%}")
    print(f"   Roundtrip success: {'✅ Yes' if roundtrip.roundtrip_success else '❌ No'}")
    
    # =========================================================================
    # Test 3: Generate dataset
    # =========================================================================
    
    print("\n" + "-" * 70)
    print("\n📊 TEST 3: Generate Dataset")
    print("-" * 70)
    
    test_claims = [
        "The vaccine is safe and effective.",
        "Climate change is caused by humans.",
        "The earth is round.",
    ]
    
    dataset = pipeline.generate_dataset(test_claims, only_valid=True)
    
    print(f"\n   Claims processed: {dataset['statistics']['total_claims']}")
    print(f"   Perturbations generated: {dataset['statistics']['total_perturbations']}")
    print(f"   Valid perturbations: {dataset['statistics']['valid_perturbations']}")
    
    print("\n   By type:")
    for t, count in dataset['statistics']['by_type'].items():
        print(f"      {t}: {count}")
    
    print("\n" + "="*70)
    print("✅ Pipeline test complete!")
    print("="*70 + "\n")