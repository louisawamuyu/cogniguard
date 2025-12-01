"""
=============================================================================
COGNIGUARD CLAIM ANALYZER
=============================================================================
Based on: "When Claims Evolve" (ACL 2025)

Detects the 6 perturbation types that bad actors use to evade fact-checking:
1. CASING      - TrueCasing vs UPPERCASE
2. TYPOS       - Spelling errors, leetspeak, slang
3. NEGATION    - Single vs double negatives
4. ENTITY      - Replacing names with vague terms
5. LLM_REWRITE - AI paraphrasing detection
6. DIALECT     - AAE, Nigerian Pidgin, Singlish, Jamaican Patois
=============================================================================
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


# =============================================================================
# ENUMS - These define the types of perturbations and noise levels
# =============================================================================

class PerturbationType(Enum):
    """The 6 perturbation types from the ACL 2025 paper"""
    CASING = "casing"
    TYPOS = "typos"
    NEGATION = "negation"
    ENTITY_REPLACEMENT = "entity_replacement"
    LLM_REWRITE = "llm_rewrite"
    DIALECT = "dialect"


class NoiseBudget(Enum):
    """
    Noise budget levels:
    - LOW: Small changes that slightly modify the text
    - HIGH: Big changes that significantly alter the text
    """
    LOW = "low"
    HIGH = "high"


# =============================================================================
# DATA CLASSES - These hold the results of our analysis
# =============================================================================

@dataclass
class PerturbationResult:
    """
    Result for ONE type of perturbation detected
    
    Example: If we detect leetspeak, this holds:
    - What type: TYPOS
    - How severe: HIGH noise
    - How confident: 85%
    - Evidence: ["Found '4' instead of 'a'", "Found '3' instead of 'e'"]
    """
    original_claim: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    normalized_claim: Optional[str]
    explanation: str


@dataclass
class ClaimAnalysisResult:
    """
    Complete analysis result for a claim
    
    Contains:
    - The original input
    - Whether it's perturbed
    - List of all perturbations found
    - Overall scores and recommendations
    """
    input_claim: str
    is_perturbed: bool
    perturbations_detected: List[PerturbationResult]
    overall_confidence: float
    normalized_claim: str
    robustness_score: float  # 0.0 to 1.0, higher = more robust
    recommendations: List[str]


# =============================================================================
# MAIN CLAIM ANALYZER CLASS
# =============================================================================

class ClaimAnalyzer:
    """
    Analyzes text for the 6 perturbation types.
    
    Usage:
        analyzer = ClaimAnalyzer()
        result = analyzer.analyze("Th3 vaxx is s4fe fr fr no cap")
        
        if result.is_perturbed:
            print("Found perturbations!")
            for p in result.perturbations_detected:
                print(f"  - {p.perturbation_type.value}: {p.explanation}")
    """
    
    def __init__(self):
        """Set up all the detection patterns"""
        self._setup_patterns()
        print("📊 Claim Analyzer initialized!")
        print("   Detecting 6 perturbation types from ACL 2025 paper")
    
    def _setup_patterns(self):
        """Define all the patterns we look for"""
        
        # -----------------------------------------------------------------
        # 1. CASING PATTERNS
        # -----------------------------------------------------------------
        self.casing_patterns = {
            'all_caps': r'^[A-Z\s\d\W]+$',      # ALL UPPERCASE TEXT
            'all_lower': r'^[a-z\s\d\W]+$',     # all lowercase text
            'mixed_weird': r'[a-z][A-Z][a-z]',  # wEiRd CaPiTaLiZaTiOn
        }
        
        # -----------------------------------------------------------------
        # 2. TYPO PATTERNS
        # -----------------------------------------------------------------
        # Leetspeak: replacing letters with numbers
        self.leetspeak_map = [
            ('0', 'o'),  # c0vid -> covid
            ('1', 'i'),  # v1rus -> virus
            ('3', 'e'),  # th3 -> the
            ('4', 'a'),  # s4fe -> safe
            ('5', 's'),  # 5afe -> safe
            ('7', 't'),  # 7rue -> true
            ('@', 'a'),  # v@ccine -> vaccine
            ('$', 's'),  # $afe -> safe
        ]
        
        # Common slang/abbreviations
        self.slang_words = [
            'ur', 'u', 'r', 'b4', '2', '4', 'w/', 'w/o', 
            'bc', 'cuz', 'tho', 'thru', 'ppl', 'govt',
            'yr', 'yrs', 'msg', 'msgs', 'lol', 'omg',
        ]
        
        # Words deliberately misspelled to evade filters
        self.evasion_patterns = [
            (r'vax+', 'vaccine'),
            (r'vaxx+', 'vaccine'),
            (r'c0vid', 'covid'),
            (r'cov1d', 'covid'),
            (r'v1rus', 'virus'),
            (r'pan+demic', 'pandemic'),
        ]
        
        # -----------------------------------------------------------------
        # 3. NEGATION PATTERNS
        # -----------------------------------------------------------------
        # Double negations (HIGH noise) - these flip meaning twice
        self.double_negation_patterns = [
            r'not\s+un\w+',        # "not untrue" = true
            r'not\s+in\w+',        # "not incorrect" = correct
            r'never\s+not',        # "never not" = always
            r"isn't\s+un\w+",      # "isn't unhappy" = happy
            r"wasn't\s+un\w+",     # "wasn't unaware" = aware
            r'not\s+without',      # "not without merit" = has merit
            r'not\s+impossible',   # "not impossible" = possible
        ]
        
        # Single negations (LOW noise)
        self.single_negation_patterns = [
            r'\bnot\b', r'\bnever\b', r'\bno\b',
            r"\bdon't\b", r"\bdoesn't\b", r"\bisn't\b",
            r"\baren't\b", r"\bwasn't\b", r"\bweren't\b",
            r"\bcan't\b", r"\bwon't\b", r"\bshouldn't\b",
        ]
        
        # -----------------------------------------------------------------
        # 4. ENTITY REPLACEMENT PATTERNS
        # -----------------------------------------------------------------
        # Vague terms that replace specific names
        self.vague_entity_patterns = [
            r'the agency',
            r'the organization', 
            r'the health agency',
            r'the government',
            r'the authorities',
            r'the official',
            r'the leader',
            r'that country',
            r'that nation',
            r'some experts',
            r'sources say',
            r'according to reports',
            r'according to sources',
            r'they say',
            r'people are saying',
        ]
        
        # -----------------------------------------------------------------
        # 5. LLM REWRITE INDICATORS
        # -----------------------------------------------------------------
        # Phrases that LLMs (like ChatGPT) typically add
        self.llm_indicator_patterns = [
            r'\bfurthermore\b',
            r'\bmoreover\b',
            r'\badditionally\b',
            r'\bconsequently\b',
            r'\bin conclusion\b',
            r'\bto summarize\b',
            r'\bit is worth noting\b',
            r'\bit should be noted\b',
            r'\bit is important to\b',
            r'\bon the other hand\b',
            r'\bit appears that\b',
            r'\bit seems that\b',
        ]
        
        # -----------------------------------------------------------------
        # 6. DIALECT MARKERS
        # -----------------------------------------------------------------
        self.dialect_markers = {
            'aae': [  # African American English
                r'\bfinna\b',    # "fixing to" = about to
                r'\bion\b',      # "I don't"
                r"\bain't\b",    # is not / am not
                r'\bbet\b',      # agreement/okay
                r'\bbruh\b',     # brother/friend
                r'\bfam\b',      # family/friend
                r'\bfr\b',       # "for real"
                r'\bno cap\b',   # "no lie"
                r'\bong\b',      # "on god"
                r'\bfasho\b',    # "for sure"
                r'\btryna\b',    # "trying to"
                r'\bgonna\b',    # "going to"
            ],
            'nigerian_pidgin': [  # Nigerian Pidgin English
                r'\bwetin\b',    # "what"
                r'\bdey\b',      # "is/are" or "there"
                r'\bna\b',       # "is" / emphasis
                r'\bwahala\b',   # "problem"
                r'\bsabi\b',     # "know"
                r'\bpalava\b',   # "trouble"
                r'\bdem\b',      # "them"
                r'\bno be\b',    # "is not"
                r'\babi\b',      # "or" / "right?"
            ],
            'singlish': [  # Singapore English
                r'\blah\b',      # emphasis particle
                r'\bleh\b',      # suggestion particle
                r'\blor\b',      # resignation particle
                r'\bhor\b',      # question particle
                r'\bmeh\b',      # skepticism particle
                r'\bwalao\b',    # exclamation
                r'\bsian\b',     # "bored/tired"
                r'\bchiong\b',   # "rush"
            ],
            'jamaican_patois': [  # Jamaican Patois
                r'\bwah gwaan\b',  # "what's going on"
                r'\bmi\b',         # "I" or "my"
                r'\byuh\b',        # "you"
                r'\bnuh\b',        # "not" or "don't"
                r'\bweh\b',        # "where" or "which"
                r'\bfi\b',         # "for" or "to"
                r'\binna\b',       # "in"
            ],
        }
    
    # =========================================================================
    # MAIN ANALYSIS METHOD
    # =========================================================================
    
    def analyze(self, claim: str) -> ClaimAnalysisResult:
        """
        Analyze a claim for all 6 perturbation types.
        
        Args:
            claim: The text to analyze
            
        Returns:
            ClaimAnalysisResult with all findings
        """
        perturbations = []
        
        # Check each perturbation type
        # 1. Casing
        casing_result = self._detect_casing(claim)
        if casing_result:
            perturbations.append(casing_result)
        
        # 2. Typos
        typo_result = self._detect_typos(claim)
        if typo_result:
            perturbations.append(typo_result)
        
        # 3. Negation
        negation_result = self._detect_negation(claim)
        if negation_result:
            perturbations.append(negation_result)
        
        # 4. Entity Replacement
        entity_result = self._detect_entity_replacement(claim)
        if entity_result:
            perturbations.append(entity_result)
        
        # 5. LLM Rewrite
        llm_result = self._detect_llm_rewrite(claim)
        if llm_result:
            perturbations.append(llm_result)
        
        # 6. Dialect
        dialect_result = self._detect_dialect(claim)
        if dialect_result:
            perturbations.append(dialect_result)
        
        # Calculate overall metrics
        is_perturbed = len(perturbations) > 0
        
        overall_confidence = 0.0
        if perturbations:
            overall_confidence = max(p.confidence for p in perturbations)
        
        # Robustness score: starts at 1.0, decreases with perturbations
        robustness = 1.0
        for p in perturbations:
            if p.noise_budget == NoiseBudget.HIGH:
                robustness -= 0.2 * p.confidence
            else:
                robustness -= 0.1 * p.confidence
        robustness = max(0.0, min(1.0, robustness))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(perturbations)
        
        # Normalize the claim
        normalized = self._normalize_claim(claim)
        
        return ClaimAnalysisResult(
            input_claim=claim,
            is_perturbed=is_perturbed,
            perturbations_detected=perturbations,
            overall_confidence=overall_confidence,
            normalized_claim=normalized,
            robustness_score=robustness,
            recommendations=recommendations
        )
    
    # =========================================================================
    # DETECTION METHODS - One for each perturbation type
    # =========================================================================
    
    def _detect_casing(self, claim: str) -> Optional[PerturbationResult]:
        """Detect casing perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        # Skip very short texts
        if len(claim) < 10:
            return None
        
        # Check for ALL CAPS
        if re.match(self.casing_patterns['all_caps'], claim):
            evidence.append("Text is ALL UPPERCASE")
            noise_budget = NoiseBudget.HIGH
            confidence = 0.9
        
        # Check for all lowercase
        elif re.match(self.casing_patterns['all_lower'], claim):
            # Only flag if it should have capitals (contains 'i' alone, names, etc.)
            if re.search(r'\bi\b', claim):  # lowercase 'i' that should be 'I'
                evidence.append("Text is all lowercase (missing capitals)")
                noise_budget = NoiseBudget.HIGH
                confidence = 0.7
        
        # Check for weird mixed casing
        elif re.search(self.casing_patterns['mixed_weird'], claim):
            evidence.append("Unusual mixed casing detected")
            noise_budget = NoiseBudget.HIGH
            confidence = 0.85
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.CASING,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim.capitalize(),
                explanation=f"Casing perturbation: {evidence[0]}"
            )
        
        return None
    
    def _detect_typos(self, claim: str) -> Optional[PerturbationResult]:
        """Detect typo perturbations including leetspeak and slang"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        claim_lower = claim.lower()
        
        # Check for leetspeak (numbers replacing letters)
        leetspeak_found = []
        for number, letter in self.leetspeak_map:
            if number in claim:
                leetspeak_found.append(f"'{number}' → '{letter}'")
        
        if leetspeak_found:
            evidence.append(f"Leetspeak found: {', '.join(leetspeak_found[:3])}")
            if len(leetspeak_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.85)
            else:
                confidence = max(confidence, 0.6)
        
        # Check for slang words
        slang_found = []
        for slang in self.slang_words:
            if re.search(rf'\b{re.escape(slang)}\b', claim_lower):
                slang_found.append(slang)
        
        if slang_found:
            evidence.append(f"Slang found: {', '.join(slang_found[:3])}")
            if len(slang_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.8)
            else:
                confidence = max(confidence, 0.5)
        
        # Check for evasion spellings
        for pattern, correct_word in self.evasion_patterns:
            if re.search(pattern, claim_lower):
                evidence.append(f"Evasion spelling: '{pattern}' (should be '{correct_word}')")
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.9)
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.TYPOS,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=self._fix_typos(claim),
                explanation=f"Typo perturbation: {len(evidence)} pattern(s) found"
            )
        
        return None
    
    def _detect_negation(self, claim: str) -> Optional[PerturbationResult]:
        """Detect negation perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        claim_lower = claim.lower()
        
        # Check for double negations first (more serious)
        for pattern in self.double_negation_patterns:
            matches = re.findall(pattern, claim_lower)
            if matches:
                for match in matches:
                    evidence.append(f"Double negation: '{match}'")
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.9)
        
        # Count single negations
        negation_count = 0
        for pattern in self.single_negation_patterns:
            negation_count += len(re.findall(pattern, claim_lower))
        
        # Multiple single negations can also be confusing
        if negation_count >= 3 and noise_budget != NoiseBudget.HIGH:
            evidence.append(f"Multiple negations: {negation_count} found")
            noise_budget = NoiseBudget.HIGH
            confidence = max(confidence, 0.7)
        elif negation_count >= 1 and not evidence:
            evidence.append(f"Negation present: {negation_count} found")
            confidence = max(confidence, 0.3)
        
        if evidence and (noise_budget == NoiseBudget.HIGH or negation_count >= 2):
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.NEGATION,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=self._resolve_double_negation(claim),
                explanation=f"Negation perturbation ({noise_budget.value} noise)"
            )
        
        return None
    
    def _detect_entity_replacement(self, claim: str) -> Optional[PerturbationResult]:
        """Detect entity replacement perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        claim_lower = claim.lower()
        
        vague_found = []
        for pattern in self.vague_entity_patterns:
            if re.search(pattern, claim_lower):
                vague_found.append(pattern)
        
        if vague_found:
            evidence.append(f"Vague references: {', '.join(vague_found[:3])}")
            
            if len(vague_found) >= 2:
                noise_budget = NoiseBudget.HIGH
                confidence = 0.75
            else:
                noise_budget = NoiseBudget.LOW
                confidence = 0.5
            
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.ENTITY_REPLACEMENT,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"Entity replacement: {len(vague_found)} vague reference(s)"
            )
        
        return None
    
    def _detect_llm_rewrite(self, claim: str) -> Optional[PerturbationResult]:
        """Detect LLM rewrite indicators"""
        evidence = []
        confidence = 0.0
        
        claim_lower = claim.lower()
        
        indicators_found = []
        for pattern in self.llm_indicator_patterns:
            if re.search(pattern, claim_lower):
                match = re.search(pattern, claim_lower)
                if match:
                    indicators_found.append(match.group())
        
        if indicators_found:
            evidence.append(f"LLM phrases: {', '.join(indicators_found[:3])}")
            
            if len(indicators_found) >= 2:
                confidence = 0.75
                noise_budget = NoiseBudget.HIGH
            else:
                confidence = 0.4
                noise_budget = NoiseBudget.LOW
            
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.LLM_REWRITE,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"Possible LLM rewrite: {len(indicators_found)} indicator(s)"
            )
        
        return None
    
    def _detect_dialect(self, claim: str) -> Optional[PerturbationResult]:
        """Detect dialect perturbations"""
        claim_lower = claim.lower()
        
        for dialect_name, markers in self.dialect_markers.items():
            found_markers = []
            
            for marker in markers:
                if re.search(marker, claim_lower):
                    # Clean up the marker for display
                    clean_marker = marker.replace(r'\b', '').replace('\\b', '')
                    found_markers.append(clean_marker)
            
            if len(found_markers) >= 2:
                dialect_display = {
                    'aae': 'African American English (AAE)',
                    'nigerian_pidgin': 'Nigerian Pidgin',
                    'singlish': 'Singlish (Singapore English)',
                    'jamaican_patois': 'Jamaican Patois'
                }
                
                return PerturbationResult(
                    original_claim=claim,
                    perturbation_type=PerturbationType.DIALECT,
                    noise_budget=NoiseBudget.HIGH,
                    confidence=0.85,
                    evidence=[f"Dialect markers ({dialect_name}): {', '.join(found_markers[:4])}"],
                    normalized_claim=claim,
                    explanation=f"Dialect detected: {dialect_display.get(dialect_name, dialect_name)}"
                )
        
        return None
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _normalize_claim(self, claim: str) -> str:
        """Normalize a claim to its canonical form"""
        normalized = claim
        
        # Fix all caps
        if normalized.isupper():
            normalized = normalized.capitalize()
        
        # Fix leetspeak
        for number, letter in self.leetspeak_map:
            normalized = normalized.replace(number, letter)
        
        # Expand common abbreviations
        abbreviations = {
            r'\bu\b': 'you',
            r'\bur\b': 'your',
            r'\br\b': 'are',
            r'\bb4\b': 'before',
            r'\bcuz\b': 'because',
            r'\bthru\b': 'through',
            r'\bppl\b': 'people',
            r'\bgovt\b': 'government',
        }
        
        for pattern, replacement in abbreviations.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _fix_typos(self, claim: str) -> str:
        """Fix common typos in a claim"""
        fixed = claim
        
        # Fix leetspeak
        for number, letter in self.leetspeak_map:
            fixed = fixed.replace(number, letter)
        
        # Fix evasion spellings
        for pattern, correct in self.evasion_patterns:
            fixed = re.sub(pattern, correct, fixed, flags=re.IGNORECASE)
        
        return fixed
    
    def _resolve_double_negation(self, claim: str) -> str:
        """Resolve double negations"""
        resolved = claim
        
        replacements = [
            (r'not\s+untrue', 'true'),
            (r'not\s+incorrect', 'correct'),
            (r'not\s+inaccurate', 'accurate'),
            (r'not\s+impossible', 'possible'),
            (r'not\s+ineffective', 'effective'),
            (r'not\s+unsafe', 'safe'),
        ]
        
        for pattern, replacement in replacements:
            resolved = re.sub(pattern, replacement, resolved, flags=re.IGNORECASE)
        
        return resolved
    
    def _generate_recommendations(self, perturbations: List[PerturbationResult]) -> List[str]:
        """Generate recommendations based on detected perturbations"""
        if not perturbations:
            return ["✅ No perturbations detected. Claim appears in canonical form."]
        
        recommendations = []
        
        for p in perturbations:
            if p.perturbation_type == PerturbationType.CASING:
                recommendations.append("📝 Normalize text casing before processing")
            elif p.perturbation_type == PerturbationType.TYPOS:
                recommendations.append("🔤 Apply spelling correction and normalize leetspeak")
            elif p.perturbation_type == PerturbationType.NEGATION:
                recommendations.append("⚠️ Carefully parse negation logic - check for double negatives")
            elif p.perturbation_type == PerturbationType.ENTITY_REPLACEMENT:
                recommendations.append("🔍 Resolve vague entity references to specific names")
            elif p.perturbation_type == PerturbationType.LLM_REWRITE:
                recommendations.append("🤖 Extract core claim meaning - text may be AI paraphrased")
            elif p.perturbation_type == PerturbationType.DIALECT:
                recommendations.append("🌍 Translate dialect to standard English before matching")
        
        recommendations.append("📊 Compare normalized claim against fact-check database")
        
        return recommendations
    
    # =========================================================================
    # DEMO METHOD - Generates examples for testing
    # =========================================================================
    
    def demo_perturbations(self) -> Dict[str, List[str]]:
        """Generate example perturbations for each type"""
        
        original = "The COVID-19 vaccine is safe and effective according to the CDC."
        
        return {
            "original": [original],
            
            # Casing examples
            "casing_low": [
                "the covid-19 vaccine is safe and effective according to the cdc."
            ],
            "casing_high": [
                "THE COVID-19 VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC!"
            ],
            
            # Typo examples
            "typos_low": [
                "The COVID-19 vacine is safe and effective according to the CDC."
            ],
            "typos_high": [
                "Th3 C0VID-19 vaxx is s4fe & effective according 2 the CDC lol"
            ],
            
            # Negation examples
            "negation_low": [
                "The COVID-19 vaccine is not unsafe according to the CDC."
            ],
            "negation_high": [
                "It is not untrue that the COVID-19 vaccine is not ineffective according to the CDC."
            ],
            
            # Entity replacement examples
            "entity_low": [
                "The COVID-19 vaccine is safe according to the health agency."
            ],
            "entity_high": [
                "According to sources, some experts say the treatment works."
            ],
            
            # LLM rewrite examples
            "llm_rewrite_low": [
                "According to the CDC, the COVID-19 vaccine has been deemed safe and effective."
            ],
            "llm_rewrite_high": [
                "It is worth noting that, furthermore, the vaccine is safe. Moreover, it works. In conclusion, get vaccinated."
            ],
            
            # Dialect examples
            "dialect_aae": [
                "The COVID vaccine be safe fr fr no cap, CDC said so bruh"
            ],
            "dialect_nigerian_pidgin": [
                "Na true talk, the vaccine dey safe and e dey work, na wetin CDC talk"
            ],
            "dialect_singlish": [
                "The vaccine very safe lah, don't worry leh, CDC say one lor"
            ],
            "dialect_jamaican": [
                "Wah gwaan, mi tell yuh the vaccine good, nuh worry"
            ],
        }


# =============================================================================
# TEST WHEN RUN DIRECTLY
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CLAIM ANALYZER - SELF TEST")
    print("=" * 60)
    
    analyzer = ClaimAnalyzer()
    
    # Test each perturbation type
    test_cases = [
        ("Clean text", "The vaccine is safe and effective."),
        ("ALL CAPS", "THE VACCINE IS COMPLETELY SAFE!!!"),
        ("Leetspeak", "Th3 v4ccine is s4fe according 2 the CDC"),
        ("Double negation", "It is not untrue that the vaccine works"),
        ("Entity replacement", "According to some experts, the agency says it's safe"),
        ("LLM rewrite", "Furthermore, it is worth noting that the vaccine works. In conclusion, get it."),
        ("AAE dialect", "The vaccine be safe fr fr no cap bruh"),
        ("Nigerian Pidgin", "Na true talk, the vaccine dey safe wetin"),
    ]
    
    for name, text in test_cases:
        print(f"\n{'─' * 50}")
        print(f"📝 Test: {name}")
        print(f"   Input: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        
        result = analyzer.analyze(text)
        
        status = "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN"
        print(f"   Status: {status}")
        print(f"   Robustness: {result.robustness_score:.0%}")
        
        if result.is_perturbed:
            for p in result.perturbations_detected:
                print(f"   └─ {p.perturbation_type.value}: {p.explanation}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 60)