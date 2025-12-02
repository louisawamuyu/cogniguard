"""
COGNIGUARD CLAIM ANALYZER
Based on: "When Claims Evolve" (ACL 2025)

Detects 6 perturbation types:
1. CASING - TrueCasing vs UPPERCASE
2. TYPOS - Spelling errors, leetspeak, slang
3. NEGATION - Single vs double negatives
4. ENTITY REPLACEMENT - Names replaced with vague terms
5. LLM REWRITE - AI paraphrasing detection
6. DIALECT - AAE, Nigerian Pidgin, Singlish, Jamaican Patois
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class PerturbationType(Enum):
    """The 6 perturbation types from the paper"""
    CASING = "casing"
    TYPOS = "typos"
    NEGATION = "negation"
    ENTITY_REPLACEMENT = "entity_replacement"
    LLM_REWRITE = "llm_rewrite"
    DIALECT = "dialect"


class NoiseBudget(Enum):
    """Low = minimal changes, High = substantial changes"""
    LOW = "low"
    HIGH = "high"


@dataclass
class PerturbationResult:
    """Result for one detected perturbation"""
    original_claim: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    confidence: float
    evidence: List[str]
    normalized_claim: Optional[str]
    explanation: str


@dataclass
class ClaimAnalysisResult:
    """Complete analysis result"""
    input_claim: str
    is_perturbed: bool
    perturbations_detected: List[PerturbationResult]
    overall_confidence: float
    normalized_claim: str
    robustness_score: float
    recommendations: List[str]


class ClaimAnalyzer:
    """
    Analyzes text for the 6 perturbation types.
    
    Usage:
        analyzer = ClaimAnalyzer()
        result = analyzer.analyze("Th3 vaxx is s4fe fr fr no cap")
        print(result.is_perturbed)  # True
    """
    
    def __init__(self):
        """Set up all detection patterns"""
        self._setup_patterns()
        print("📊 Claim Analyzer initialized!")
        print("   Detecting 6 perturbation types from ACL 2025 paper")
    
    def _setup_patterns(self):
        """Define all detection patterns"""
        
        # CASING patterns
        self.casing_patterns = {
            'all_caps': r'^[A-Z\s\d\W]+$',
            'all_lower': r'^[a-z\s\d\W]+$',
            'mixed_weird': r'[a-z][A-Z][a-z]',
        }
        
        # TYPO patterns - leetspeak
        self.leetspeak_map = [
            ('0', 'o'),
            ('1', 'i'),
            ('3', 'e'),
            ('4', 'a'),
            ('5', 's'),
            ('7', 't'),
            ('@', 'a'),
        ]
        
        # TYPO patterns - slang
        self.slang_words = [
            'ur', 'u', 'r', 'b4', '2', '4', 'bc', 'cuz',
            'tho', 'thru', 'ppl', 'govt', 'lol', 'omg',
        ]
        
        # TYPO patterns - evasion
        self.evasion_patterns = [
            (r'vax+', 'vaccine'),
            (r'vaxx+', 'vaccine'),
            (r'c0vid', 'covid'),
            (r'cov1d', 'covid'),
        ]
        
        # NEGATION patterns - double
        self.double_negation_patterns = [
            r'not\s+un\w+',
            r'not\s+in\w+',
            r'never\s+not',
            r'not\s+without',
            r'not\s+impossible',
        ]
        
        # NEGATION patterns - single
        self.single_negation_patterns = [
            r'\bnot\b',
            r'\bnever\b',
            r'\bno\b',
            r"\bdon't\b",
            r"\bdoesn't\b",
            r"\bisn't\b",
            r"\baren't\b",
            r"\bwasn't\b",
            r"\bcan't\b",
            r"\bwon't\b",
        ]
        
        # ENTITY patterns
        self.vague_entity_patterns = [
            r'the agency',
            r'the organization',
            r'the health agency',
            r'the government',
            r'the authorities',
            r'the official',
            r'that country',
            r'some experts',
            r'sources say',
            r'according to reports',
        ]
        
        # LLM patterns
        self.llm_indicator_patterns = [
            r'\bfurthermore\b',
            r'\bmoreover\b',
            r'\badditionally\b',
            r'\bin conclusion\b',
            r'\bto summarize\b',
            r'\bit is worth noting\b',
            r'\bit should be noted\b',
        ]
        
        # DIALECT patterns
        self.dialect_markers = {
            'aae': [
                r'\bfinna\b',
                r'\bfr\b',
                r'\bno cap\b',
                r'\bbet\b',
                r'\bbruh\b',
                r'\bfam\b',
                r'\btryna\b',
            ],
            'nigerian_pidgin': [
                r'\bwetin\b',
                r'\bdey\b',
                r'\bna\b',
                r'\bwahala\b',
                r'\bsabi\b',
            ],
            'singlish': [
                r'\blah\b',
                r'\bleh\b',
                r'\blor\b',
                r'\bhor\b',
                r'\bmeh\b',
            ],
            'jamaican_patois': [
                r'\bwah gwaan\b',
                r'\bmi\b',
                r'\byuh\b',
                r'\bnuh\b',
            ],
        }
    
    def analyze(self, claim: str) -> ClaimAnalysisResult:
        """Analyze a claim for all 6 perturbation types"""
        perturbations = []
        
        # Check each type
        casing = self._detect_casing(claim)
        if casing:
            perturbations.append(casing)
        
        typos = self._detect_typos(claim)
        if typos:
            perturbations.append(typos)
        
        negation = self._detect_negation(claim)
        if negation:
            perturbations.append(negation)
        
        entity = self._detect_entity_replacement(claim)
        if entity:
            perturbations.append(entity)
        
        llm = self._detect_llm_rewrite(claim)
        if llm:
            perturbations.append(llm)
        
        dialect = self._detect_dialect(claim)
        if dialect:
            perturbations.append(dialect)
        
        # Calculate metrics
        is_perturbed = len(perturbations) > 0
        
        overall_confidence = 0.0
        if perturbations:
            overall_confidence = max(p.confidence for p in perturbations)
        
        # Robustness score
        robustness = 1.0
        for p in perturbations:
            if p.noise_budget == NoiseBudget.HIGH:
                robustness -= 0.2 * p.confidence
            else:
                robustness -= 0.1 * p.confidence
        robustness = max(0.0, min(1.0, robustness))
        
        recommendations = self._generate_recommendations(perturbations)
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
    
    def _detect_casing(self, claim: str) -> Optional[PerturbationResult]:
        """Detect casing perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        if len(claim) < 10:
            return None
        
        # Check ALL CAPS
        if re.match(self.casing_patterns['all_caps'], claim):
            evidence.append("Text is ALL UPPERCASE")
            noise_budget = NoiseBudget.HIGH
            confidence = 0.9
        
        # Check all lowercase
        elif re.match(self.casing_patterns['all_lower'], claim):
            if re.search(r'\bi\b', claim):
                evidence.append("Text is all lowercase (missing capitals)")
                noise_budget = NoiseBudget.HIGH
                confidence = 0.7
        
        # Check weird mixed casing
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
        """Detect typo perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        claim_lower = claim.lower()
        
        # Check leetspeak
        leetspeak_found = []
        for number, letter in self.leetspeak_map:
            if number in claim:
                leetspeak_found.append(f"'{number}' for '{letter}'")
        
        if leetspeak_found:
            evidence.append(f"Leetspeak: {', '.join(leetspeak_found[:3])}")
            if len(leetspeak_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.85)
            else:
                confidence = max(confidence, 0.6)
        
        # Check slang
        slang_found = []
        for slang in self.slang_words:
            pattern = r'\b' + re.escape(slang) + r'\b'
            if re.search(pattern, claim_lower):
                slang_found.append(slang)
        
        if slang_found:
            evidence.append(f"Slang: {', '.join(slang_found[:3])}")
            if len(slang_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.8)
            else:
                confidence = max(confidence, 0.5)
        
        # Check evasion spellings
        for pattern, correct in self.evasion_patterns:
            if re.search(pattern, claim_lower):
                evidence.append(f"Evasion spelling: '{pattern}' for '{correct}'")
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
        
        # Check double negations first
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
                    clean_marker = marker.replace(r'\b', '')
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
    
    def _normalize_claim(self, claim: str) -> str:
        """Normalize a claim to canonical form"""
        normalized = claim
        
        # Fix all caps
        if normalized.isupper():
            normalized = normalized.capitalize()
        
        # Fix leetspeak
        for number, letter in self.leetspeak_map:
            normalized = normalized.replace(number, letter)
        
        # Expand abbreviations
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
        """Fix common typos"""
        fixed = claim
        
        for number, letter in self.leetspeak_map:
            fixed = fixed.replace(number, letter)
        
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
        """Generate recommendations"""
        if not perturbations:
            return ["No perturbations detected. Claim appears in canonical form."]
        
        recommendations = []
        
        for p in perturbations:
            if p.perturbation_type == PerturbationType.CASING:
                recommendations.append("Normalize text casing before processing")
            elif p.perturbation_type == PerturbationType.TYPOS:
                recommendations.append("Apply spelling correction and normalize leetspeak")
            elif p.perturbation_type == PerturbationType.NEGATION:
                recommendations.append("Carefully parse negation logic - check for double negatives")
            elif p.perturbation_type == PerturbationType.ENTITY_REPLACEMENT:
                recommendations.append("Resolve vague entity references to specific names")
            elif p.perturbation_type == PerturbationType.LLM_REWRITE:
                recommendations.append("Extract core claim meaning - text may be AI paraphrased")
            elif p.perturbation_type == PerturbationType.DIALECT:
                recommendations.append("Translate dialect to standard English before matching")
        
        recommendations.append("Compare normalized claim against fact-check database")
        
        return recommendations
    
    def demo_perturbations(self) -> Dict[str, List[str]]:
        """Generate example perturbations for each type"""
        
        original = "The COVID-19 vaccine is safe and effective according to the CDC."
        
        return {
            "original": [original],
            "casing_low": [
                "the covid-19 vaccine is safe and effective according to the cdc."
            ],
            "casing_high": [
                "THE COVID-19 VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC!"
            ],
            "typos_low": [
                "The COVID-19 vacine is safe and effective according to the CDC."
            ],
            "typos_high": [
                "Th3 C0VID-19 vaxx is s4fe and effective according 2 the CDC lol"
            ],
            "negation_low": [
                "The COVID-19 vaccine is not unsafe according to the CDC."
            ],
            "negation_high": [
                "It is not untrue that the COVID-19 vaccine is not ineffective according to the CDC."
            ],
            "entity_low": [
                "The COVID-19 vaccine is safe according to the health agency."
            ],
            "entity_high": [
                "According to sources, some experts say the treatment works."
            ],
            "llm_rewrite_low": [
                "According to the CDC, the COVID-19 vaccine has been deemed safe and effective."
            ],
            "llm_rewrite_high": [
                "It is worth noting that, furthermore, the vaccine is safe. Moreover, it works. In conclusion, get vaccinated."
            ],
            "dialect_aae": [
                "The COVID vaccine be safe fr fr no cap, CDC said so bruh"
            ],
            "dialect_nigerian_pidgin": [
                "Na true talk, the vaccine dey safe and e dey work, na wetin CDC talk"
            ],
        }


# Test when run directly
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CLAIM ANALYZER - SELF TEST")
    print("=" * 50)
    
    analyzer = ClaimAnalyzer()
    
    test_cases = [
        "The vaccine is safe and effective.",
        "THE VACCINE IS COMPLETELY SAFE!!!",
        "Th3 v4ccine is s4fe according 2 the CDC",
        "It is not untrue that the vaccine works",
        "The vaccine be safe fr fr no cap bruh",
    ]
    
    for text in test_cases:
        result = analyzer.analyze(text)
        status = "PERTURBED" if result.is_perturbed else "CLEAN"
        print(f"\n[{status}] \"{text[:40]}...\"")
        print(f"   Robustness: {result.robustness_score:.0%}")
        if result.is_perturbed:
            for p in result.perturbations_detected:
                print(f"   - {p.perturbation_type.value}: {p.explanation}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    