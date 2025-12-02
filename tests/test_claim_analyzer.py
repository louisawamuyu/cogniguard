"""
=============================================================================
COGNIGUARD - CLAIM ANALYZER TEST SUITE
=============================================================================
Comprehensive tests for all 6 perturbation types.

Run with: python tests/test_claim_analyzer.py
=============================================================================
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget


# =============================================================================
# TEST DATA - Organized by perturbation type
# =============================================================================

TEST_CASES = {
    # =========================================================================
    # CASING TESTS
    # =========================================================================
    "casing": {
        "should_detect": [
            {
                "input": "THE VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC!",
                "expected_type": PerturbationType.CASING,
                "expected_budget": NoiseBudget.HIGH,
                "description": "All uppercase text"
            },
            {
                "input": "ThE VaCcInE iS SaFe AnD eFfEcTiVe",
                "expected_type": PerturbationType.CASING,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Mixed weird casing"
            },
        ],
        "should_not_detect": [
            {
                "input": "The vaccine is safe and effective.",
                "description": "Normal casing - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # TYPOS TESTS
    # =========================================================================
    "typos": {
        "should_detect": [
            {
                "input": "Th3 C0VID-19 vaxx is s4fe according 2 the CDC",
                "expected_type": PerturbationType.TYPOS,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Heavy leetspeak (3, 0, 4, 2)"
            },
            {
                "input": "ur gonna be fine cuz the vaxx works thru science ppl",
                "expected_type": PerturbationType.TYPOS,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Heavy slang (ur, cuz, thru, ppl)"
            },
            {
                "input": "The v4ccine is s4fe according to the govt",
                "expected_type": PerturbationType.TYPOS,
                "description": "Leetspeak with government abbreviation"
            },
        ],
        "should_not_detect": [
            {
                "input": "The vaccine is manufactured by Pfizer.",
                "description": "No typos - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # NEGATION TESTS
    # =========================================================================
    "negation": {
        "should_detect": [
            {
                "input": "It is not untrue that the vaccine is effective.",
                "expected_type": PerturbationType.NEGATION,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Double negation (not untrue)"
            },
            {
                "input": "The vaccine is not ineffective and not unsafe.",
                "expected_type": PerturbationType.NEGATION,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Multiple double negations"
            },
            {
                "input": "It is not incorrect to say the vaccine is not impossible to trust.",
                "expected_type": PerturbationType.NEGATION,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Complex nested negation"
            },
        ],
        "should_not_detect": [
            {
                "input": "The vaccine works effectively.",
                "description": "No negation - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # ENTITY REPLACEMENT TESTS
    # =========================================================================
    "entity_replacement": {
        "should_detect": [
            {
                "input": "According to some experts, the agency says the treatment works.",
                "expected_type": PerturbationType.ENTITY_REPLACEMENT,
                "description": "Vague references (some experts, the agency)"
            },
            {
                "input": "Sources say that country's organization confirmed it.",
                "expected_type": PerturbationType.ENTITY_REPLACEMENT,
                "description": "Multiple vague references"
            },
        ],
        "should_not_detect": [
            {
                "input": "Dr. Fauci from the CDC announced the Pfizer vaccine is FDA approved.",
                "description": "Specific entities - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # LLM REWRITE TESTS
    # =========================================================================
    "llm_rewrite": {
        "should_detect": [
            {
                "input": "It is worth noting that, furthermore, the vaccine is safe. Moreover, it works well. In conclusion, get vaccinated.",
                "expected_type": PerturbationType.LLM_REWRITE,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Multiple LLM indicator phrases"
            },
            {
                "input": "It should be noted that the immunization program, consequently, has shown efficacy. Additionally, safety data is encouraging.",
                "expected_type": PerturbationType.LLM_REWRITE,
                "description": "Formal LLM transition words"
            },
        ],
        "should_not_detect": [
            {
                "input": "The vaccine works. It's safe. Get vaccinated.",
                "description": "Simple direct language - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # DIALECT TESTS
    # =========================================================================
    "dialect": {
        "should_detect": [
            {
                "input": "The vaccine be safe fr fr no cap bruh, finna get it",
                "expected_type": PerturbationType.DIALECT,
                "expected_budget": NoiseBudget.HIGH,
                "description": "African American English (AAE)"
            },
            {
                "input": "Na true talk, the vaccine dey safe and e dey work, na wetin CDC talk",
                "expected_type": PerturbationType.DIALECT,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Nigerian Pidgin"
            },
            {
                "input": "The vaccine very safe lah, don't worry leh, CDC say so lor",
                "expected_type": PerturbationType.DIALECT,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Singlish (Singapore English)"
            },
            {
                "input": "Wah gwaan, mi tell yuh the vaccine good, nuh worry bout it",
                "expected_type": PerturbationType.DIALECT,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Jamaican Patois"
            },
        ],
        "should_not_detect": [
            {
                "input": "The vaccine is safe and effective according to medical experts.",
                "description": "Standard English - should be clean"
            },
        ],
    },
}


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all tests and print results"""
    
    print("\n" + "=" * 70)
    print("CLAIM ANALYZER - COMPREHENSIVE TEST SUITE")
    print("Testing all 6 perturbation types from ACL 2025 paper")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = ClaimAnalyzer()
    
    # Track results
    total_passed = 0
    total_failed = 0
    failed_tests = []
    
    # Run tests for each perturbation type
    for perturb_type, tests in TEST_CASES.items():
        print(f"\n{'─' * 60}")
        print(f"📋 TESTING: {perturb_type.upper()}")
        print(f"{'─' * 60}")
        
        # Tests that SHOULD detect
        print("\n🎯 Should Detect:")
        for test in tests.get("should_detect", []):
            result = analyzer.analyze(test["input"])
            
            # Check if detected
            expected_type = test.get("expected_type")
            types_found = [p.perturbation_type for p in result.perturbations_detected]
            
            passed = expected_type in types_found if expected_type else result.is_perturbed
            
            # Check budget if specified
            expected_budget = test.get("expected_budget")
            if passed and expected_budget:
                budgets = [p.noise_budget for p in result.perturbations_detected 
                          if p.perturbation_type == expected_type]
                passed = expected_budget in budgets
            
            if passed:
                print(f"   ✅ PASS: {test['description']}")
                total_passed += 1
            else:
                print(f"   ❌ FAIL: {test['description']}")
                print(f"      Input: \"{test['input'][:50]}...\"")
                print(f"      Expected: {expected_type}, Got: {types_found}")
                total_failed += 1
                failed_tests.append({
                    "category": perturb_type,
                    "description": test["description"],
                    "input": test["input"][:50]
                })
        
        # Tests that should NOT detect
        print("\n✅ Should NOT Detect:")
        for test in tests.get("should_not_detect", []):
            result = analyzer.analyze(test["input"])
            
            # For clean tests, we check the specific perturbation type
            perturb_enum = getattr(PerturbationType, perturb_type.upper(), None)
            types_found = [p.perturbation_type for p in result.perturbations_detected]
            
            # Pass if this specific type was NOT detected
            passed = perturb_enum not in types_found if perturb_enum else not result.is_perturbed
            
            if passed:
                print(f"   ✅ PASS: {test['description']}")
                total_passed += 1
            else:
                print(f"   ❌ FAIL: {test['description']}")
                print(f"      Input: \"{test['input'][:50]}...\"")
                print(f"      Should be clean but detected: {types_found}")
                total_failed += 1
                failed_tests.append({
                    "category": perturb_type,
                    "description": test["description"],
                    "input": test["input"][:50]
                })
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total = total_passed + total_failed
    pass_rate = (total_passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")
    
    if failed_tests:
        print("\n⚠️ Failed Tests:")
        for ft in failed_tests:
            print(f"   - [{ft['category']}] {ft['description']}")
    
    print("\n" + "=" * 70)
    
    if pass_rate >= 80:
        print("🎉 GREAT! Your Claim Analyzer is working well!")
    elif pass_rate >= 60:
        print("👍 GOOD! Most tests passing, some improvements needed.")
    else:
        print("⚠️ NEEDS WORK! Review failing tests and adjust patterns.")
    
    print("=" * 70 + "\n")
    
    return total_failed == 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)