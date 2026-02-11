"""
=============================================================================
CLAIM CONSTRAINT - Implements the Semantic Constraint C(q, q', v)
=============================================================================

MATHEMATICAL FORMULA:
    C(q, q', v) = true
    
WHERE:
    q   = Original claim
    q'  = Perturbed claim
    v   = Veracity (truth value) of the claim
    C   = Constraint function that checks if meaning is preserved

WHAT THIS FILE DOES:
    Verifies that a perturbed claim still means the same thing as the original.
    
WHY THIS MATTERS:
    A good perturbation should DISGUISE the text but not CHANGE its meaning.
    
    Good perturbation:
        q  = "The vaccine is safe"
        q' = "Th3 v4ccine is s4fe"
        C(q, q', v) = TRUE ✅ (same meaning, different spelling)
    
    Bad perturbation:
        q  = "The vaccine is safe"
        q' = "The vaccine is dangerous"
        C(q, q', v) = FALSE ❌ (different meaning!)

HOW IT WORKS:
    Uses semantic similarity (AI embeddings) to compare meanings.
    If similarity > threshold, constraint is satisfied.
=============================================================================
"""

from dataclasses import dataclass
from typing import Optional, Dict
import numpy as np


# =============================================================================
# RESULT DATACLASS
# =============================================================================

@dataclass
class ConstraintResult:
    """
    Result of checking the constraint C(q, q', v)
    """
    original: str               # q
    perturbed: str              # q'
    similarity: float           # How similar they are (0.0 to 1.0)
    threshold: float            # The minimum required similarity
    constraint_satisfied: bool  # Is C(q, q', v) = true?
    explanation: str            # Human-readable explanation
    formula: str                # Mathematical notation


# =============================================================================
# MAIN CONSTRAINT CLASS
# =============================================================================

class ClaimConstraint:
    """
    Implements the constraint function: C(q, q', v) = true
    
    This checks if a perturbed claim preserves the meaning of the original.
    
    USAGE:
        constraint = ClaimConstraint()
        
        # Check if perturbation preserves meaning
        result = constraint.verify(
            q="The vaccine is safe",
            q_prime="Th3 v4ccine is s4fe"
        )
        
        if result.constraint_satisfied:
            print("✅ Meaning preserved!")
        else:
            print("❌ Meaning changed!")
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.70,
                 use_semantic: bool = True):
        """
        Initialize the constraint checker
        
        Args:
            similarity_threshold: Minimum similarity for constraint to pass (0.0 to 1.0)
                                 0.70 means "at least 70% similar"
            use_semantic: Use AI embeddings for comparison (requires sentence-transformers)
        """
        
        print("🔒 Loading Claim Constraint Checker...")
        print(f"   Threshold: {similarity_threshold:.0%} similarity required")
        
        self.threshold = similarity_threshold
        self.use_semantic = use_semantic
        self.model = None
        
        # Try to load the semantic model
        if use_semantic:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("   ✅ Semantic model loaded!")
            except ImportError:
                print("   ⚠️ sentence-transformers not installed")
                print("   ⚠️ Falling back to basic text comparison")
                self.use_semantic = False
        
        print("   ✅ Constraint Checker ready!\n")
    
    # =========================================================================
    # MAIN VERIFICATION METHODS
    # =========================================================================
    
    def verify(self, q: str, q_prime: str) -> ConstraintResult:
        """
        Verify if C(q, q', v) = true
        
        This is the main method that checks if the perturbed text
        still means the same thing as the original.
        
        Args:
            q: Original claim
            q_prime: Perturbed claim
            
        Returns:
            ConstraintResult with the verification details
        """
        
        # Calculate similarity
        if self.use_semantic and self.model is not None:
            similarity = self._semantic_similarity(q, q_prime)
            method = "semantic"
        else:
            similarity = self._basic_similarity(q, q_prime)
            method = "basic"
        
        # Check if constraint is satisfied
        constraint_satisfied = similarity >= self.threshold
        
        # Generate explanation
        if constraint_satisfied:
            explanation = (
                f"✅ Constraint SATISFIED. "
                f"Similarity ({similarity:.0%}) >= threshold ({self.threshold:.0%}). "
                f"The perturbed text preserves the original meaning."
            )
        else:
            explanation = (
                f"❌ Constraint VIOLATED. "
                f"Similarity ({similarity:.0%}) < threshold ({self.threshold:.0%}). "
                f"The perturbed text may have changed the meaning."
            )
        
        # Create formula notation
        formula = f"C(q, q', v) = {str(constraint_satisfied).lower()}"
        
        return ConstraintResult(
            original=q,
            perturbed=q_prime,
            similarity=similarity,
            threshold=self.threshold,
            constraint_satisfied=constraint_satisfied,
            explanation=explanation,
            formula=formula
        )
    
    def verify_batch(self, pairs: list) -> list:
        """
        Verify multiple (q, q') pairs at once
        
        Args:
            pairs: List of (original, perturbed) tuples
            
        Returns:
            List of ConstraintResult objects
        """
        results = []
        for q, q_prime in pairs:
            result = self.verify(q, q_prime)
            results.append(result)
        return results
    
    # =========================================================================
    # SIMILARITY CALCULATION METHODS
    # =========================================================================
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using AI embeddings
        
        This uses a neural network to understand the MEANING of text,
        not just the surface-level words.
        
        HOW IT WORKS:
        1. Convert each text to a vector of numbers (embedding)
        2. Calculate the cosine of the angle between vectors
        3. Cosine of 1 = identical, 0 = unrelated, -1 = opposite
        """
        
        if self.model is None:
            return self._basic_similarity(text1, text2)
        
        # Get embeddings
        embedding1 = self.model.encode(text1, convert_to_numpy=True)
        embedding2 = self.model.encode(text2, convert_to_numpy=True)
        
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure it's between 0 and 1
        return float(max(0.0, min(1.0, similarity)))
    
    def _basic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate basic similarity without AI
        
        This is a fallback when sentence-transformers isn't available.
        Uses character-level comparison and word overlap.
        """
        
        # Normalize texts
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()
        
        # Method 1: Character-level Jaccard similarity
        set1 = set(t1)
        set2 = set(t2)
        char_similarity = len(set1 & set2) / len(set1 | set2) if set1 | set2 else 0
        
        # Method 2: Word-level Jaccard similarity
        words1 = set(t1.split())
        words2 = set(t2.split())
        word_similarity = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
        
        # Method 3: Length similarity
        len_similarity = min(len(t1), len(t2)) / max(len(t1), len(t2)) if max(len(t1), len(t2)) > 0 else 0
        
        # Combine methods (weighted average)
        combined = (char_similarity * 0.3) + (word_similarity * 0.5) + (len_similarity * 0.2)
        
        return combined
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_stats(self, results: list) -> Dict:
        """
        Get statistics from multiple constraint checks
        """
        if not results:
            return {"total": 0}
        
        satisfied = sum(1 for r in results if r.constraint_satisfied)
        
        return {
            "total": len(results),
            "satisfied": satisfied,
            "violated": len(results) - satisfied,
            "satisfaction_rate": satisfied / len(results),
            "avg_similarity": sum(r.similarity for r in results) / len(results),
        }
    
    def adjust_threshold(self, new_threshold: float):
        """
        Adjust the similarity threshold
        
        Use this to make the constraint stricter or looser.
        """
        if 0 <= new_threshold <= 1:
            self.threshold = new_threshold
            print(f"Threshold adjusted to {new_threshold:.0%}")
        else:
            raise ValueError("Threshold must be between 0 and 1")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLAIM CONSTRAINT - SELF TEST")
    print("Formula: C(q, q', v) = true")
    print("="*70 + "\n")
    
    constraint = ClaimConstraint(similarity_threshold=0.70)
    
    # Test cases
    test_cases = [
        # (original, perturbed, expected_result)
        ("The vaccine is safe", "Th3 v4ccine is s4fe", True),
        ("The vaccine is safe", "THE VACCINE IS SAFE", True),
        ("The vaccine is safe", "The vaccine is dangerous", False),
        ("The vaccine is safe", "Hello world", False),
        ("Climate change is real", "Climat3 chang3 is r34l", True),
    ]
    
    print("Testing constraint verification...\n")
    print("-" * 70)
    
    passed = 0
    
    for q, q_prime, expected in test_cases:
        result = constraint.verify(q, q_prime)
        
        if result.constraint_satisfied == expected:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"\n{status}")
        print(f"  q:  \"{q}\"")
        print(f"  q': \"{q_prime}\"")
        print(f"  Similarity: {result.similarity:.0%}")
        print(f"  {result.formula}")
    
    print("\n" + "-" * 70)
    print(f"\n📊 Results: {passed}/{len(test_cases)} tests passed")
    
    print("\n" + "="*70)
    print("✅ Claim Constraint test complete!")
    print("="*70 + "\n")