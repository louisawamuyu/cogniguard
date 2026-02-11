"""
Visualization Module - Create Plots for Research Findings

Generates publication-quality visualizations for:
1. Layer-by-layer probe accuracy
2. Activation differences
3. Attention patterns
4. Feature directions
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any
import os


def plot_layer_differences(
    analysis: Any,  # ActivationAnalysis
    title: str = "Activation Similarity: Safe vs Threat",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot cosine similarity across layers.
    
    Shows where in the model safe and threat representations diverge.
    """
    
    layers = list(analysis.layer_differences.keys())
    similarities = [analysis.layer_differences[l].mean_cosine_similarity 
                   for l in layers]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create gradient coloring
    colors = plt.cm.RdYlGn(similarities)
    
    bars = ax.bar(layers, similarities, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Layer', fontsize=12)
    ax.set_ylabel('Cosine Similarity', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='0.5 threshold')
    ax.axhline(y=np.mean(similarities), color='blue', linestyle='--', 
               alpha=0.5, label=f'Mean: {np.mean(similarities):.3f}')
    
    # Mark most different layer
    min_layer = analysis.most_different_layer
    ax.scatter([min_layer], [similarities[min_layer]], 
              color='red', s=100, zorder=5, marker='v')
    ax.annotate(f'Most different\n(Layer {min_layer})', 
               xy=(min_layer, similarities[min_layer]),
               xytext=(min_layer + 1, similarities[min_layer] - 0.1),
               fontsize=10, ha='left')
    
    ax.legend()
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to {save_path}")
    
    return fig


def plot_probe_accuracy(
    probe_analysis: Any,  # ProbeAnalysis
    title: str = "Threat Detection Probe Accuracy by Layer",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot probe accuracy across layers.
    
    Shows at which layer the model "knows" something is a threat.
    """
    
    layers = list(probe_analysis.results_by_layer.keys())
    accuracies = [probe_analysis.results_by_layer[l].accuracy for l in layers]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color based on accuracy
    colors = plt.cm.Greens([a for a in accuracies])
    
    bars = ax.bar(layers, accuracies, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Layer', fontsize=12)
    ax.set_ylabel('Probe Accuracy', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Chance level')
    
    # Mark best layer
    best_layer = probe_analysis.best_layer
    ax.scatter([best_layer], [accuracies[best_layer]], 
              color='gold', s=150, zorder=5, marker='*', edgecolor='black')
    ax.annotate(f'Best: Layer {best_layer}\n({accuracies[best_layer]:.1%})', 
               xy=(best_layer, accuracies[best_layer]),
               xytext=(best_layer + 1, accuracies[best_layer] + 0.05),
               fontsize=10, ha='left', fontweight='bold')
    
    ax.legend()
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to {save_path}")
    
    return fig


def plot_attention_patterns(
    attention: np.ndarray,  # Shape: [n_heads, seq_len, seq_len]
    token_strs: List[str],
    layer: int,
    heads_to_show: Optional[List[int]] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot attention patterns for specific heads.
    """
    
    if heads_to_show is None:
        heads_to_show = list(range(min(4, attention.shape[0])))
    
    n_heads = len(heads_to_show)
    fig, axes = plt.subplots(1, n_heads, figsize=(4 * n_heads, 4))
    
    if n_heads == 1:
        axes = [axes]
    
    for idx, head in enumerate(heads_to_show):
        ax = axes[idx]
        
        im = ax.imshow(attention[head], cmap='Blues', aspect='auto')
        
        ax.set_xticks(range(len(token_strs)))
        ax.set_yticks(range(len(token_strs)))
        ax.set_xticklabels(token_strs, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(token_strs, fontsize=8)
        
        ax.set_xlabel('Key', fontsize=10)
        ax.set_ylabel('Query', fontsize=10)
        ax.set_title(f'Layer {layer}, Head {head}', fontsize=11)
        
        plt.colorbar(im, ax=ax, fraction=0.046)
    
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to {save_path}")
    
    return fig


def create_activation_heatmap(
    activations: np.ndarray,  # Shape: [n_layers, d_model] or similar
    title: str = "Activation Magnitudes",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create a heatmap of activation magnitudes.
    """
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    im = ax.imshow(activations, aspect='auto', cmap='viridis')
    
    ax.set_xlabel('Dimension', fontsize=12)
    ax.set_ylabel('Layer', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Activation')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to {save_path}")
    
    return fig


def create_summary_figure(
    probe_analysis: Any,
    activation_analysis: Any,
    title: str = "CogniGuard Interpretability Analysis",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create a combined summary figure for research presentation.
    """
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Probe accuracy
    ax1 = axes[0]
    layers = list(probe_analysis.results_by_layer.keys())
    accuracies = [probe_analysis.results_by_layer[l].accuracy for l in layers]
    
    ax1.bar(layers, accuracies, color='steelblue', edgecolor='black', linewidth=0.5)
    ax1.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Chance')
    ax1.scatter([probe_analysis.best_layer], [probe_analysis.best_accuracy], 
               color='gold', s=150, marker='*', zorder=5, edgecolor='black')
    
    ax1.set_xlabel('Layer', fontsize=12)
    ax1.set_ylabel('Probe Accuracy', fontsize=12)
    ax1.set_title('A) Threat Detection Accuracy', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.set_ylim(0, 1.1)
    ax1.grid(axis='y', alpha=0.3)
    
    # Right: Activation similarity
    ax2 = axes[1]
    similarities = [activation_analysis.layer_differences[l].mean_cosine_similarity 
                   for l in layers]
    
    colors = plt.cm.RdYlGn(similarities)
    ax2.bar(layers, similarities, color=colors, edgecolor='black', linewidth=0.5)
    
    ax2.set_xlabel('Layer', fontsize=12)
    ax2.set_ylabel('Cosine Similarity', fontsize=12)
    ax2.set_title('B) Safe vs Threat Similarity', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 1)
    ax2.grid(axis='y', alpha=0.3)
    
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to {save_path}")
    
    return fig


# =============================================================================
# Quick test
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("VISUALIZATION TEST")
    print("="*60 + "\n")
    
    # Create mock data for testing
    from dataclasses import dataclass
    
    @dataclass
    class MockLayerDiff:
        layer: int
        mean_cosine_similarity: float
        mean_l2_distance: float
        direction_alignment: float = 0.0
    
    @dataclass
    class MockAnalysis:
        layer_differences: Dict
        most_different_layer: int
        most_similar_layer: int
        overall_divergence_pattern: str
    
    # Create mock activation analysis
    mock_analysis = MockAnalysis(
        layer_differences={
            i: MockLayerDiff(
                layer=i, 
                mean_cosine_similarity=0.8 - 0.05 * i + np.random.random() * 0.1,
                mean_l2_distance=10 + i * 2
            ) 
            for i in range(12)
        },
        most_different_layer=8,
        most_similar_layer=0,
        overall_divergence_pattern="gradual"
    )
    
    # Test plot
    fig = plot_layer_differences(mock_analysis, save_path=None)
    plt.show()
    
    print("✅ Visualization test complete!")