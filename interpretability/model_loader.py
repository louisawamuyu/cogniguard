"""
Model Loader - TransformerLens Integration

Loads language models with hooks for extracting internal activations.
Uses TransformerLens for easy access to model internals.
"""

import torch
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Information about a loaded model"""
    name: str
    n_layers: int
    n_heads: int
    d_model: int
    d_head: int
    d_mlp: int
    n_params: int
    device: str


def load_model(
    model_name: str = "gpt2",
    device: Optional[str] = None
) -> Tuple[Any, ModelInfo]:
    """
    Load a model with TransformerLens for interpretability research.
    
    Args:
        model_name: HuggingFace model name or shorthand
            Options: "gpt2", "gpt2-medium", "gpt2-large", "gpt2-xl"
                    "EleutherAI/pythia-70m", "EleutherAI/pythia-160m", etc.
        device: "cuda", "cpu", or None (auto-detect)
    
    Returns:
        Tuple of (model, model_info)
    
    Example:
        model, info = load_model("gpt2")
        print(f"Loaded {info.name} with {info.n_layers} layers")
    """
    
    try:
        from transformer_lens import HookedTransformer
    except ImportError:
        raise ImportError(
            "TransformerLens is required for interpretability research.\n"
            "Install with: pip install transformer-lens"
        )
    
    # Auto-detect device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"🔄 Loading {model_name} on {device}...")
    
    # Load the model with TransformerLens
    model = HookedTransformer.from_pretrained(
        model_name,
        device=device,
        default_padding_side="left"  # Important for batched inference
    )
    
    # Extract model information
    cfg = model.cfg
    info = ModelInfo(
        name=model_name,
        n_layers=cfg.n_layers,
        n_heads=cfg.n_heads,
        d_model=cfg.d_model,
        d_head=cfg.d_head,
        d_mlp=cfg.d_mlp,
        n_params=sum(p.numel() for p in model.parameters()),
        device=device
    )
    
    print(f"✅ Loaded {model_name}")
    print(f"   Layers: {info.n_layers}")
    print(f"   Attention heads: {info.n_heads}")
    print(f"   Model dimension: {info.d_model}")
    print(f"   Parameters: {info.n_params:,}")
    print(f"   Device: {info.device}")
    
    return model, info


def get_model_info(model) -> ModelInfo:
    """Extract ModelInfo from an already-loaded model"""
    cfg = model.cfg
    return ModelInfo(
        name=cfg.model_name,
        n_layers=cfg.n_layers,
        n_heads=cfg.n_heads,
        d_model=cfg.d_model,
        d_head=cfg.d_head,
        d_mlp=cfg.d_mlp,
        n_params=sum(p.numel() for p in model.parameters()),
        device=str(model.cfg.device)
    )


# =============================================================================
# Quick test
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MODEL LOADER TEST")
    print("="*60 + "\n")
    
    model, info = load_model("gpt2")
    
    # Quick forward pass test
    test_text = "Hello, world!"
    tokens = model.to_tokens(test_text)
    logits = model(tokens)
    
    print(f"\n✅ Forward pass successful!")
    print(f"   Input: '{test_text}'")
    print(f"   Tokens shape: {tokens.shape}")
    print(f"   Logits shape: {logits.shape}")