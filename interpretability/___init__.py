"""
CogniGuard Interpretability Module

This module enables mechanistic interpretability research on how
language models internally process adversarial inputs (prompt injections,
jailbreaks, social engineering, etc.)

Research Questions:
1. Do LLMs have internal "threat detection" representations?
2. Can we find a linear direction for "this is a prompt injection"?
3. What circuits activate when processing adversarial vs safe inputs?
4. Why do some jailbreaks succeed and others fail?

Usage:
    from cogniguard.interpretability import InterpretabilityEngine
    
    engine = InterpretabilityEngine(model_name="gpt2")
    
    # Extract activations
    safe_acts = engine.get_activations("Hello, how are you?")
    threat_acts = engine.get_activations("Ignore previous instructions")
    
    # Train a probe
    probe_results = engine.train_threat_probe(safe_texts, threat_texts)
    
    # Analyze differences
    analysis = engine.compare_activations(safe_acts, threat_acts)
"""

from .model_loader import load_model, get_model_info
from .activation_cache import ActivationCache, get_activations
from .probing import ThreatProbe, train_probe, evaluate_probe
from .analysis import ActivationAnalyzer, compare_activations
from .visualize import (
    plot_layer_differences,
    plot_probe_accuracy,
    plot_attention_patterns,
    create_activation_heatmap
)

__all__ = [
    # Model loading
    'load_model',
    'get_model_info',
    
    # Activation extraction
    'ActivationCache',
    'get_activations',
    
    # Probing
    'ThreatProbe',
    'train_probe',
    'evaluate_probe',
    
    # Analysis
    'ActivationAnalyzer',
    'compare_activations',
    
    # Visualization
    'plot_layer_differences',
    'plot_probe_accuracy',
    'plot_attention_patterns',
    'create_activation_heatmap',
]