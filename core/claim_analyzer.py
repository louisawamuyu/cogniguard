"""
CogniGuard Claim Analyzer
Detects 6 perturbation types from ACL 2025 paper
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class PerturbationType(Enum):
    CASING = "casing"
    TYPOS = "typos"
    NEGATION = "negation"
    ENTITY_REPLACEMENT = "entity_replacement"
    LLM_REWRITE = "llm_rewrite"
    DIALECT = "dialect"


class NoiseBudget(Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class PerturbationResult:
    original_claim: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    confidence: float
    evidence: List[str]
    normalized_claim: Optional[str]
    explanation: str


@dataclass
class ClaimAnalysisResult:
    input_claim: str
    is_perturbed: bool
    perturbations_detected: List[PerturbationResult]
    overall_confidence: float
    normalized_claim: str
    robustness_score: float
    recommendations: List[str]


class ClaimAnalyzer:
    """Analyzes claims for 6 perturbation types"""
    
    def __init__(self):
        # Casing patterns
        self.casing_patterns = {
            'all_caps': r'^[A-Z\s\d\W]+$',
            'all_lower': r'^[a-z\s\d\W]+$',
        }
        
        # Typo patterns
        self.leetspeak = [(r'0', 'o'), (r'1', 'i'), (r'3', 'e'), (r'4', 'a'), (r'5', 's')]
        self.slang_words = ['ur', 'u', 'r', 'b4', '2', '4', 'bc', 'cuz', 'tho', 'thru', 'ppl', 'govt']
        
        # Negation patterns
        self.double_negation = [r'\b(not\s+un\w+)\b', r'\b(not\s+in\w+)\b']
        self.single_negation = [r'\bnot\b', r'\bnever\b', r"\bdon't\b", r"\bdoesn't\b", r"\bisn't\b"]
        
        # Dialect markers
        self.dialect_markers = {
            'aae': [r'\bfinna\b', r'\bfr\b', r'\bno cap\b', r'\bbet\b', r'\bbruh\b'],
            'nigerian_pidgin': [r'\bwetin\b', r'\bdey\b', r'\bna\b', r'\bwahala\b'],
            'singlish': [r'\blah\b', r'\bleh\b', r'\blor\b', r'\bmeh\b'],
            'jamaican': [r'\bwah gwaan\b', r'\bmi\b', r'\byuh\b', r'\bnuh\b'],
        }
        
        # LLM indicators
        self.llm_indicators = [r'\bfurthermore\b', r'\bmoreover\b', r'\bin conclusion\b', r'\bit is worth noting\b']
        
        # Entity patterns
        self.vague_entities = [r'\bthe agency\b', r'\bthe organization\b', r'\bsome experts\b', r'\bthat country\b']
    
    def analyze(self, claim: str) -> ClaimAnalysisResult:
        """Analyze a claim for perturbations"""
        perturbations = []
        
        # Check casing
        casing = self._check_casing(claim)
        if casing:
            perturbations.append(casing)
        
        # Check typos
        typos = self._check_typos(claim)
        if typos:
            perturbations.append(typos)
        
        # Check negation
        negation = self._check_negation(claim)
        if negation:
            perturbations.append(negation)
        
        # Check dialect
        dialect = self._check_dialect(claim)
        if dialect:
            perturbations.append(dialect)
        
        # Check LLM rewrite
        llm = self._check_llm(claim)
        if llm:
            perturbations.append(llm)
        
        # Check entity replacement
        entity = self._check_entity(claim)
        if entity:
            perturbations.append(entity)
        
        # Calculate metrics
        is_perturbed = len(perturbations) > 0
        confidence = max([p.confidence for p in perturbations], default=0.0)
        robustness = 1.0 - (0.15 * len(perturbations))
        robustness = max(0.0, min(1.0, robustness))
        
        recommendations = self._get_recommendations(perturbations)
        normalized = self._normalize(claim)
        
        return ClaimAnalysisResult(
            input_claim=claim,
            is_perturbed=is_perturbed,
            perturbations_detected=perturbations,
            overall_confidence=confidence,
            normalized_claim=normalized,
            robustness_score=robustness,
            recommendations=recommendations
        )
    
    def _check_casing(self, claim: str) -> Optional[PerturbationResult]:
        if re.match(self.casing_patterns['all_caps'], claim) and len(claim) > 10:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.CASING,
                noise_budget=NoiseBudget.HIGH,
                confidence=0.9,
                evidence=["Text is ALL UPPERCASE"],
                normalized_claim=claim.capitalize(),
                explanation="All caps detected - high noise casing perturbation"
            )
        return None
    
    def _check_typos(self, claim: str) -> Optional[PerturbationResult]:
        evidence = []
        claim_lower = claim.lower()
        
        # Check leetspeak
        for pattern, letter in self.leetspeak:
            if re.search(pattern, claim):
                evidence.append(f"Leetspeak: {pattern} → {letter}")
        
        # Check slang
        for slang in self.slang_words:
            if re.search(rf'\b{slang}\b', claim_lower):
                evidence.append(f"Slang: {slang}")
        
        if len(evidence) >= 2:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.TYPOS,
                noise_budget=NoiseBudget.HIGH if len(evidence) >= 3 else NoiseBudget.LOW,
                confidence=min(0.9, 0.3 * len(evidence)),
                evidence=evidence,
                normalized_claim=claim,
                explanation=f"Typo perturbation: {len(evidence)} patterns found"
            )
        return None
    
    def _check_negation(self, claim: str) -> Optional[PerturbationResult]:
        claim_lower = claim.lower()
        evidence = []
        
        # Check double negation first
        for pattern in self.double_negation:
            matches = re.findall(pattern, claim_lower)
            for m in matches:
                evidence.append(f"Double negation: {m}")
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.NEGATION,
                noise_budget=NoiseBudget.HIGH,
                confidence=0.85,
                evidence=evidence,
                normalized_claim=claim,
                explanation="Double negation detected"
            )
        
        # Check single negation count
        neg_count = sum(len(re.findall(p, claim_lower)) for p in self.single_negation)
        if neg_count >= 2:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.NEGATION,
                noise_budget=NoiseBudget.LOW,
                confidence=0.5,
                evidence=[f"Multiple negations: {neg_count} found"],
                normalized_claim=claim,
                explanation="Multiple negations detected"
            )
        return None
    
    def _check_dialect(self, claim: str) -> Optional[PerturbationResult]:
        claim_lower = claim.lower()
        
        for dialect, markers in self.dialect_markers.items():
            found = []
            for marker in markers:
                if re.search(marker, claim_lower):
                    found.append(marker.replace(r'\b', ''))
            
            if len(found) >= 2:
                return PerturbationResult(
                    original_claim=claim,
                    perturbation_type=PerturbationType.DIALECT,
                    noise_budget=NoiseBudget.HIGH,
                    confidence=0.85,
                    evidence=[f"Dialect ({dialect}): {', '.join(found)}"],
                    normalized_claim=claim,
                    explanation=f"Dialect detected: {dialect.upper()}"
                )
        return None
    
    def _check_llm(self, claim: str) -> Optional[PerturbationResult]:
        claim_lower = claim.lower()
        found = []
        
        for pattern in self.llm_indicators:
            if re.search(pattern, claim_lower):
                match = re.search(pattern, claim_lower)
                if match:
                    found.append(match.group())
        
        if len(found) >= 2:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.LLM_REWRITE,
                noise_budget=NoiseBudget.HIGH,
                confidence=0.75,
                evidence=[f"LLM indicators: {', '.join(found)}"],
                normalized_claim=claim,
                explanation="Possible LLM rewrite detected"
            )
        return None
    
    def _check_entity(self, claim: str) -> Optional[PerturbationResult]:
        claim_lower = claim.lower()
        found = []
        
        for pattern in self.vague_entities:
            if re.search(pattern, claim_lower):
                match = re.search(pattern, claim_lower)
                if match:
                    found.append(match.group())
        
        if found:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.ENTITY_REPLACEMENT,
                noise_budget=NoiseBudget.HIGH if len(found) >= 2 else NoiseBudget.LOW,
                confidence=0.6,
                evidence=[f"Vague entities: {', '.join(found)}"],
                normalized_claim=claim,
                explanation="Entity replacement detected"
            )
        return None
    
    def _normalize(self, claim: str) -> str:
        normalized = claim
        if normalized.isupper():
            normalized = normalized.capitalize()
        # Fix leetspeak
        for pattern, letter in self.leetspeak:
            normalized = re.sub(pattern, letter, normalized)
        return normalized
    
    def _get_recommendations(self, perturbations: List[PerturbationResult]) -> List[str]:
        if not perturbations:
            return ["No perturbations detected"]
        
        recs = []
        for p in perturbations:
            if p.perturbation_type == PerturbationType.CASING:
                recs.append("Normalize text casing")
            elif p.perturbation_type == PerturbationType.TYPOS:
                recs.append("Apply spelling correction")
            elif p.perturbation_type == PerturbationType.NEGATION:
                recs.append("Carefully parse negation logic")
            elif p.perturbation_type == PerturbationType.DIALECT:
                recs.append("Translate to standard English")
            elif p.perturbation_type == PerturbationType.LLM_REWRITE:
                recs.append("Extract core claim meaning")
            elif p.perturbation_type == PerturbationType.ENTITY_REPLACEMENT:
                recs.append("Resolve vague entity references")
        
        recs.append("Compare against fact-check database")
        return recs
    
    def demo_perturbations(self) -> Dict[str, List[str]]:
        """Demo examples for each perturbation type"""
        return {
            "original": ["The COVID-19 vaccine is safe and effective according to the CDC."],
            "casing_low": ["the covid-19 vaccine is safe."],
            "casing_high": ["THE COVID-19 VACCINE IS SAFE AND EFFECTIVE!"],
            "typos_low": ["The COVID-19 vacine is safe."],
            "typos_high": ["Th3 vaxx is s4fe according 2 the CDC"],
            "negation_low": ["The vaccine is not unsafe."],
            "negation_high": ["It is not untrue that the vaccine is not ineffective."],
            "entity_low": ["The vaccine is safe according to the agency."],
            "entity_high": ["According to some experts, that organization says it works."],
            "llm_rewrite_low": ["According to the CDC, the vaccine is safe."],
            "llm_rewrite_high": ["It is worth noting that, furthermore, the vaccine works. In conclusion, get it."],
            "dialect_aae": ["The vaccine be safe fr fr no cap bruh"],
            "dialect_nigerian_pidgin": ["Na true talk, the vaccine dey safe wetin"],
        }


# Test when run directly
if __name__ == "__main__":
    print("Testing Claim Analyzer...")
    analyzer = ClaimAnalyzer()
    
    tests = [
        "The vaccine is safe.",
        "THE VACCINE IS SAFE AND EFFECTIVE!!!",
        "Th3 vaxx is s4fe according 2 the govt",
        "It is not untrue that the vaccine works",
        "The vaccine be safe fr fr no cap bruh",
    ]
    
    for text in tests:
        result = analyzer.analyze(text)
        status = "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN"
        print(f"\n{status}: \"{text[:40]}...\"")
        print(f"   Robustness: {result.robustness_score:.0%}")
        if result.perturbations_detected:
            for p in result.perturbations_detected:
                print(f"   - {p.perturbation_type.value}: {p.explanation}")
    
    print("\n✅ Claim Analyzer working!")