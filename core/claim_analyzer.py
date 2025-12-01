"""
=============================================================================
COGNIGUARD CLAIM ANALYZER
Based on: "When Claims Evolve: Evaluating and Enhancing the Robustness of 
Embedding Models Against Misinformation Edits" (ACL 2025)

This module implements the paper's taxonomy of 6 perturbation types:
1. Casing - TrueCasing (low) vs. UPPERCASE (high)
2. Typos - Minimal vs. maximal Levenshtein distance edits
3. Negation - Single vs. double negation
4. Entity Replacement - Partial vs. full entity swapping
5. LLM Rewrite - Minimal vs. maximal paraphrasing
6. Dialect - Rewrites in AAE, Nigerian Pidgin, Singlish, Jamaican Patois
=============================================================================
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class PerturbationType(Enum):
    """
    The 6 perturbation types from the paper
    Each type has low and high noise budgets
    """
    CASING = "casing"
    TYPOS = "typos"
    NEGATION = "negation"
    ENTITY_REPLACEMENT = "entity_replacement"
    LLM_REWRITE = "llm_rewrite"
    DIALECT = "dialect"


class NoiseBudget(Enum):
    """
    Low = minimal changes
    High = substantial changes
    """
    LOW = "low"
    HIGH = "high"


@dataclass
class PerturbationResult:
    """
    Result of analyzing a claim for perturbations
    """
    original_claim: str
    perturbation_type: PerturbationType
    noise_budget: NoiseBudget
    confidence: float
    evidence: List[str]
    normalized_claim: Optional[str]
    explanation: str


@dataclass
class ClaimAnalysisResult:
    """
    Complete analysis of a potentially perturbed claim
    """
    input_claim: str
    is_perturbed: bool
    perturbations_detected: List[PerturbationResult]
    overall_confidence: float
    normalized_claim: str
    robustness_score: float
    recommendations: List[str]


# =============================================================================
# MAIN CLAIM ANALYZER CLASS
# =============================================================================

class ClaimAnalyzer:
    """
    Analyzes claims for perturbations based on the ACL 2025 paper taxonomy.
    
    The paper defines 6 perturbation types that bad actors use to evade
    misinformation detection:
    
    1. CASING: Changing capitalization
       - Low: TrueCasing (normal capitalization)
       - High: ALL UPPERCASE or all lowercase
       
    2. TYPOS: Introducing spelling errors
       - Low: Minor typos (1-2 characters)
       - High: Major typos, slang, abbreviations
       
    3. NEGATION: Adding/removing negations
       - Low: Single negation ("is not")
       - High: Double negation ("is not untrue")
       
    4. ENTITY REPLACEMENT: Swapping names/places
       - Low: 1 entity replaced
       - High: All entities replaced with synonyms
       
    5. LLM REWRITE: Paraphrasing via LLM
       - Low: Minimal rewrite (similar words)
       - High: Complete rewrite (same meaning, different words)
       
    6. DIALECT: Rewriting in different dialects
       - African American English (AAE)
       - Nigerian Pidgin
       - Singlish
       - Jamaican Patois
    """
    
    def __init__(self):
        """Initialize the claim analyzer with detection patterns"""
        
        # =====================================================================
        # CASING DETECTION PATTERNS
        # =====================================================================
        
        self.casing_patterns = {
            'all_caps': r'^[A-Z\s\d\W]+$',  # ALL UPPERCASE
            'all_lower': r'^[a-z\s\d\W]+$',  # all lowercase
            'mixed_unusual': r'[a-z]+[A-Z]+[a-z]+',  # wEiRd CaPiTaLiZaTiOn
        }
        
        # =====================================================================
        # TYPO DETECTION PATTERNS
        # =====================================================================
        
        # Common intentional misspellings used to evade detection
        self.typo_patterns = {
            # Leetspeak substitutions
            'leetspeak': [
                (r'0', 'o'), (r'1', 'i'), (r'3', 'e'), (r'4', 'a'),
                (r'5', 's'), (r'7', 't'), (r'@', 'a'), (r'\$', 's'),
            ],
            # Common slang/abbreviations
            'slang': [
                'ur', 'u', 'r', 'b4', '2', '4', 'w/', 'w/o', 'bc', 'cuz',
                'tho', 'thru', 'ppl', 'govt', 'yr', 'yrs', 'msg', 'msgs',
            ],
            # Deliberate misspellings of sensitive words
            'evasion_spellings': [
                (r'vax+ine', 'vaccine'), (r'vaxx', 'vaccine'),
                (r'c0vid', 'covid'), (r'cov1d', 'covid'),
                (r'v1rus', 'virus'), (r'pan+demic', 'pandemic'),
            ],
        }
        
        # =====================================================================
        # NEGATION DETECTION PATTERNS
        # =====================================================================
        
        self.negation_patterns = {
            # Single negation (low noise)
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
            # Double negation (high noise)
            'double': [
                r'\b(not\s+un\w+)\b',  # "not untrue", "not unhappy"
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
        
        # =====================================================================
        # ENTITY REPLACEMENT PATTERNS
        # =====================================================================
        
        # Common entity replacements in misinformation
        self.entity_replacements = {
            # Political figures (examples)
            'political': {
                'synonyms': [
                    ('president', ['POTUS', 'the administration', 'the leader', 'the head of state']),
                    ('government', ['govt', 'the state', 'authorities', 'officials']),
                    ('congress', ['the legislature', 'lawmakers', 'parliament']),
                ],
            },
            # Organizations
            'organizations': {
                'synonyms': [
                    ('WHO', ['World Health Organization', 'the health agency', 'global health body']),
                    ('CDC', ['Centers for Disease Control', 'the health department', 'disease control']),
                    ('FDA', ['Food and Drug Administration', 'drug regulators', 'the agency']),
                ],
            },
            # Locations
            'locations': {
                'synonyms': [
                    ('China', ['the PRC', 'the mainland', 'the country', 'that nation']),
                    ('USA', ['America', 'the US', 'the States', 'the country']),
                ],
            },
        }
        
        # =====================================================================
        # DIALECT PATTERNS
        # =====================================================================
        
        # Markers for different dialects
        self.dialect_markers = {
            'aae': [  # African American English
                r'\bfinna\b', r'\bion\b', r'\baint\b', r"\bain't\b",
                r'\bgon\b', r'\bgonna\b', r'\btryna\b', r'\bwanna\b',
                r'\bbruh\b', r'\bfam\b', r'\bbet\b', r'\bcap\b',
                r'\bno cap\b', r'\bfr\b', r'\bong\b', r'\bfasho\b',
            ],
            'nigerian_pidgin': [  # Nigerian Pidgin
                r'\bwetin\b', r'\bdey\b', r'\bna\b', r'\bwahala\b',
                r'\bsabi\b', r'\bpalava\b', r'\bdem\b', r'\bfor\b',
                r'\bno be\b', r'\bsharp sharp\b', r'\babi\b',
            ],
            'singlish': [  # Singlish (Singapore English)
                r'\blah\b', r'\bleh\b', r'\blor\b', r'\bhor\b',
                r'\bmeh\b', r'\bsibo\b', r'\bwalao\b', r'\bsian\b',
                r'\bchiong\b', r'\bkiasu\b', r'\bbo jio\b',
            ],
            'jamaican_patois': [  # Jamaican Patois
                r'\bwah gwaan\b', r'\bmi\b', r'\bdem\b', r'\byuh\b',
                r'\bweh\b', r'\bfi\b', r'\binna\b', r'\boutta\b',
                r'\bbigup\b', r'\bsmaddy\b', r'\bnuh\b',
            ],
        }
        
        # =====================================================================
        # LLM REWRITE INDICATORS
        # =====================================================================
        
        # Phrases that often indicate LLM rewriting
        self.llm_rewrite_indicators = [
            # Formal transitions often added by LLMs
            r'\b(furthermore|moreover|additionally|consequently)\b',
            r'\b(it is worth noting that|it should be noted that)\b',
            r'\b(in conclusion|to summarize|in summary)\b',
            r'\b(on the other hand|conversely|alternatively)\b',
            # Hedging language often added by LLMs
            r'\b(it appears that|it seems that|it is suggested that)\b',
            r'\b(some experts believe|according to sources)\b',
            r'\b(it could be argued that|one might argue that)\b',
        ]
        
        print("📊 Claim Analyzer initialized!")
        print("   Based on: 'When Claims Evolve' (ACL 2025)")
        print("   Perturbation types: 6")
        print("   Ready for claim analysis")
    
    # =========================================================================
    # MAIN ANALYSIS METHOD
    # =========================================================================
    
    def analyze(self, claim: str, original_claim: Optional[str] = None) -> ClaimAnalysisResult:
        """
        Analyze a claim for perturbations
        
        Args:
            claim: The claim to analyze
            original_claim: Optional original claim for comparison
            
        Returns:
            ClaimAnalysisResult with detected perturbations
        """
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
        
        # Calculate overall metrics
        is_perturbed = len(perturbations) > 0
        overall_confidence = max([p.confidence for p in perturbations]) if perturbations else 0.0
        normalized = self._normalize_claim(claim)
        robustness = self._calculate_robustness_score(claim, perturbations)
        
        # Generate recommendations
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
    
    # =========================================================================
    # PERTURBATION DETECTION METHODS
    # =========================================================================
    
    def _check_casing(self, claim: str) -> Optional[PerturbationResult]:
        """Check for casing perturbations"""
        
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        # Check for all caps
        if re.match(self.casing_patterns['all_caps'], claim):
            evidence.append("Entire claim is in UPPERCASE")
            noise_budget = NoiseBudget.HIGH
            confidence = 0.9
        
        # Check for all lowercase (when proper nouns should be capitalized)
        elif re.match(self.casing_patterns['all_lower'], claim):
            # Check if there are words that should be capitalized
            if re.search(r'\b(i|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', claim):
                evidence.append("Claim is all lowercase, missing expected capitals")
                noise_budget = NoiseBudget.HIGH
                confidence = 0.7
        
        # Check for weird mixed casing
        elif re.search(self.casing_patterns['mixed_unusual'], claim):
            evidence.append("Unusual mixed casing detected (e.g., wEiRd)")
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
                explanation=f"Casing perturbation detected: {', '.join(evidence)}"
            )
        
        return None
    
    def _check_typos(self, claim: str) -> Optional[PerturbationResult]:
        """Check for typo perturbations including leetspeak and slang"""
        
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        
        # Check for leetspeak
        leetspeak_count = 0
        for pattern, replacement in self.typo_patterns['leetspeak']:
            if re.search(pattern, claim):
                leetspeak_count += 1
                evidence.append(f"Leetspeak character: '{pattern}' (should be '{replacement}')")
        
        if leetspeak_count >= 3:
            noise_budget = NoiseBudget.HIGH
            confidence = max(confidence, 0.85)
        elif leetspeak_count >= 1:
            confidence = max(confidence, 0.6)
        
        # Check for slang
        claim_lower = claim.lower()
        slang_found = []
        for slang in self.typo_patterns['slang']:
            if re.search(rf'\b{slang}\b', claim_lower):
                slang_found.append(slang)
        
        if slang_found:
            evidence.append(f"Slang/abbreviations found: {', '.join(slang_found)}")
            if len(slang_found) >= 3:
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.8)
            else:
                confidence = max(confidence, 0.5)
        
        # Check for evasion spellings
        for pattern, correct in self.typo_patterns['evasion_spellings']:
            if re.search(pattern, claim_lower):
                evidence.append(f"Evasion spelling detected: '{pattern}' (evading '{correct}')")
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
                explanation=f"Typo perturbation detected: {len(evidence)} patterns found"
            )
        
        return None
    
    def _check_negation(self, claim: str) -> Optional[PerturbationResult]:
        """Check for negation perturbations"""
        
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        claim_lower = claim.lower()
        
        # Check for double negation first (higher priority)
        for pattern in self.negation_patterns['double']:
            matches = re.findall(pattern, claim_lower)
            if matches:
                evidence.append(f"Double negation: '{matches[0]}'")
                noise_budget = NoiseBudget.HIGH
                confidence = max(confidence, 0.9)
        
        # Check for single negation
        negation_count = 0
        for pattern in self.negation_patterns['single']:
            matches = re.findall(pattern, claim_lower)
            negation_count += len(matches)
        
        if negation_count >= 3 and noise_budget != NoiseBudget.HIGH:
            evidence.append(f"Multiple negations in claim: {negation_count} found")
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
                explanation=f"Negation perturbation: {noise_budget.value} noise budget"
            )
        
        return None
    
    def _check_entity_replacement(self, claim: str) -> Optional[PerturbationResult]:
        """Check for entity replacement perturbations"""
        
        evidence = []
        noise_budget = NoiseBudget.LOW
        confidence = 0.0
        claim_lower = claim.lower()
        
        replacement_count = 0
        
        # Check for synonym replacements
        for category, data in self.entity_replacements.items():
            for original, synonyms in data['synonyms']:
                for synonym in synonyms:
                    if synonym.lower() in claim_lower:
                        evidence.append(f"Possible replacement: '{synonym}' (original: '{original}')")
                        replacement_count += 1
        
        if replacement_count >= 3:
            noise_budget = NoiseBudget.HIGH
            confidence = 0.8
        elif replacement_count >= 1:
            noise_budget = NoiseBudget.LOW
            confidence = 0.5
        
        # Check for vague references
        vague_patterns = [
            r'\b(that country|the country|that nation)\b',
            r'\b(the agency|the organization|the group)\b',
            r'\b(the leader|the official|the authorities)\b',
            r'\b(some experts|sources say|according to reports)\b',
        ]
        
        for pattern in vague_patterns:
            if re.search(pattern, claim_lower):
                evidence.append(f"Vague entity reference: '{pattern}'")
                confidence = max(confidence, 0.6)
        
        if evidence:
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.ENTITY_REPLACEMENT,
                noise_budget=noise_budget,
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,  # Entity normalization would require external knowledge
                explanation=f"Entity replacement detected: {replacement_count} potential swaps"
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
                    evidence.append(f"Dialect markers for {dialect.upper()}: {', '.join(matches)}")
                    confidence = max(confidence, 0.85)
                elif len(matches) == 1:
                    evidence.append(f"Possible {dialect.upper()} marker: {matches[0]}")
                    confidence = max(confidence, 0.4)
        
        if evidence:
            dialect_names = {
                'aae': 'African American English (AAE)',
                'nigerian_pidgin': 'Nigerian Pidgin',
                'singlish': 'Singlish (Singapore English)',
                'jamaican_patois': 'Jamaican Patois',
            }
            
            return PerturbationResult(
                original_claim=claim,
                perturbation_type=PerturbationType.DIALECT,
                noise_budget=NoiseBudget.HIGH,  # Dialect is always high noise
                confidence=confidence,
                evidence=evidence,
                normalized_claim=claim,  # Dialect normalization would require translation
                explanation=f"Dialect perturbation detected: {dialect_names.get(detected_dialect, 'Unknown dialect')}"
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
                evidence.append(f"LLM indicator phrase: '{match.group()}'")
                indicator_count += 1
        
        # LLM rewrites often have balanced sentence structure
        sentences = claim.split('.')
        if len(sentences) >= 3:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
                if variance < 10:  # Very consistent sentence lengths
                    evidence.append("Unusually consistent sentence structure (LLM pattern)")
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
                explanation=f"Possible LLM rewrite: {indicator_count} indicators found"
            )
        
        return None
    
    # =========================================================================
    # NORMALIZATION METHODS
    # =========================================================================
    
    def _normalize_claim(self, claim: str) -> str:
        """
        Normalize a claim to its canonical form
        This is the key to robustness - map all variations to the same form
        """
        normalized = claim
        
        # Fix casing
        normalized = normalized.strip()
        if normalized.isupper():
            normalized = normalized.capitalize()
        
        # Fix leetspeak
        for pattern, replacement in self.typo_patterns['leetspeak']:
            normalized = re.sub(pattern, replacement, normalized)
        
        # Expand common abbreviations
        abbreviation_map = {
            r'\bu\b': 'you',
            r'\bur\b': 'your',
            r'\br\b': 'are',
            r'\bb4\b': 'before',
            r'\bw/\b': 'with',
            r'\bw/o\b': 'without',
            r'\bbc\b': 'because',
            r'\bcuz\b': 'because',
            r'\btho\b': 'though',
            r'\bthru\b': 'through',
            r'\bppl\b': 'people',
            r'\bgovt\b': 'government',
        }
        
        for pattern, replacement in abbreviation_map.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _fix_typos(self, claim: str) -> str:
        """Attempt to fix common typos"""
        fixed = claim
        
        # Fix leetspeak
        for pattern, replacement in self.typo_patterns['leetspeak']:
            fixed = re.sub(pattern, replacement, fixed)
        
        # Fix evasion spellings
        for pattern, correct in self.typo_patterns['evasion_spellings']:
            fixed = re.sub(pattern, correct, fixed, flags=re.IGNORECASE)
        
        return fixed
    
    def _resolve_negation(self, claim: str) -> str:
        """Attempt to resolve double negations"""
        resolved = claim
        
        # Replace common double negations with positive forms
        double_neg_fixes = [
            (r'not\s+untrue', 'true'),
            (r'not\s+incorrect', 'correct'),
            (r'not\s+inaccurate', 'accurate'),
            (r'not\s+impossible', 'possible'),
            (r'never\s+not', 'always'),
        ]
        
        for pattern, replacement in double_neg_fixes:
            resolved = re.sub(pattern, replacement, resolved, flags=re.IGNORECASE)
        
        return resolved
    
    # =========================================================================
    # SCORING AND RECOMMENDATIONS
    # =========================================================================
    
    def _calculate_robustness_score(self, claim: str, perturbations: List[PerturbationResult]) -> float:
        """
        Calculate a robustness score (0-1)
        Higher = more robust (less affected by perturbations)
        """
        if not perturbations:
            return 1.0  # No perturbations = fully robust
        
        # Start with base score
        score = 1.0
        
        for p in perturbations:
            # High noise perturbations reduce score more
            if p.noise_budget == NoiseBudget.HIGH:
                penalty = 0.2 * p.confidence
            else:
                penalty = 0.1 * p.confidence
            
            score -= penalty
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(self, perturbations: List[PerturbationResult]) -> List[str]:
        """Generate recommendations based on detected perturbations"""
        
        if not perturbations:
            return ["No perturbations detected. Claim appears in canonical form."]
        
        recommendations = []
        
        for p in perturbations:
            if p.perturbation_type == PerturbationType.CASING:
                recommendations.append("Normalize casing before processing")
            elif p.perturbation_type == PerturbationType.TYPOS:
                recommendations.append("Apply typo correction and normalize spelling")
            elif p.perturbation_type == PerturbationType.NEGATION:
                recommendations.append("Carefully parse negation logic - check for double negatives")
            elif p.perturbation_type == PerturbationType.ENTITY_REPLACEMENT:
                recommendations.append("Resolve entity references to canonical names")
            elif p.perturbation_type == PerturbationType.LLM_REWRITE:
                recommendations.append("Extract core claim meaning - text may be paraphrased")
            elif p.perturbation_type == PerturbationType.DIALECT:
                recommendations.append("Translate dialect to standard form before matching")
        
        recommendations.append("Compare normalized claim against fact-check database")
        
        return recommendations
    
    # =========================================================================
    # TESTING AND DEMONSTRATION
    # =========================================================================
    
    def demo_perturbations(self) -> Dict[str, List[str]]:
        """
        Generate example perturbations for each type
        Useful for demonstrations and testing
        """
        
        original = "The COVID-19 vaccine is safe and effective according to the CDC."
        
        return {
            "original": [original],
            "casing_low": [
                "the covid-19 vaccine is safe and effective according to the cdc."
            ],
            "casing_high": [
                "THE COVID-19 VACCINE IS SAFE AND EFFECTIVE ACCORDING TO THE CDC."
            ],
            "typos_low": [
                "The COVID-19 vacine is safe and effective according to the CDC."
            ],
            "typos_high": [
                "Th3 C0VID-19 vaxx is safe & effective according 2 the CDC lol"
            ],
            "negation_low": [
                "The COVID-19 vaccine is not unsafe according to the CDC."
            ],
            "negation_high": [
                "It is not untrue that the COVID-19 vaccine is not ineffective according to the CDC."
            ],
            "entity_low": [
                "The COVID-19 vaccine is safe and effective according to the health agency."
            ],
            "entity_high": [
                "The shot is safe and effective according to that government organization."
            ],
            "llm_rewrite_low": [
                "According to the CDC, the COVID-19 vaccine has been deemed safe and effective."
            ],
            "llm_rewrite_high": [
                "It is worth noting that, according to statements from the Centers for Disease Control and Prevention, the vaccine developed for COVID-19 has been determined to be both safe for public use and effective in preventing the disease."
            ],
            "dialect_aae": [
                "The COVID vaccine be safe and effective fr fr no cap, CDC said so"
            ],
            "dialect_nigerian_pidgin": [
                "Na true talk, the COVID vaccine dey safe and e dey work well, na wetin CDC talk"
            ],
        }


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLAIM ANALYZER - TEST SUITE")
    print("Based on: 'When Claims Evolve' (ACL 2025)")
    print("="*70 + "\n")
    
    analyzer = ClaimAnalyzer()
    
    # Get demo perturbations
    demos = analyzer.demo_perturbations()
    
    print("Testing perturbation detection...\n")
    print("-" * 70)
    
    # Test each demo
    for category, claims in demos.items():
        for claim in claims:
            result = analyzer.analyze(claim)
            
            # Determine display
            if result.is_perturbed:
                types = [p.perturbation_type.value for p in result.perturbations_detected]
                budgets = [p.noise_budget.value for p in result.perturbations_detected]
                status = f"⚠️  PERTURBED: {', '.join(types)} ({', '.join(budgets)} noise)"
            else:
                status = "✅ CLEAN"
            
            print(f"\n📝 Category: {category}")
            print(f"   Claim: \"{claim[:60]}{'...' if len(claim) > 60 else ''}\"")
            print(f"   {status}")
            print(f"   Robustness Score: {result.robustness_score:.0%}")
            
            if result.is_perturbed:
                print(f"   Normalized: \"{result.normalized_claim[:60]}...\"")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")