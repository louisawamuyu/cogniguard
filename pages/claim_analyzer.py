"""
=============================================================================
COGNIGUARD CLAIM ANALYZER
Based on: "When Claims Evolve" (ACL 2025)

Detects the 6 perturbation types:
1. Casing - TrueCasing vs UPPERCASE
2. Typos - Minor vs leetspeak/slang
3. Negation - Single vs double negation
4. Entity Replacement - Partial vs full swapping
5. LLM Rewrite - Minimal vs maximal paraphrasing
6. Dialect - AAE, Nigerian Pidgin, Singlish, Jamaican Patois
=============================================================================
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
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
    """Result of analyzing a claim for one perturbation type"""
    original_claim: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    confidence: float
    evidence: List[str]
    normalized_claim: Optional[str]
    explanation: str


@dataclass
class ClaimAnalysisResult:
    """Complete analysis of a potentially perturbed claim"""
    input_claim: str
    is_perturbed: bool
    perturbations_detected: List[PerturbationResult]
    overall_confidence: float
    normalized_claim: str
    robustness_score: float
    recommendations: List[str]


class ClaimAnalyzer:
    """
    Analyzes claims for perturbations based on ACL 2025 paper.
    
    Example:
        analyzer = ClaimAnalyzer()
        result = analyzer.analyze("Th3 v4ccine is s4fe")
        print(result.is_perturbed)  # True
        print(result.perturbations_detected)  # [typos]
    """
    
    def __init__(self):
        """Initialize with detection patterns"""
        
        # Casing patterns
        self.casing_patterns = {
            'all_caps': r'^[A-Z\s\d\W]+$',
            'all_lower': r'^[a-z\s\d\W]+$',
            'mixed_unusual': r'[a-z]+[A-Z]+[a-z]+',
        }
        
        # Typo patterns
        self.typo_patterns = {
            'leetspeak': [
                (r'0', 'o'), (r'1', 'i'), (r'3', 'e'), (r'4', 'a'),
                (r'5', 's'), (r'7', 't'), (r'@', 'a'), (r'\$', 's'),
            ],
            'slang': [
                'ur', 'u', 'r', 'b4', '2', '4', 'w/', 'w/o', 'bc', 'cuz',
                'tho', 'thru', 'ppl', 'govt', 'yr', 'yrs', 'msg', 'msgs',
            ],
            'evasion_spellings': [
                (r'vax+ine', 'vaccine'), (r'vaxx', 'vaccine'),
                (r'c0vid', 'covid'), (r'cov1d', 'covid'),
                (r'v1rus', 'virus'), (r'pan+demic', 'pandemic'),
            ],
        }
        
        # Negation patterns
        self.negation_patterns = {
            'single': [
                r'\b(is not|are not|was not|were not)\b',
                r"\b(isn't|aren't|wasn't|weren't)\b",
                r'\b(does not|do not|did not)\b',
                r"\b(doesn't|don't|didn't)\b",
                r'\b(has not|have not|had not)\b',
                r"\b(hasn't|haven't|hadn't)\b",
                r'\b(will not|would not|could not|should not)\b',
                r"\b(won't|wouldn't|couldn't|shouldn't)\b",
                r'\b(cannot|can not)\b',
                r"\b(can't)\b",
                r'\bnot\b',
                r'\bnever\b',
                r'\bno\b',
            ],
            'double': [
                r'\b(not\s+un\w+)\b',
                r'\b(never\s+not)\b',
                r'\b(no\s+un\w+)\b',
                r"\b(isn't\s+un\w+)\b",
                r"\b(wasn't\s+un\w+)\b",
                r"\b(can't\s+not)\b",
                r'\b(not\s+without)\b',
                r'\b(not\s+impossible)\b',
                r'\b(not\s+incorrect)\b',
                r'\b(not\s+inaccurate)\b',
            ],
        }
        
        # Entity replacement patterns
        self.entity_replacements = {
            'political': {
                'synonyms': [
                    ('president', ['POTUS', 'the administration', 'the leader']),
                    ('government', ['govt', 'the state', 'authorities']),
                ],
            },
            'organizations': {
                'synonyms': [
                    ('WHO', ['World Health Organization', 'the health agency']),
                    ('CDC', ['Centers for Disease Control', 'the health department']),
                    ('FDA', ['Food and Drug Administration', 'drug regulators']),
                ],
            },
        }
        
        # Dialect markers
        self.dialect_markers = {
            'aae': [
                r'\bfinna\b', r'\bion\b', r'\baint\b', r"\bain't\b",
                r'\bgon\b', r'\bgonna\b', r'\btryna\b', r'\bwanna\b',
                r'\bbruh\b', r'\bfam\b', r'\bbet\b', r'\bcap\b',
                r'\bno cap\b', r'\bfr\b', r'\bong\b', r'\bfasho\b',
            ],
            'nigerian_pidgin': [
                r'\bwetin\b', r'\bdey\b', r'\bna\b', r'\bwahala\b',
                r'\bsabi\b', r'\bpalava\b', r'\bdem\b',
                r'\bno be\b', r'\bsharp sharp\b', r'\babi\b',
            ],
            'singlish': [
                r'\blah\b', r'\bleh\b', r'\blor\b', r'\bhor\b',
                r'\bmeh\b', r'\bsibo\b', r'\bwalao\b', r'\bsian\b',
            ],
            'jamaican_patois': [
                r'\bwah gwaan\b', r'\bmi\b', r'\bdem\b', r'\byuh\b',
                r'\bweh\b', r'\bfi\b', r'\binna\b', r'\boutta\b',
            ],
        }
        
        # LLM rewrite indicators
        self.llm_rewrite_indicators = [
            r'\b(furthermore|moreover|additionally|consequently)\b',
            r'\b(it is worth noting that|it should be noted that)\b',
            r'\b(in conclusion|to summarize|in summary)\b',
            r'\b(on the other hand|conversely|alternatively)\b',
            r'\b(it appears that|it seems that|it is suggested that)\b',
        ]
        
        print("📊 Claim Analyzer initialized!")
        print("   Based on: 'When Claims Evolve' (ACL 2025)")
        print("   Perturbation types: 6")
    
    def analyze(self, claim: str, original_claim: Optional[str] = None) -> ClaimAnalysisResult:
        """Analyze a claim for perturbations"""
        perturbations = []
        
        # Check each perturbation type
        casing_result = self._check_casing(claim)
        if casing_result:
            perturbations.append(casing_result)
        
        typo_result = self._check_typos(claim)
        if typo_result:
            perturbations.append(typo_result)
        
        negation_result = self._check_negation(claim)
        if negation_result:
            perturbations.append(negation_result)
        
        entity_result = self._check_entity_replacement(claim)
        if entity_result:
            perturbations.append(entity_result)
        
        dialect_result = self._check_dialect(claim)
        if dialect_result:
            perturbations.append(dialect_result)
        
        llm_result = self._check_llm_rewrite(claim)
        if llm_result:
            perturbations.append(llm_result)
        
        # Calculate metrics
        is_perturbed = len(perturbations) > 0
        overall_confidence = max([p.confidence for p in perturbations]) if perturbations else 0.0
        normalized = self._normalize_claim(claim)
        robustness = self._calculate_robustness_score(claim, perturbations)
        recommendations = self._generate_recommendations(perturbations)
        
        return ClaimAnalysisResult(
            input_claim=claim,
            is_perturbed=is_perturbed,
            perturbations_detected=perturbations,
            overall_confidence=overall_confidence,
            normalized_claim=normalized,
            robustness_score=robustness,
            recommendations=recommendations
        )
    
    def _check_casing(self, claim: str) -> Optional[PerturbationResult]:
        """Check for casing perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        if re.match(self.casing_patterns['all_caps'], claim):
            evidence.append("Entire claim is in UPPERCASE")
            noise_budget = NoiseBudget.HIGH
            confidence = 0.9
        elif re.match(self.casing_patterns['all_lower'], claim):
            if re.search(r'\b(i|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', claim):
                evidence.append("Claim is all lowercase, missing expected capitals")
                noise_budget = NoiseBudget.HIGH
                confidence = 0.7
        elif re.search(self.casing_patterns['mixed_unusual'], claim):
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
                normalized_claim=claim.capitalize() if noise_budget == NoiseBudget.HIGH else claim,
                explanation=f"Casing perturbation: {', '.join(evidence)}"
            )
        return None
    
    def _check_typos(self, claim: str) -> Optional[PerturbationResult]:
        """Check for typo perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        # Check leetspeak
        leetspeak_count = 0
        for pattern, replacement in self.typo_patterns['leetspeak']:
            if re.search(pattern, claim):
                leetspeak_count += 1
                evidence.append(f"Leetspeak: '{pattern}' → '{replacement}'")
        
        if leetspeak_count >= 3:
            noise_budget = NoiseBudget.HIGH
            confidence = max(confidence, 0.85)
        elif leetspeak_count >= 1:
            confidence = max(confidence, 0.6)
        
        # Check slang
        claim_lower = claim.lower()
        slang_found = []
        for slang in self.typo_patterns['slang']:
            if re.search(rf'\b{slang}\b', claim_lower):
                slang_found.append(slang)
        
        if slang_found:
            evidence.append(f"Slang: {', '.join(slang_found)}")
            if len(slang_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.8)
            else:
                confidence = max(confidence, 0.5)
        
        # Check evasion spellings
        for pattern, correct in self.typo_patterns['evasion_spellings']:
            if re.search(pattern, claim_lower):
                evidence.append(f"Evasion spelling: '{pattern}' → '{correct}'")
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
                explanation=f"Typo perturbation: {len(evidence)} patterns found"
            )
        return None
    
    def _check_negation(self, claim: str) -> Optional[PerturbationResult]:
        """Check for negation perturbations"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        claim_lower = claim.lower()
        
        # Check double negation first
        for pattern in self.negation_patterns['double']:
            matches = re.findall(pattern, claim_lower)
            if matches:
                evidence.append(f"Double negation: '{matches[0]}'")
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.9)
        
        # Check single negation
        negation_count = 0
        for pattern in self.negation_patterns['single']:
            matches = re.findall(pattern, claim_lower)
            negation_count += len(matches)
        
        if negation_count >= 3 and noise_budget != NoiseBudget.HIGH:
            evidence.append(f"Multiple negations: {negation_count} found")
            noise_budget = NoiseBudget.HIGH
            confidence = max(confidence, 0.7)
        elif negation_count >= 1 and not evidence:
            evidence.append(f"Negation present: {negation_count} negation(s)")
            confidence = max(confidence, 0.4)
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.NEGATION,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=self._resolve_negation(claim),
                explanation=f"Negation perturbation: {noise_budget.value} noise"
            )
        return None
    
    def _check_entity_replacement(self, claim: str) -> Optional[PerturbationResult]:
        """Check for entity replacement"""
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        claim_lower = claim.lower()
        
        replacement_count = 0
        for category, data in self.entity_replacements.items():
            for original, synonyms in data['synonyms']:
                for synonym in synonyms:
                    if synonym.lower() in claim_lower:
                        evidence.append(f"Possible replacement: '{synonym}' → '{original}'")
                        replacement_count += 1
        
        if replacement_count >= 3:
            noise_budget = NoiseBudget.HIGH
            confidence = 0.8
        elif replacement_count >= 1:
            confidence = 0.5
        
        # Check vague references
        vague_patterns = [
            r'\b(that country|the country|that nation)\b',
            r'\b(the agency|the organization|the group)\b',
            r'\b(the leader|the official|the authorities)\b',
            r'\b(some experts|sources say|according to reports)\b',
        ]
        
        for pattern in vague_patterns:
            if re.search(pattern, claim_lower):
                evidence.append(f"Vague reference: '{pattern}'")
                confidence = max(confidence, 0.6)
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.ENTITY_REPLACEMENT,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"Entity replacement: {replacement_count} swaps"
            )
        return None
    
    def _check_dialect(self, claim: str) -> Optional[PerturbationResult]:
        """Check for dialect perturbations"""
        evidence = []
        detected_dialect = None
        confidence = 0.0
        claim_lower = claim.lower()
        
        for dialect, markers in self.dialect_markers.items():
            matches = []
            for marker in markers:
                if re.search(marker, claim_lower):
                    matches.append(marker.replace(r'\b', '').replace('\\b', ''))
            
            if matches:
                if len(matches) >= 2:
                    detected_dialect = dialect
                    evidence.append(f"Dialect markers ({dialect}): {', '.join(matches)}")
                    confidence = max(confidence, 0.85)
                elif len(matches) == 1:
                    evidence.append(f"Possible {dialect} marker: {matches[0]}")
                    confidence = max(confidence, 0.4)
        
        if evidence:
            dialect_names = {
                'aae': 'African American English',
                'nigerian_pidgin': 'Nigerian Pidgin',
                'singlish': 'Singlish',
                'jamaican_patois': 'Jamaican Patois',
            }
            
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.DIALECT,
                noise_budget=NoiseBudget.HIGH,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"Dialect: {dialect_names.get(detected_dialect, 'Unknown')}"
            )
        return None
    
    def _check_llm_rewrite(self, claim: str) -> Optional[PerturbationResult]:
        """Check for LLM rewrite indicators"""
        evidence = []
        confidence = 0.0
        claim_lower = claim.lower()
        
        indicator_count = 0
        for pattern in self.llm_rewrite_indicators:
            if re.search(pattern, claim_lower):
                match = re.search(pattern, claim_lower)
                evidence.append(f"LLM indicator: '{match.group()}'")
                indicator_count += 1
        
        if indicator_count >= 2:
            confidence = 0.75
        elif indicator_count >= 1:
            confidence = 0.4
        
        if evidence:
            noise_budget = NoiseBudget.HIGH if confidence >= 0.6 else NoiseBudget.LOW
            
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.LLM_REWRITE,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"LLM rewrite: {indicator_count} indicators"
            )
        return None
    
    def _normalize_claim(self, claim: str) -> str:
        """Normalize a claim to canonical form"""
        normalized = claim.strip()
        
        if normalized.isupper():
            normalized = normalized.capitalize()
        
        for pattern, replacement in self.typo_patterns['leetspeak']:
            normalized = re.sub(pattern, replacement, normalized)
        
        abbreviation_map = {
            r'\bu\b': 'you', r'\bur\b': 'your', r'\br\b': 'are',
            r'\bb4\b': 'before', r'\bw/\b': 'with', r'\bw/o\b': 'without',
            r'\bbc\b': 'because', r'\bcuz\b': 'because',
            r'\btho\b': 'though', r'\bthru\b': 'through',
            r'\bppl\b': 'people', r'\bgovt\b': 'government',
        }
        
        for pattern, replacement in abbreviation_map.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _fix_typos(self, claim: str) -> str:
        """Fix common typos"""
        fixed = claim
        for pattern, replacement in self.typo_patterns['leetspeak']:
            fixed = re.sub(pattern, replacement, fixed)
        for pattern, correct in self.typo_patterns['evasion_spellings']:
            fixed = re.sub(pattern, correct, fixed, flags=re.IGNORECASE)
        return fixed
    
    def _resolve_negation(self, claim: str) -> str:
        """Resolve double negations"""
        resolved = claim
        fixes = [
            (r'not\s+untrue', 'true'),
            (r'not\s+incorrect', 'correct'),
            (r'not\s+inaccurate', 'accurate'),
            (r'not\s+impossible', 'possible'),
            (r'never\s+not', 'always'),
        ]
        for pattern, replacement in fixes:
            resolved = re.sub(pattern, replacement, resolved, flags=re.IGNORECASE)
        return resolved
    
    def _calculate_robustness_score(self, claim: str, perturbations: List[PerturbationResult]) -> float:
        """Calculate robustness score (0-1), higher = more robust"""
        if not perturbations:
            return 1.0
        
        score = 1.0
        for p in perturbations:
            if p.noise_budget == NoiseBudget.HIGH:
                penalty = 0.2 * p.confidence
            else:
                penalty = 0.1 * p.confidence
            score -= penalty
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(self, perturbations: List[PerturbationResult]) -> List[str]:
        """Generate recommendations"""
        if not perturbations:
            return ["No perturbations detected. Claim appears in canonical form."]
        
        recommendations = []
        for p in perturbations:
            if p.perturbation_type == PerturbationType.CASING:
                recommendations.append("Normalize casing before processing")
            elif p.perturbation_type == PerturbationType.TYPOS:
                recommendations.append("Apply typo correction")
            elif p.perturbation_type == PerturbationType.NEGATION:
                recommendations.append("Check for double negatives")
            elif p.perturbation_type == PerturbationType.ENTITY_REPLACEMENT:
                recommendations.append("Resolve entity references")
            elif p.perturbation_type == PerturbationType.LLM_REWRITE:
                recommendations.append("Extract core claim meaning")
            elif p.perturbation_type == PerturbationType.DIALECT:
                recommendations.append("Translate dialect to standard form")
        
        recommendations.append("Compare normalized claim against fact-check database")
        return recommendations
    
    def demo_perturbations(self) -> Dict[str, List[str]]:
        """Generate example perturbations for testing"""
        original = "The COVID-19 vaccine is safe and effective according to the CDC."
        
        return {
            "original": [original],
            "casing_low": ["the covid-19 vaccine is safe and effective according to the cdc."],
            "casing_high": ["THE COVID-19 VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC."],
            "typos_low": ["The COVID-19 vacine is safe and effective according to the CDC."],
            "typos_high": ["Th3 C0VID-19 vaxx is safe & effective according 2 the CDC lol"],
            "negation_low": ["The COVID-19 vaccine is not unsafe according to the CDC."],
            "negation_high": ["It is not untrue that the COVID-19 vaccine is not ineffective."],
            "entity_low": ["The COVID-19 vaccine is safe according to the health agency."],
            "entity_high": ["The shot is safe according to that government organization."],
            "llm_rewrite_low": ["According to the CDC, the COVID-19 vaccine has been deemed safe."],
            "llm_rewrite_high": ["It is worth noting that, furthermore, the vaccine has been deemed safe. In conclusion, it works."],
            "dialect_aae": ["The COVID vaccine be safe fr fr no cap, CDC said so"],
            "dialect_nigerian_pidgin": ["Na true talk, the vaccine dey safe, na wetin CDC talk"],
        }


# Test when run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("CLAIM ANALYZER TEST")
    print("="*60 + "\n")
    
    analyzer = ClaimAnalyzer()
    demos = analyzer.demo_perturbations()
    
    for category, claims in demos.items():
        for claim in claims:
            result = analyzer.analyze(claim)
            status = "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN"
            print(f"\n{category}: {status}")
            print(f"  \"{claim[:50]}...\"" if len(claim) > 50 else f"  \"{claim}\"")
            print(f"  Robustness: {result.robustness_score:.0%}")
    
    print("\n" + "="*60)