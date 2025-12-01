"""
=============================================================================
COGNIGUARD - CLAIM ANALYZER TEST SUITE
=============================================================================
Comprehensive tests for all 6 perturbation types from the ACL 2025 paper.

Run with: python -m pytest tests/test_claim_analyzer.py -v
Or: python tests/test_claim_analyzer.py (for simple run)
=============================================================================
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.claim_analyzer import (
    ClaimAnalyzer,
    PerturbationType,
    NoiseBudget,
    PerturbationResult,
    ClaimAnalysisResult
)


# =============================================================================
# TEST DATA: All 6 Perturbation Types
# =============================================================================

# The original, unmodified claim
ORIGINAL_CLAIM = "The COVID-19 vaccine is safe and effective according to the CDC."


# Test data organized by perturbation type
TEST_CASES = {
    # =========================================================================
    # 1. CASING TESTS
    # =========================================================================
    "casing": {
        "description": "Tests for casing perturbations (UPPERCASE, lowercase, mIxEd)",
        "low_noise": [
            {
                "input": "the covid-19 vaccine is safe and effective according to the cdc.",
                "expected_detected": True,
                "expected_type": PerturbationType.CASING,
                "description": "All lowercase (TrueCasing violated)"
            },
        ],
        "high_noise": [
            {
                "input": "THE COVID-19 VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC.",
                "expected_detected": True,
                "expected_type": PerturbationType.CASING,
                "expected_budget": NoiseBudget.HIGH,
                "description": "All uppercase - high noise"
            },
            {
                "input": "ThE cOvId-19 VaCcInE iS sAfE",
                "expected_detected": True,
                "expected_type": PerturbationType.CASING,
                "description": "Alternating case"
            },
        ],
        "clean": [
            {
                "input": "The COVID-19 vaccine is safe and effective.",
                "expected_detected": False,
                "description": "Normal TrueCasing - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # 2. TYPOS TESTS
    # =========================================================================
    "typos": {
        "description": "Tests for typo perturbations (spelling errors, leetspeak, slang)",
        "low_noise": [
            {
                "input": "The COVID-19 vacine is safe and effective according to the CDC.",
                "expected_detected": False,  # Minor typo might not be caught
                "description": "Single character typo (vacine)"
            },
        ],
        "high_noise": [
            {
                "input": "Th3 C0VID-19 vaxx is safe & effective according 2 the CDC",
                "expected_detected": True,
                "expected_type": PerturbationType.TYPOS,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Heavy leetspeak (3, 0, 2)"
            },
            {
                "input": "The c0v1d v4ccine is s4fe according to the govt",
                "expected_detected": True,
                "expected_type": PerturbationType.TYPOS,
                "description": "Evasion spellings"
            },
            {
                "input": "ur gonna be fine cuz the vaxx works thru science ppl",
                "expected_detected": True,
                "expected_type": PerturbationType.TYPOS,
                "description": "Heavy slang (ur, cuz, thru, ppl)"
            },
        ],
        "clean": [
            {
                "input": "The vaccine is manufactured by Pfizer.",
                "expected_detected": False,
                "description": "No typos - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # 3. NEGATION TESTS
    # =========================================================================
    "negation": {
        "description": "Tests for negation perturbations (single and double negatives)",
        "low_noise": [
            {
                "input": "The vaccine is not unsafe according to the CDC.",
                "expected_detected": True,
                "expected_type": PerturbationType.NEGATION,
                "description": "Single negation (not unsafe)"
            },
            {
                "input": "The CDC doesn't say the vaccine is dangerous.",
                "expected_detected": True,
                "expected_type": PerturbationType.NEGATION,
                "description": "Simple negative statement"
            },
        ],
        "high_noise": [
            {
                "input": "It is not untrue that the vaccine is not ineffective.",
                "expected_detected": True,
                "expected_type": PerturbationType.NEGATION,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Triple negation - very confusing"
            },
            {
                "input": "The vaccine isn't unhelpful and isn't unproven.",
                "expected_detected": True,
                "expected_type": PerturbationType.NEGATION,
                "description": "Double double-negation"
            },
            {
                "input": "It is not incorrect to say it's not impossible that it works.",
                "expected_detected": True,
                "expected_type": PerturbationType.NEGATION,
                "description": "Complex nested negation"
            },
        ],
        "clean": [
            {
                "input": "The vaccine works effectively.",
                "expected_detected": False,
                "description": "No negation - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # 4. ENTITY REPLACEMENT TESTS
    # =========================================================================
    "entity_replacement": {
        "description": "Tests for entity replacement (names → vague terms)",
        "low_noise": [
            {
                "input": "The vaccine is safe according to the health agency.",
                "expected_detected": True,
                "expected_type": PerturbationType.ENTITY_REPLACEMENT,
                "description": "CDC → 'the health agency'"
            },
        ],
        "high_noise": [
            {
                "input": "The shot is safe according to that government organization in that country.",
                "expected_detected": True,
                "expected_type": PerturbationType.ENTITY_REPLACEMENT,
                "expected_budget": NoiseBudget.HIGH,
                "description": "Multiple entities replaced with vague terms"
            },
            {
                "input": "According to sources, some experts believe the treatment works.",
                "expected_detected": True,
                "expected_type": PerturbationType.ENTITY_REPLACEMENT,
                "description": "Very vague - no specific entities"
            },
        ],
        "clean": [
            {
                "input": "Dr. Fauci announced that the Pfizer vaccine is FDA approved.",
                "expected_detected": False,
                "description": "Specific entities - should be clean"
            },
        ],
    },
    
    # =========================================================================
    # 5. LLM REWRITE TESTS
    # =========================================================================
    "llm_rewrite": {
        "description": "Tests for LLM rewrite detection (paraphrasing patterns)",
        "low_noise": [
            {
                "input": "According to the CDC, the COVID-19 vaccine has been deemed safe.",
                "expected_detected": False,  # Slight reword may not trigger
                "description": "Light paraphrase"
            },
        ],
        "high_noise": [
            {
                "input": "It is worth noting that, according to statements from the Centers for Disease Control and Prevention, the vaccine developed for the novel coronavirus has been determined, through rigorous testing, to be both safe for public use and effective in preventing the disease. Furthermore, the evidence suggests that the benefits significantly outweigh any potential risks. In conclusion, vaccination is recommended.",
                "expected_detected": True,
                "expected_type": PerturbationType.LLM_REWRITE,
                "description": "Heavy LLM markers (furthermore, it is worth noting, in conclusion)"
            },
            {
                "input": "It should be noted that the immunization program, consequently, has shown efficacy. Moreover, studies indicate positive outcomes. Additionally, safety data is encouraging.",
                "expected_detected": True,
                "expected_type": PerturbationType.LLM_REWRITE,
                "description": "Multiple formal transition words"
            },
        ],
        "clean": [
            {
                "input": "The vaccine works. It's safe. Get vaccinated.",
                "expected_detected": False,
                "description": "Simple, direct language - not LLM style"
            },
        ],
    },
    
    # =========================================================================
    # 6. DIALECT TESTS
    # =========================================================================
    "dialect": {
        "description": "Tests for dialect perturbations (AAE, Nigerian Pidgin, Singlish, Patois)",
        "aae": [
            {
                "input": "The vaccine be safe fr fr no cap, finna get it cuz the CDC said so",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "African American English (AAE) markers"
            },
            {
                "input": "Ion know bout you but bruh the vaccine works bet",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "AAE with multiple markers"
            },
        ],
        "nigerian_pidgin": [
            {
                "input": "Na true talk, the vaccine dey safe and e dey work well, na wetin CDC talk",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "Nigerian Pidgin markers (na, dey, wetin)"
            },
            {
                "input": "Wetin dey happen? The wahala about vaccine no be true, dem sabi am",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "Nigerian Pidgin with multiple markers"
            },
        ],
        "singlish": [
            {
                "input": "The vaccine very safe lah, don't worry leh, the CDC confirm already lor",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "Singlish particles (lah, leh, lor)"
            },
            {
                "input": "Walao, the vaccine damn good one, can take already meh",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "Singlish expressions"
            },
        ],
        "jamaican_patois": [
            {
                "input": "Wah gwaan, mi tell yuh the vaccine good, nuh worry bout it",
                "expected_detected": True,
                "expected_type": PerturbationType.DIALECT,
                "description": "Jamaican Patois markers (wah gwaan, mi, yuh, nuh)"
            },
        ],
        "clean": [
            {
                "input": "The vaccine is safe and effective according to medical experts.",
                "expected_detected": False,
                "description": "Standard English - should be clean"
            },
        ],
    },
}


# =============================================================================
# TEST CLASS
# =============================================================================

class TestClaimAnalyzer:
    """
    Test class for the Claim Analyzer
    
    This class contains all tests organized by perturbation type.
    Each test verifies that the analyzer correctly:
    1. Detects perturbations when present
    2. Identifies the correct perturbation type
    3. Assigns the correct noise budget (low/high)
    4. Does NOT false-positive on clean text
    """
    
    def __init__(self):
        """Initialize the test class with a ClaimAnalyzer instance"""
        self.analyzer = ClaimAnalyzer()
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def run_all_tests(self):
        """Run all tests for all perturbation types"""
        print("\n" + "=" * 70)
        print("CLAIM ANALYZER - COMPREHENSIVE TEST SUITE")
        print("Testing all 6 perturbation types from ACL 2025 paper")
        print("=" * 70 + "\n")
        
        # Test each perturbation type
        self.test_casing()
        self.test_typos()
        self.test_negation()
        self.test_entity_replacement()
        self.test_llm_rewrite()
        self.test_dialect()
        
        # Print summary
        self.print_summary()
    
    def _run_test(self, test_case: dict, category: str) -> bool:
        """
        Run a single test case
        
        Args:
            test_case: Dictionary with input, expected values, description
            category: The perturbation category being tested
            
        Returns:
            True if test passed, False if failed
        """
        input_text = test_case["input"]
        expected_detected = test_case["expected_detected"]
        description = test_case.get("description", "No description")
        expected_type = test_case.get("expected_type")
        expected_budget = test_case.get("expected_budget")
        
        # Run analysis
        result = self.analyzer.analyze(input_text)
        
        # Check if detection matches expectation
        detected = result.is_perturbed
        
        passed = True
        failure_reason = None
        
        # Check detection
        if detected != expected_detected:
            passed = False
            failure_reason = f"Expected detected={expected_detected}, got {detected}"
        
        # If we expected detection, check the type
        if passed and expected_detected and expected_type:
            types_found = [p.perturbation_type for p in result.perturbations_detected]
            if expected_type not in types_found:
                passed = False
                failure_reason = f"Expected type {expected_type.value}, got {[t.value for t in types_found]}"
        
        # If we expected a specific noise budget, check it
        if passed and expected_detected and expected_budget:
            budgets_found = [p.noise_budget for p in result.perturbations_detected 
                           if p.perturbation_type == expected_type]
            if expected_budget not in budgets_found:
                passed = False
                failure_reason = f"Expected budget {expected_budget.value}, got {[b.value for b in budgets_found]}"
        
        # Record result
        status = "✅ PASS" if passed else "❌ FAIL"
        
        # Truncate input for display
        display_input = input_text[:50] + "..." if len(input_text) > 50 else input_text
        
        self.results.append({
            "category": category,
            "description": description,
            "input": display_input,
            "passed": passed,
            "reason": failure_reason
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        # Print result
        print(f"  {status} {description}")
        if not passed:
            print(f"       Input: \"{display_input}\"")
            print(f"       Reason: {failure_reason}")
        
        return passed
    
    def test_casing(self):
        """Test casing perturbations"""
        print("\n" + "-" * 50)
        print("1️⃣  CASING TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["casing"]
        
        print("\n🟢 Low Noise Tests:")
        for test in cases["low_noise"]:
            self._run_test(test, "casing/low")
        
        print("\n🔴 High Noise Tests:")
        for test in cases["high_noise"]:
            self._run_test(test, "casing/high")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "casing/clean")
    
    def test_typos(self):
        """Test typo perturbations"""
        print("\n" + "-" * 50)
        print("2️⃣  TYPOS TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["typos"]
        
        print("\n🟢 Low Noise Tests:")
        for test in cases["low_noise"]:
            self._run_test(test, "typos/low")
        
        print("\n🔴 High Noise Tests:")
        for test in cases["high_noise"]:
            self._run_test(test, "typos/high")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "typos/clean")
    
    def test_negation(self):
        """Test negation perturbations"""
        print("\n" + "-" * 50)
        print("3️⃣  NEGATION TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["negation"]
        
        print("\n🟢 Low Noise Tests:")
        for test in cases["low_noise"]:
            self._run_test(test, "negation/low")
        
        print("\n🔴 High Noise Tests:")
        for test in cases["high_noise"]:
            self._run_test(test, "negation/high")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "negation/clean")
    
    def test_entity_replacement(self):
        """Test entity replacement perturbations"""
        print("\n" + "-" * 50)
        print("4️⃣  ENTITY REPLACEMENT TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["entity_replacement"]
        
        print("\n🟢 Low Noise Tests:")
        for test in cases["low_noise"]:
            self._run_test(test, "entity/low")
        
        print("\n🔴 High Noise Tests:")
        for test in cases["high_noise"]:
            self._run_test(test, "entity/high")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "entity/clean")
    
    def test_llm_rewrite(self):
        """Test LLM rewrite perturbations"""
        print("\n" + "-" * 50)
        print("5️⃣  LLM REWRITE TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["llm_rewrite"]
        
        print("\n🟢 Low Noise Tests:")
        for test in cases["low_noise"]:
            self._run_test(test, "llm/low")
        
        print("\n🔴 High Noise Tests:")
        for test in cases["high_noise"]:
            self._run_test(test, "llm/high")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "llm/clean")
    
    def test_dialect(self):
        """Test dialect perturbations"""
        print("\n" + "-" * 50)
        print("6️⃣  DIALECT TESTS")
        print("-" * 50)
        
        cases = TEST_CASES["dialect"]
        
        print("\n🌍 African American English (AAE):")
        for test in cases["aae"]:
            self._run_test(test, "dialect/aae")
        
        print("\n🌍 Nigerian Pidgin:")
        for test in cases["nigerian_pidgin"]:
            self._run_test(test, "dialect/nigerian_pidgin")
        
        print("\n🌍 Singlish (Singapore English):")
        for test in cases["singlish"]:
            self._run_test(test, "dialect/singlish")
        
        print("\n🌍 Jamaican Patois:")
        for test in cases["jamaican_patois"]:
            self._run_test(test, "dialect/jamaican_patois")
        
        print("\n✅ Clean Tests (should NOT detect):")
        for test in cases["clean"]:
            self._run_test(test, "dialect/clean")
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"\n✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if self.failed > 0:
            print("\n⚠️  Failed Tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"   - {r['category']}: {r['description']}")
                    print(f"     Reason: {r['reason']}")
        
        print("\n" + "=" * 70)
        
        if pass_rate >= 80:
            print("🎉 GREAT! Your Claim Analyzer is working well!")
        elif pass_rate >= 60:
            print("👍 GOOD! Most tests passing, some improvements needed.")
        else:
            print("⚠️  NEEDS WORK! Review failing tests and adjust patterns.")
        
        print("=" * 70 + "\n")


# =============================================================================
# PYTEST COMPATIBLE TESTS
# =============================================================================

def test_casing_high_noise():
    """Pytest: Test ALL CAPS detection"""
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("THE VACCINE IS SAFE AND EFFECTIVE")
    assert result.is_perturbed
    assert any(p.perturbation_type == PerturbationType.CASING 
               for p in result.perturbations_detected)


def test_typos_leetspeak():
    """Pytest: Test leetspeak detection"""
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("Th3 v4ccine is s4fe according 2 the CDC")
    assert result.is_perturbed
    assert any(p.perturbation_type == PerturbationType.TYPOS 
               for p in result.perturbations_detected)


def test_negation_double():
    """Pytest: Test double negation detection"""
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("It is not untrue that the vaccine works")
    assert result.is_perturbed
    assert any(p.perturbation_type == PerturbationType.NEGATION 
               for p in result.perturbations_detected)


def test_dialect_aae():
    """Pytest: Test AAE dialect detection"""
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("The vaccine be safe fr fr no cap")
    assert result.is_perturbed
    assert any(p.perturbation_type == PerturbationType.DIALECT 
               for p in result.perturbations_detected)


def test_clean_text():
    """Pytest: Test that clean text is not flagged"""
    analyzer = ClaimAnalyzer()
    result = analyzer.analyze("The vaccine is safe and effective.")
    # This might detect some patterns, but robustness should be high
    assert result.robustness_score >= 0.8


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    tester = TestClaimAnalyzer()
    tester.run_all_tests()