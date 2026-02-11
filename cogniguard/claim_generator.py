"""
=============================================================================
CLAIM GENERATOR - Implements the Transformation Function t_b(q)
=============================================================================

MATHEMATICAL FORMULA:
    q'_{t,b} = t_b(q)
    
WHERE:
    q   = Original claim (input text)
    q'  = Perturbed claim (disguised text)
    t   = Perturbation type (CASING, TYPOS, etc.)
    b   = Noise budget (LOW or HIGH)
    t_b = Transformation function

WHAT THIS FILE DOES:
    Takes a normal sentence and "disguises" it in various ways.
    
EXAMPLE:
    Input:  "The vaccine is safe"
    Type:   TYPOS
    Budget: HIGH
    Output: "Th3 v4ccin3 is s4f3"

WHY WE NEED THIS:
    1. To generate test cases for our detection system
    2. To create training data for machine learning
    3. To understand how attackers modify text
=============================================================================
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict
import random
import re


# =============================================================================
# PERTURBATION TYPES (These match claim_analyzer.py)
# =============================================================================

class PerturbationType(Enum):
    """
    The 6 types of text perturbation (t in the formula)
    
    Each type represents a different way to "disguise" text.
    """
    CASING = "casing"           # Change letter case (ALL CAPS, lowercase)
    TYPOS = "typos"             # Leetspeak and misspellings (v4ccine)
    NEGATION = "negation"       # Add confusing negatives (not unsafe)
    ENTITY = "entity"           # Replace names with vague references
    LLM_REWRITE = "llm_rewrite" # Rewrite in AI-style language
    DIALECT = "dialect"         # Add dialect markers (fr fr, no cap)


class NoiseBudget(Enum):
    """
    How much to change the text (b in the formula)
    
    LOW  = Small changes (still easy to read)
    HIGH = Big changes (heavily disguised)
    """
    LOW = "low"
    HIGH = "high"


# =============================================================================
# RESULT DATACLASS
# =============================================================================

@dataclass
class GenerationResult:
    """
    Result of applying a perturbation
    """
    original: str               # The original text (q)
    perturbed: str              # The disguised text (q')
    perturbation_type: PerturbationType  # Which disguise type (t)
    noise_budget: NoiseBudget   # How much change (b)
    changes_made: List[str]     # List of specific changes
    formula: str                # The mathematical notation


# =============================================================================
# MAIN GENERATOR CLASS
# =============================================================================

class ClaimGenerator:
    """
    Implements the transformation function: q' = t_b(q)
    
    USAGE:
        generator = ClaimGenerator()
        
        # Generate a single perturbation
        result = generator.transform(
            q="The vaccine is safe",
            t=PerturbationType.TYPOS,
            b=NoiseBudget.HIGH
        )
        print(result.perturbed)  # "Th3 v4ccin3 is s4f3"
        
        # Generate all possible perturbations
        all_results = generator.generate_all("The vaccine is safe")
    """
    
    def __init__(self):
        """Initialize the generator with all transformation rules"""
        
        print("🧬 Loading Claim Generator...")
        
        # ═══════════════════════════════════════════════════════════════
        # LEETSPEAK MAPPINGS (for TYPOS perturbation)
        # ═══════════════════════════════════════════════════════════════
        
        self.leetspeak_map = {
            'a': '4',
            'e': '3',
            'i': '1',
            'o': '0',
            's': '5',
            't': '7',
            'b': '8',
            'g': '9',
        }
        
        # ═══════════════════════════════════════════════════════════════
        # ENTITY REPLACEMENTS (for ENTITY perturbation)
        # ═══════════════════════════════════════════════════════════════
        
        self.entity_replacements = {
            # Organizations
            'cdc': 'the health agency',
            'who': 'the global health organization',
            'fda': 'the regulatory agency',
            'nih': 'the research institute',
            
            # People
            'dr.': 'the expert',
            'doctor': 'the medical professional',
            'scientist': 'the researcher',
            'professor': 'the academic',
            
            # Companies
            'pfizer': 'the pharmaceutical company',
            'moderna': 'the biotech company',
            'johnson': 'the healthcare company',
            
            # Places
            'america': 'that country',
            'united states': 'that nation',
            'china': 'the eastern nation',
            'europe': 'the continent',
        }
        
        # ═══════════════════════════════════════════════════════════════
        # LLM PHRASES (for LLM_REWRITE perturbation)
        # ═══════════════════════════════════════════════════════════════
        
        self.llm_prefixes = [
            "It is worth noting that ",
            "Furthermore, ",
            "Moreover, ",
            "It is important to understand that ",
            "From a factual standpoint, ",
            "According to available evidence, ",
            "It should be emphasized that ",
            "Taking into consideration the facts, ",
        ]
        
        self.llm_suffixes = [
            " This is supported by evidence.",
            " This has been well-documented.",
            " This is widely accepted.",
            ", as research has shown.",
            ", according to experts.",
            " This is a factual statement.",
        ]
        
        # ═══════════════════════════════════════════════════════════════
        # DIALECT MARKERS (for DIALECT perturbation)
        # ═══════════════════════════════════════════════════════════════
        
        self.dialect_markers = {
            "aae": {  # African American English
                "is": "be",
                "are": "be",
                "very": "hella",
                "really": "deadass",
                "true": "fr fr",
                "yes": "no cap",
                "good": "bussin",
            },
            "nigerian_pidgin": {
                "is": "dey",
                "it is": "na",
                "what": "wetin",
                "problem": "wahala",
                "yes": "na so",
            },
            "singlish": {
                "very": "damn",
                "right": "lah",
                "you know": "hor",
                "already": "liao",
            }
        }
        
        print("   ✅ Claim Generator ready!")
        print(f"   📊 Perturbation types: {len(PerturbationType)}")
        print(f"   📊 Noise budgets: {len(NoiseBudget)}")
        print()
    
    # =========================================================================
    # MAIN TRANSFORMATION METHOD
    # =========================================================================
    
    def transform(self, 
                  q: str, 
                  t: PerturbationType, 
                  b: NoiseBudget) -> GenerationResult:
        """
        Apply transformation t with budget b to claim q
        
        FORMULA: q' = t_b(q)
        
        Args:
            q: Original claim (the input text)
            t: Perturbation type (which disguise to use)
            b: Noise budget (how much to change)
            
        Returns:
            GenerationResult with the perturbed text and details
        """
        
        # Route to the appropriate transformation method
        if t == PerturbationType.CASING:
            perturbed, changes = self._apply_casing(q, b)
        
        elif t == PerturbationType.TYPOS:
            perturbed, changes = self._apply_typos(q, b)
        
        elif t == PerturbationType.NEGATION:
            perturbed, changes = self._apply_negation(q, b)
        
        elif t == PerturbationType.ENTITY:
            perturbed, changes = self._apply_entity(q, b)
        
        elif t == PerturbationType.LLM_REWRITE:
            perturbed, changes = self._apply_llm_rewrite(q, b)
        
        elif t == PerturbationType.DIALECT:
            perturbed, changes = self._apply_dialect(q, b)
        
        else:
            perturbed = q
            changes = ["No transformation applied"]
        
        # Create the formula notation
        formula = f"q'_{{{t.value},{b.value}}} = t_{b.value}(\"{q[:20]}...\")"
        
        return GenerationResult(
            original=q,
            perturbed=perturbed,
            perturbation_type=t,
            noise_budget=b,
            changes_made=changes,
            formula=formula
        )
    
    # =========================================================================
    # INDIVIDUAL TRANSFORMATION METHODS
    # =========================================================================
    
    def _apply_casing(self, q: str, b: NoiseBudget) -> tuple:
        """
        Apply CASING perturbation
        
        LOW:  lowercase everything
        HIGH: UPPERCASE EVERYTHING
        """
        changes = []
        
        if b == NoiseBudget.LOW:
            perturbed = q.lower()
            changes.append("Converted to lowercase")
        else:  # HIGH
            perturbed = q.upper()
            changes.append("Converted to UPPERCASE")
        
        return perturbed, changes
    
    def _apply_typos(self, q: str, b: NoiseBudget) -> tuple:
        """
        Apply TYPOS (leetspeak) perturbation
        
        LOW:  Replace 2-3 characters
        HIGH: Replace all possible characters
        """
        changes = []
        perturbed = q
        
        if b == NoiseBudget.LOW:
            # Low noise: only replace a few characters
            count = 0
            max_replacements = 3
            
            for char, leet in self.leetspeak_map.items():
                if count >= max_replacements:
                    break
                if char in perturbed.lower():
                    # Replace first occurrence only
                    perturbed = perturbed.replace(char, leet, 1)
                    perturbed = perturbed.replace(char.upper(), leet, 1)
                    changes.append(f"'{char}' → '{leet}'")
                    count += 1
        
        else:  # HIGH
            # High noise: replace ALL possible characters
            for char, leet in self.leetspeak_map.items():
                if char in perturbed.lower():
                    original = perturbed
                    perturbed = perturbed.replace(char, leet)
                    perturbed = perturbed.replace(char.upper(), leet)
                    if perturbed != original:
                        changes.append(f"All '{char}' → '{leet}'")
        
        return perturbed, changes
    
    def _apply_negation(self, q: str, b: NoiseBudget) -> tuple:
        """
        Apply NEGATION perturbation
        
        LOW:  Add single negation (safe → not unsafe)
        HIGH: Add double negation (safe → not not safe)
        """
        changes = []
        perturbed = q
        
        # Common replacements
        negation_pairs = {
            " is ": " is not un",
            " are ": " are not un",
            " was ": " was not un",
            " were ": " were not un",
            " has ": " has not un",
            " have ": " have not un",
        }
        
        if b == NoiseBudget.LOW:
            # Low noise: simple negation
            for original, replacement in negation_pairs.items():
                if original in perturbed.lower():
                    perturbed = re.sub(
                        original, 
                        replacement, 
                        perturbed, 
                        flags=re.IGNORECASE,
                        count=1
                    )
                    changes.append(f"Added 'not un' negation")
                    break
        
        else:  # HIGH
            # High noise: double negation + word changes
            for original, replacement in negation_pairs.items():
                if original in perturbed.lower():
                    perturbed = re.sub(
                        original, 
                        replacement, 
                        perturbed, 
                        flags=re.IGNORECASE
                    )
                    changes.append(f"Added multiple negations")
            
            # Also change positive words to negative
            word_changes = {
                "safe": "unsafe",
                "effective": "ineffective",
                "true": "untrue",
                "correct": "incorrect",
            }
            for word, negative in word_changes.items():
                if word in perturbed.lower():
                    perturbed = re.sub(
                        word, 
                        negative, 
                        perturbed, 
                        flags=re.IGNORECASE,
                        count=1
                    )
                    changes.append(f"'{word}' → '{negative}'")
        
        return perturbed, changes
    
    def _apply_entity(self, q: str, b: NoiseBudget) -> tuple:
        """
        Apply ENTITY perturbation (replace names with vague references)
        
        LOW:  Replace 1-2 entities
        HIGH: Replace all possible entities
        """
        changes = []
        perturbed = q
        
        if b == NoiseBudget.LOW:
            # Low noise: replace only first match
            count = 0
            for entity, vague in self.entity_replacements.items():
                if count >= 2:
                    break
                if entity in perturbed.lower():
                    perturbed = re.sub(
                        entity, 
                        vague, 
                        perturbed, 
                        flags=re.IGNORECASE,
                        count=1
                    )
                    changes.append(f"'{entity}' → '{vague}'")
                    count += 1
        
        else:  # HIGH
            # High noise: replace ALL entities
            for entity, vague in self.entity_replacements.items():
                if entity in perturbed.lower():
                    perturbed = re.sub(
                        entity, 
                        vague, 
                        perturbed, 
                        flags=re.IGNORECASE
                    )
                    changes.append(f"'{entity}' → '{vague}'")
        
        return perturbed, changes
    
    def _apply_llm_rewrite(self, q: str, b: NoiseBudget) -> tuple:
        """
        Apply LLM_REWRITE perturbation (add AI-style language)
        
        LOW:  Add one prefix phrase
        HIGH: Add prefix AND suffix, more formal language
        """
        changes = []
        
        if b == NoiseBudget.LOW:
            # Low noise: just add a prefix
            prefix = random.choice(self.llm_prefixes)
            perturbed = prefix + q.lower()
            changes.append(f"Added prefix: '{prefix.strip()}'")
        
        else:  # HIGH
            # High noise: prefix + suffix + more formal
            prefix = random.choice(self.llm_prefixes)
            suffix = random.choice(self.llm_suffixes)
            
            # Make it more formal
            formal = q.replace("'s", " is").replace("'re", " are")
            
            perturbed = prefix + formal.lower() + suffix
            changes.append(f"Added prefix: '{prefix.strip()}'")
            changes.append(f"Added suffix: '{suffix.strip()}'")
            changes.append("Made language more formal")
        
        return perturbed, changes
    
    def _apply_dialect(self, q: str, b: NoiseBudget, 
                       dialect: str = "aae") -> tuple:
        """
        Apply DIALECT perturbation
        
        LOW:  Replace 1-2 words with dialect
        HIGH: Replace all possible words + add markers
        """
        changes = []
        perturbed = q
        
        dialect_map = self.dialect_markers.get(dialect, self.dialect_markers["aae"])
        
        if b == NoiseBudget.LOW:
            # Low noise: few replacements
            count = 0
            for standard, dialectal in dialect_map.items():
                if count >= 2:
                    break
                if standard in perturbed.lower():
                    perturbed = re.sub(
                        r'\b' + standard + r'\b', 
                        dialectal, 
                        perturbed, 
                        flags=re.IGNORECASE,
                        count=1
                    )
                    changes.append(f"'{standard}' → '{dialectal}'")
                    count += 1
        
        else:  # HIGH
            # High noise: all replacements + add markers at end
            for standard, dialectal in dialect_map.items():
                if standard in perturbed.lower():
                    perturbed = re.sub(
                        r'\b' + standard + r'\b', 
                        dialectal, 
                        perturbed, 
                        flags=re.IGNORECASE
                    )
                    changes.append(f"'{standard}' → '{dialectal}'")
            
            # Add dialect markers at the end
            if dialect == "aae":
                perturbed = perturbed.rstrip('.!?') + " fr fr no cap"
                changes.append("Added 'fr fr no cap'")
            elif dialect == "nigerian_pidgin":
                perturbed = perturbed.rstrip('.!?') + " o"
                changes.append("Added 'o' marker")
        
        return perturbed, changes
    
    # =========================================================================
    # BULK GENERATION METHODS
    # =========================================================================
    
    def generate_all(self, q: str) -> List[GenerationResult]:
        """
        Generate ALL possible perturbations of a claim
        
        Returns a list with 12 results (6 types × 2 budgets)
        """
        results = []
        
        for t in PerturbationType:
            for b in NoiseBudget:
                result = self.transform(q, t, b)
                results.append(result)
        
        return results
    
    def generate_dataset(self, 
                         claims: List[str], 
                         types: List[PerturbationType] = None,
                         budgets: List[NoiseBudget] = None) -> List[Dict]:
        """
        Generate a dataset of perturbed claims
        
        Useful for:
        - Training machine learning models
        - Testing detection systems
        - Research
        
        Args:
            claims: List of original claims
            types: Which perturbation types to use (default: all)
            budgets: Which budgets to use (default: all)
            
        Returns:
            List of dictionaries with all perturbations
        """
        if types is None:
            types = list(PerturbationType)
        if budgets is None:
            budgets = list(NoiseBudget)
        
        dataset = []
        
        for claim in claims:
            for t in types:
                for b in budgets:
                    result = self.transform(claim, t, b)
                    dataset.append({
                        "original": result.original,
                        "perturbed": result.perturbed,
                        "type": result.perturbation_type.value,
                        "budget": result.noise_budget.value,
                        "changes": result.changes_made,
                        "formula": result.formula,
                    })
        
        return dataset


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLAIM GENERATOR - SELF TEST")
    print("Formula: q' = t_b(q)")
    print("="*70 + "\n")
    
    generator = ClaimGenerator()
    
    # Test claim
    q = "The vaccine is safe and effective according to the CDC."
    
    print(f"Original claim (q):\n\"{q}\"\n")
    print("-" * 70)
    
    # Generate all perturbations
    results = generator.generate_all(q)
    
    for result in results:
        print(f"\n📝 {result.perturbation_type.value.upper()} ({result.noise_budget.value})")
        print(f"   Formula: {result.formula}")
        print(f"   Result: \"{result.perturbed[:60]}...\"")
        print(f"   Changes: {result.changes_made}")
    
    print("\n" + "="*70)
    print("✅ Claim Generator test complete!")
    print("="*70 + "\n")