class MechanisticClaimGenerator:
    """
    Extends ClaimGenerator with internal representation analysis.
    """
    
    def __init__(self, model, tokenizer):
        self.surface_generator = ClaimGenerator()  # Keep existing
        self.model = model
        self.tokenizer = tokenizer
    
    def analyze_perturbation_representations(self, claim: str):
        """
        Compare how model internally represents original vs perturbed claims.
        """
        
        # Step 1: Generate all perturbations (existing functionality)
        perturbations = self.surface_generator.generate_all(claim)
        
        # Step 2: Extract activations for each (NEW - requires model)
        activation_map = {}
        for result in perturbations:
            acts = self._extract_activations(result.perturbed)
            activation_map[f"{result.perturbation_type}_{result.noise_budget}"] = acts
        
        # Step 3: Compare representations (NEW - mechanistic analysis)
        original_acts = self._extract_activations(claim)
        
        comparisons = {}
        for key, acts in activation_map.items():
            comparisons[key] = {
                "cosine_similarity": self._cosine_sim(original_acts, acts),
                "l2_distance": self._l2_distance(original_acts, acts),
                "shared_features": self._find_shared_sae_features(original_acts, acts)
            }
        
        return comparisons
    
    def find_perturbation_direction(self, perturbation_type: PerturbationType):
        """
        Find the activation direction that encodes a specific perturbation type.
        
        This would allow causal interventions:
        - Add the "dialect direction" to standard text → model treats as dialect?
        - Remove the "leetspeak direction" from perturbed text → normalizes behavior?
        """
        
        # Collect examples of this perturbation type
        perturbed_acts = []
        original_acts = []
        
        for claim in self.test_claims:
            result = self.surface_generator.transform(
                claim, perturbation_type, NoiseBudget.HIGH
            )
            perturbed_acts.append(self._extract_activations(result.perturbed))
            original_acts.append(self._extract_activations(claim))
        
        # Find the mean difference vector
        perturbation_direction = np.mean(perturbed_acts, axis=0) - np.mean(original_acts, axis=0)
        perturbation_direction = perturbation_direction / np.linalg.norm(perturbation_direction)
        
        return perturbation_direction
    
    def test_perturbation_causality(self, claim: str, 
                                     perturbation_type: PerturbationType,
                                     steering_strength: float):
        """
        Causally test whether the perturbation direction affects behavior.
        
        This is the key mechanistic experiment:
        - If adding the "dialect direction" makes the model behave as if input is dialect
        - Then we've found how the model represents distribution membership
        """
        
        direction = self.find_perturbation_direction(perturbation_type)
        
        # Generate with steering
        steered_output = self._generate_with_steering(claim, direction, steering_strength)
        
        # Generate without steering  
        baseline_output = self.model.generate(claim)
        
        return {
            "baseline": baseline_output,
            "steered": steered_output,
            "direction_norm": np.linalg.norm(direction),
            "behavioral_change": self._quantify_change(baseline_output, steered_output)
        }