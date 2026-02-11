class MechanisticClaimAnalyzer:
    """
    Extends ClaimAnalyzer with activation-level analysis.
    """
    
    def __init__(self, model, tokenizer):
        self.surface_analyzer = ClaimAnalyzer()  # Keep existing functionality
        self.model = model
        self.tokenizer = tokenizer
        self.activation_cache = {}
    
    def analyze_with_activations(self, claim: str):
        """Analyze both surface perturbations AND internal representations."""
        
        # Step 1: Surface analysis (current ClaimAnalyzer)
        surface_result = self.surface_analyzer.analyze(claim)
        
        # Step 2: Extract activations (NEW - requires model access)
        activations = self._extract_activations(claim)
        
        # Step 3: Check if model internally encodes "out-of-distribution"
        distribution_signal = self._probe_for_distribution_signature(activations)
        
        # Step 4: Test causal effect of perturbation type
        if surface_result.is_perturbed:
            causal_effect = self._test_perturbation_causality(
                claim, 
                surface_result.normalized_claim,
                surface_result.perturbations_detected
            )
        
        return {
            "surface_analysis": surface_result,
            "activations": activations,
            "distribution_signal": distribution_signal,
            "causal_effect": causal_effect
        }
    
    def _extract_activations(self, claim: str) -> Dict[str, np.ndarray]:
        """Extract activations at each layer."""
        tokens = self.tokenizer(claim, return_tensors="pt")
        
        activations = {}
        
        def hook_fn(name):
            def hook(module, input, output):
                activations[name] = output.detach().cpu().numpy()
            return hook
        
        # Register hooks on all layers
        handles = []
        for name, module in self.model.named_modules():
            if "layer" in name:
                handles.append(module.register_forward_hook(hook_fn(name)))
        
        # Forward pass
        with torch.no_grad():
            self.model(**tokens)
        
        # Remove hooks
        for handle in handles:
            handle.remove()
        
        return activations
    
    def _probe_for_distribution_signature(self, activations: Dict) -> Dict:
        """Train/apply probes to detect distribution encoding."""
        
        # This would require a trained probe that predicts:
        # "Is this input from the RLHF distribution or not?"
        
        # Example implementation:
        probe_input = activations["layer.0"]  # Early layer activations
        
        # Apply pre-trained linear probe
        distribution_logits = self.distribution_probe(probe_input)
        
        return {
            "predicted_distribution": "rlhf" if distribution_logits > 0 else "base",
            "confidence": torch.sigmoid(distribution_logits).item()
        }
    
    def _test_perturbation_causality(self, perturbed_claim: str, 
                                      normalized_claim: str,
                                      perturbations: List) -> Dict:
        """Test whether surface perturbations causally affect behavior."""
        
        # Generate outputs for both versions
        perturbed_output = self.model.generate(perturbed_claim)
        normalized_output = self.model.generate(normalized_claim)
        
        # Compare
        return {
            "perturbed_output": perturbed_output,
            "normalized_output": normalized_output,
            "behavioral_difference": self._quantify_difference(
                perturbed_output, normalized_output
            ),
            "perturbation_types": [p.perturbation_type.value for p in perturbations]
        }