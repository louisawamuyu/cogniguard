# ============================================
# MATS APPLICATION: PERTURBATION INTERPRETABILITY EXPERIMENT
# ============================================
# Author: Louisa Wamuyu Saburi
# Date: 20/12/2025
# Time tracking: Started at 9:25 am
# ============================================

print("="*60)
print("PERTURBATION INTERPRETABILITY EXPERIMENT")
print("="*60)

# --------------------------------------------
# STEP 1: Import all required libraries
# --------------------------------------------
print("\n📦 Importing libraries...")

import torch
import numpy as np
import matplotlib.pyplot as plt
from transformer_lens import HookedTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy.spatial.distance import cosine
import warnings
warnings.filterwarnings('ignore')

print("   ✅ All libraries imported!")

# --------------------------------------------
# STEP 2: Load the language model
# --------------------------------------------
print("\n🧠 Loading GPT-2 Small model...")
print("   (This will download ~500MB on first run)")
print("   (May take 2-5 minutes...)")

model = HookedTransformer.from_pretrained("gpt2-small")
model.eval()  # Put in evaluation mode

print(f"\n   ✅ Model loaded successfully!")
print(f"   📊 Model architecture:")
print(f"      - Layers: {model.cfg.n_layers}")
print(f"      - Hidden dimension: {model.cfg.d_model}")
print(f"      - Attention heads: {model.cfg.n_heads}")
print(f"      - Vocabulary size: {model.cfg.d_vocab}")

# Save key info for later
n_layers = model.cfg.n_layers
d_model = model.cfg.d_model

print("\n" + "="*60)
print("✅ SETUP COMPLETE! Model is ready.")
print("="*60)





# ============================================
# STEP 3: CREATE DATASET OF CLEAN AND PERTURBED TEXT
# ============================================

print("\n" + "="*60)
print("CREATING DATASET")
print("="*60)

# --------------------------------------------
# 3.1: Define base claims (clean text)
# --------------------------------------------
# These are diverse statements that we'll perturb

base_claims = [
    # Health/Science
    "The vaccine is safe and effective",
    "Climate change is caused by human activity",
    "The medication has been clinically tested",
    "Scientists discovered a new treatment",
    "Research shows the drug reduces symptoms",
    
    # News/Events
    "The election results were officially certified",
    "The company announced record earnings",
    "The government passed new legislation today",
    "Experts recommend following the guidelines",
    "The study was published in a major journal",
    
    # General statements
    "The technology works as described",
    "The report confirms the initial findings",
    "Officials stated the situation is under control",
    "The investigation found no evidence of fraud",
    "The data supports the original hypothesis",
    
    # More variety
    "The economy showed signs of improvement",
    "Researchers identified a new species",
    "The treaty was signed by all parties",
    "The court ruled in favor of the plaintiff",
    "The experiment produced consistent results",
]

print(f"📝 Created {len(base_claims)} base claims")

# --------------------------------------------
# 3.2: Define perturbation functions
# --------------------------------------------
# Each function takes clean text and returns perturbed text

def apply_leetspeak(text):
    """
    PERTURBATION TYPE: Leetspeak
    Replaces letters with similar-looking numbers
    Example: "safe" → "s4f3"
    """
    replacements = [
        ('e', '3'),
        ('a', '4'),
        ('i', '1'),
        ('o', '0'),
        ('s', '5'),
        ('t', '7'),
    ]
    result = text.lower()
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def apply_casing(text):
    """
    PERTURBATION TYPE: Casing
    Converts to ALL UPPERCASE
    Example: "safe" → "SAFE"
    """
    return text.upper()


def apply_slang(text):
    """
    PERTURBATION TYPE: Slang
    Adds internet slang to the end
    Example: "safe" → "safe fr fr"
    """
    slang_additions = [" fr fr", " no cap", " ngl", " tbh", " lowkey"]
    # Use deterministic selection based on text length
    idx = len(text) % len(slang_additions)
    return text + slang_additions[idx]


def apply_typos(text):
    """
    PERTURBATION TYPE: Typos
    Introduces common spelling errors
    Example: "the" → "teh"
    """
    result = text
    typo_map = [
        ("the ", "teh "),
        ("The ", "Teh "),
        (" is ", " iz "),
        (" and ", " adn "),
        (" was ", " waz "),
        ("tion", "shun"),
    ]
    for old, new in typo_map:
        result = result.replace(old, new)
    return result


def apply_spacing(text):
    """
    PERTURBATION TYPE: Spacing/Obfuscation
    Adds dots between letters
    Example: "safe" → "s.a.f.e"
    """
    words = text.split()
    obfuscated_words = []
    for word in words:
        if len(word) > 3:  # Only obfuscate longer words
            obfuscated_words.append('.'.join(word))
        else:
            obfuscated_words.append(word)
    return ' '.join(obfuscated_words)


# Dictionary of all perturbation functions
perturbation_functions = {
    "leetspeak": apply_leetspeak,
    "casing": apply_casing,
    "slang": apply_slang,
    "typos": apply_typos,
    "spacing": apply_spacing,
}

print(f"🔧 Defined {len(perturbation_functions)} perturbation types:")
for name in perturbation_functions:
    print(f"   - {name}")

# --------------------------------------------
# 3.3: Generate the full dataset
# --------------------------------------------

dataset = []

for claim in base_claims:
    # Add the clean version
    dataset.append({
        "text": claim,
        "is_perturbed": 0,
        "perturbation_type": "clean",
        "base_claim_idx": base_claims.index(claim)
    })
    
    # Add each perturbed version
    for pert_name, pert_func in perturbation_functions.items():
        perturbed_text = pert_func(claim)
        dataset.append({
            "text": perturbed_text,
            "is_perturbed": 1,
            "perturbation_type": pert_name,
            "base_claim_idx": base_claims.index(claim)
        })

# Calculate statistics
n_clean = sum(1 for d in dataset if d['is_perturbed'] == 0)
n_perturbed = sum(1 for d in dataset if d['is_perturbed'] == 1)

print(f"\n📊 Dataset created:")
print(f"   Total examples: {len(dataset)}")
print(f"   Clean examples: {n_clean}")
print(f"   Perturbed examples: {n_perturbed}")
print(f"   Perturbation types: {len(perturbation_functions)}")

# Show some examples
print(f"\n📋 Sample examples:")
print("-" * 60)
sample_claim = base_claims[0]
print(f"Original: \"{sample_claim}\"")
print()
for pert_name, pert_func in perturbation_functions.items():
    print(f"{pert_name:12}: \"{pert_func(sample_claim)}\"")
print("-" * 60)






# ============================================
# STEP 4: EXTRACT ACTIVATIONS FROM THE MODEL
# ============================================

print("\n" + "="*60)
print("EXTRACTING ACTIVATIONS (This is the interpretability part!)")
print("="*60)

# --------------------------------------------
# 4.1: Define the activation extraction function
# --------------------------------------------

def get_activations(model, text, layer):
    """
    Extract the 'residual stream' activations at a specific layer.
    
    WHAT IS THE RESIDUAL STREAM?
    ============================
    In a transformer, information flows through "residual stream" -
    think of it as the main highway of information.
    
    At each layer, the model reads from this stream, processes it,
    and writes back to it. By looking at the residual stream at
    different layers, we can see how the model builds up its
    understanding of the text.
    
    Args:
        model: The GPT-2 model
        text: The input text string
        layer: Which layer to extract from (0 to n_layers-1)
    
    Returns:
        A vector of size [d_model] representing the text at that layer
    """
    
    # Convert text to tokens
    tokens = model.to_tokens(text)
    
    # Run the model and cache all intermediate activations
    with torch.no_grad():  # Don't compute gradients (saves memory)
        _, cache = model.run_with_cache(tokens)
    
    # Get the residual stream at the specified layer
    # Shape: [batch_size, sequence_length, d_model]
    # We use "hook_resid_post" which is the output of that layer
    activations = cache[f"blocks.{layer}.hook_resid_post"]
    
    # Average across all token positions to get one vector per text
    # This gives us a single [d_model] vector representing the whole text
    mean_activation = activations[0].mean(dim=0).detach().cpu().numpy()
    
    return mean_activation


# --------------------------------------------
# 4.2: Extract activations for all examples
# --------------------------------------------

print("\n🔍 Extracting activations from all layers...")
print("   This will take a few minutes...")
print()

# Storage for activations
all_activations = {layer: [] for layer in range(n_layers)}

# Storage for labels
labels = []
perturbation_types = []
base_claim_indices = []

# Process each example
total = len(dataset)
for i, item in enumerate(dataset):
    # Progress indicator
    if (i + 1) % 20 == 0 or i == 0:
        print(f"   Processing example {i+1}/{total}...")
    
    # Extract activations at every layer
    for layer in range(n_layers):
        activation = get_activations(model, item["text"], layer)
        all_activations[layer].append(activation)
    
    # Store labels
    labels.append(item["is_perturbed"])
    perturbation_types.append(item["perturbation_type"])
    base_claim_indices.append(item["base_claim_idx"])

# Convert to numpy arrays for easier manipulation
for layer in range(n_layers):
    all_activations[layer] = np.array(all_activations[layer])

labels = np.array(labels)

print(f"\n✅ Extraction complete!")
print(f"   📊 Shape of activations at each layer: {all_activations[0].shape}")
print(f"   📊 This means: {all_activations[0].shape[0]} examples, {all_activations[0].shape[1]} dimensions")









# ============================================
# STEP 5: TRAIN LINEAR PROBES
# ============================================

print("\n" + "="*60)
print("TRAINING LINEAR PROBES")
print("="*60)

print("""
WHAT IS A LINEAR PROBE?
=======================
A linear probe is a simple classifier we train on top of the model's
internal representations (activations).

If a linear probe can predict something (like whether text is perturbed),
that means the information IS PRESENT in the model's representations!

This is how we "peek inside" the model to see what it knows.
""")

# --------------------------------------------
# 5.1: Train BINARY probe (clean vs perturbed)
# --------------------------------------------

print("📊 Training binary probes (clean vs. perturbed)...")
print("   Testing each layer to see where perturbation info is strongest...\n")

binary_probe_accuracies = []
binary_probes = {}  # Store the trained probes

for layer in range(n_layers):
    # Get activations for this layer
    X = all_activations[layer]
    y = labels  # 0 = clean, 1 = perturbed
    
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.3,      # 30% for testing
        random_state=42,    # For reproducibility
        stratify=y          # Keep class balance
    )
    
    # Train a logistic regression probe
    probe = LogisticRegression(
        max_iter=1000,      # Enough iterations to converge
        random_state=42,
        solver='lbfgs'
    )
    probe.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = probe.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Store results
    binary_probe_accuracies.append(accuracy)
    binary_probes[layer] = probe
    
    # Print progress
    print(f"   Layer {layer:2d}: Accuracy = {accuracy:.1%}")

# Find best layer
best_binary_layer = np.argmax(binary_probe_accuracies)
best_binary_accuracy = binary_probe_accuracies[best_binary_layer]

print(f"\n🏆 Best layer for binary classification: Layer {best_binary_layer}")
print(f"   Accuracy: {best_binary_accuracy:.1%}")

# --------------------------------------------
# --------------------------------------------
# 5.2: Train MULTI-CLASS probe (which type of perturbation?)
# --------------------------------------------

print("\n" + "-"*60)
print("📊 Training multi-class probes (which perturbation type?)...")
print("   Only using perturbed examples (excluding clean)...\n")

# Filter to only perturbed examples
perturbed_mask = np.array([pt != "clean" for pt in perturbation_types])
perturbed_labels = [pt for pt in perturbation_types if pt != "clean"]

multiclass_probe_accuracies = []
multiclass_probes = {}

for layer in range(n_layers):
    # Get activations for perturbed examples only
    X = all_activations[layer][perturbed_mask]
    y = perturbed_labels
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        random_state=42
    )
    
    # Train multi-class probe (sklearn auto-detects multinomial)
    probe = LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs'
    )
    probe.fit(X_train, y_train)
    
    # Evaluate
    accuracy = probe.score(X_test, y_test)
    
    # Store results
    multiclass_probe_accuracies.append(accuracy)
    multiclass_probes[layer] = probe
    
    print(f"   Layer {layer:2d}: Accuracy = {accuracy:.1%}")

# Find best layer
best_multiclass_layer = np.argmax(multiclass_probe_accuracies)
best_multiclass_accuracy = multiclass_probe_accuracies[best_multiclass_layer]

print(f"\n🏆 Best layer for multi-class: Layer {best_multiclass_layer}")
print(f"   Accuracy: {best_multiclass_accuracy:.1%}")
print(f"   (Chance would be {100/len(perturbation_functions):.1f}%)")









# ============================================
# STEP 6: SEMANTIC SIMILARITY ANALYSIS
# ============================================

print("\n" + "="*60)
print("ANALYZING SEMANTIC SIMILARITY")
print("="*60)

print("""
THE BIG QUESTION:
=================
At which layer do "The vaccine is safe" and "Th3 v4cc1n3 1s s4f3"
become similar in the model's representation?

If they converge at later layers, it means the model abstracts away
the surface perturbation and recognizes they have the SAME MEANING.
""")

# --------------------------------------------
# 6.1: Compute similarity between clean and perturbed pairs
# --------------------------------------------

def compute_cosine_similarity(vec1, vec2):
    """Compute cosine similarity (1 = identical, 0 = orthogonal)"""
    # Handle potential zero vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)

print("📊 Computing similarity between clean and perturbed versions...")

# Store similarities for each layer
similarities_by_layer = {layer: [] for layer in range(n_layers)}

# For each base claim, compare its clean version to all its perturbed versions
n_base_claims = len(base_claims)

for base_idx in range(n_base_claims):
    # Find the clean example for this base claim
    clean_indices = [i for i, item in enumerate(dataset) 
                     if item["base_claim_idx"] == base_idx 
                     and item["perturbation_type"] == "clean"]
    
    # Find all perturbed examples for this base claim
    perturbed_indices = [i for i, item in enumerate(dataset)
                         if item["base_claim_idx"] == base_idx
                         and item["perturbation_type"] != "clean"]
    
    if clean_indices and perturbed_indices:
        clean_idx = clean_indices[0]
        
        for pert_idx in perturbed_indices:
            # Compare at each layer
            for layer in range(n_layers):
                clean_act = all_activations[layer][clean_idx]
                pert_act = all_activations[layer][pert_idx]
                
                sim = compute_cosine_similarity(clean_act, pert_act)
                similarities_by_layer[layer].append(sim)

# Compute mean similarity at each layer
mean_similarities = []
std_similarities = []

for layer in range(n_layers):
    sims = similarities_by_layer[layer]
    if sims:
        mean_similarities.append(np.mean(sims))
        std_similarities.append(np.std(sims))
    else:
        mean_similarities.append(0.0)
        std_similarities.append(0.0)

print("\n📊 Mean cosine similarity by layer:")
print("-" * 40)
for layer in range(n_layers):
    bar = "█" * int(mean_similarities[layer] * 20)
    print(f"   Layer {layer:2d}: {mean_similarities[layer]:.3f} {bar}")

# Find layer where similarity is highest
convergence_layer = np.argmax(mean_similarities)
print(f"\n🎯 Maximum convergence at Layer {convergence_layer}")
print(f"   Similarity: {mean_similarities[convergence_layer]:.3f}")

# Compare early vs late layers
early_sim = np.mean(mean_similarities[:3])
late_sim = np.mean(mean_similarities[-3:])
print(f"\n📈 Early layers (0-2) average similarity: {early_sim:.3f}")
print(f"📈 Late layers (9-11) average similarity: {late_sim:.3f}")
if early_sim > 0:
    print(f"📈 Change: {late_sim - early_sim:.3f} ({(late_sim/early_sim - 1)*100:.1f}%)")


# ============================================
# STEP 7: GENERATE PUBLICATION-QUALITY GRAPHS
# ============================================

print("\n" + "="*60)
print("GENERATING GRAPHS FOR my APPLICATION")
print("="*60)

# --------------------------------------------
# GRAPH 1: Binary Probe Accuracy by Layer
# --------------------------------------------

print("\n📊 Creating Graph 1: Binary Probe Accuracy...")

fig, ax = plt.subplots(figsize=(10, 6))

# Plot the accuracies
ax.plot(range(n_layers), binary_probe_accuracies, 
        'b-o', linewidth=2, markersize=10, label='Probe Accuracy')

# Add chance line
ax.axhline(y=0.5, color='red', linestyle='--', linewidth=2, 
           label='Chance Level (50%)')

# Mark the best layer
ax.scatter([best_binary_layer], [best_binary_accuracy], 
           s=300, c='green', marker='*', zorder=5, edgecolors='black',
           label=f'Best: Layer {best_binary_layer} ({best_binary_accuracy:.1%})')

# Labels and title
ax.set_xlabel('Layer', fontsize=14)
ax.set_ylabel('Probe Accuracy', fontsize=14)
ax.set_title('Binary Perturbation Detection Probe\n(Can the model tell if text is perturbed?)', 
             fontsize=16, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
ax.set_ylim(0.4, 1.05)
ax.set_xticks(range(n_layers))
ax.tick_params(axis='both', labelsize=12)

# Grid
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('graph1_binary_probe_accuracy.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: graph1_binary_probe_accuracy.png")

# --------------------------------------------
# GRAPH 2: Semantic Similarity by Layer
# --------------------------------------------

print("\n📊 Creating Graph 2: Semantic Similarity...")

fig, ax = plt.subplots(figsize=(10, 6))

# Plot similarity with error bands
ax.plot(range(n_layers), mean_similarities, 
        'g-o', linewidth=2, markersize=10, label='Mean Similarity')

ax.fill_between(range(n_layers),
                np.array(mean_similarities) - np.array(std_similarities),
                np.array(mean_similarities) + np.array(std_similarities),
                alpha=0.3, color='green', label='±1 Std Dev')

# Mark convergence layer
ax.scatter([convergence_layer], [mean_similarities[convergence_layer]], 
           s=300, c='blue', marker='*', zorder=5, edgecolors='black',
           label=f'Max: Layer {convergence_layer} ({mean_similarities[convergence_layer]:.3f})')

# Labels and title
ax.set_xlabel('Layer', fontsize=14)
ax.set_ylabel('Cosine Similarity', fontsize=14)
ax.set_title('Semantic Convergence: Clean vs. Perturbed Text\n(Do representations become similar at deeper layers?)', 
             fontsize=16, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
ax.set_ylim(0, 1.05)
ax.set_xticks(range(n_layers))
ax.tick_params(axis='both', labelsize=12)

ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('graph2_semantic_similarity.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: graph2_semantic_similarity.png")

# --------------------------------------------
# GRAPH 3: Multi-class Probe Accuracy
# --------------------------------------------

print("\n📊 Creating Graph 3: Multi-class Probe Comparison...")

fig, ax = plt.subplots(figsize=(10, 6))

# Plot both probe types
ax.plot(range(n_layers), binary_probe_accuracies, 
        'b-o', linewidth=2, markersize=10, label='Binary (Clean vs. Perturbed)')
ax.plot(range(n_layers), multiclass_probe_accuracies, 
        'r-s', linewidth=2, markersize=10, label='Multi-class (Perturbation Type)')

# Chance lines
ax.axhline(y=0.5, color='blue', linestyle='--', alpha=0.5, linewidth=1.5,
           label='Binary Chance (50%)')
ax.axhline(y=1/len(perturbation_functions), color='red', linestyle='--', 
           alpha=0.5, linewidth=1.5, label=f'Multi-class Chance ({100/len(perturbation_functions):.0f}%)')

# Labels
ax.set_xlabel('Layer', fontsize=14)
ax.set_ylabel('Probe Accuracy', fontsize=14)
ax.set_title('Perturbation Information in Model Representations\n(Binary vs. Multi-class Classification)', 
             fontsize=16, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.set_xticks(range(n_layers))
ax.set_ylim(0, 1.05)
ax.tick_params(axis='both', labelsize=12)

ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('graph3_probe_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: graph3_probe_comparison.png")

# --------------------------------------------
# GRAPH 4: t-SNE Visualization
# --------------------------------------------

print("\n📊 Creating Graph 4: t-SNE Visualization...")
print("   (This may take 30-60 seconds...)")

from sklearn.manifold import TSNE

# Use the best binary layer for visualization
X_vis = all_activations[best_binary_layer]

# Fit t-SNE
tsne = TSNE(
    n_components=2, 
    random_state=42, 
    perplexity=min(30, len(X_vis) - 1),
    max_iter=1000
)
X_2d = tsne.fit_transform(X_vis)

# Create plot
fig, ax = plt.subplots(figsize=(12, 9))

# Color map for perturbation types
colors = {
    'clean': '#27ae60',      # Green
    'leetspeak': '#e74c3c',  # Red
    'casing': '#3498db',     # Blue
    'slang': '#f39c12',      # Orange
    'typos': '#9b59b6',      # Purple
    'spacing': '#1abc9c',    # Teal
}

# Plot each perturbation type
for pert_type in ['clean', 'leetspeak', 'casing', 'slang', 'typos', 'spacing']:
    mask = [pt == pert_type for pt in perturbation_types]
    if any(mask):
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                   c=colors.get(pert_type, 'gray'),
                   label=pert_type.upper() if pert_type == 'clean' else pert_type,
                   alpha=0.7,
                   s=150,
                   edgecolors='white',
                   linewidth=1)

ax.set_xlabel('t-SNE Dimension 1', fontsize=14)
ax.set_ylabel('t-SNE Dimension 2', fontsize=14)
ax.set_title(f't-SNE Visualization of Layer {best_binary_layer} Representations\n(How does the model organize different perturbation types?)', 
             fontsize=16, fontweight='bold')
ax.legend(loc='best', fontsize=11, title='Perturbation Type', title_fontsize=12)
ax.tick_params(axis='both', labelsize=12)

plt.tight_layout()
plt.savefig('graph4_tsne_visualization.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: graph4_tsne_visualization.png")

print("\n" + "="*60)
print("✅ ALL GRAPHS GENERATED!")
print("="*60)


# ============================================
# STEP 8: GENERATE SUMMARY STATISTICS FOR WRITE-UP
# ============================================

print("\n" + "="*60)
print("SUMMARY STATISTICS FOR MY MATS APPLICATION")
print("="*60)

print("""
╔══════════════════════════════════════════════════════════════╗
║     Copy these numbers directly into my executive summary! ║
╚══════════════════════════════════════════════════════════════╝
""")

print("-" * 60)
print("📊 DATASET")
print("-" * 60)
print(f"   Total examples: {len(dataset)}")
print(f"   Clean examples: {n_clean}")
print(f"   Perturbed examples: {n_perturbed}")
print(f"   Base claims: {len(base_claims)}")
print(f"   Perturbation types: {len(perturbation_functions)}")
for ptype in perturbation_functions.keys():
    print(f"      • {ptype}")

print("\n" + "-" * 60)
print("🧠 MODEL")
print("-" * 60)
print(f"   Model: GPT-2 Small (124M parameters)")
print(f"   Layers: {n_layers}")
print(f"   Hidden dimension: {d_model}")

print("\n" + "-" * 60)
print("🔬 KEY FINDING 1: Binary Perturbation Detection")
print("-" * 60)
print(f"   Best layer: Layer {best_binary_layer}")
print(f"   Best accuracy: {best_binary_accuracy:.1%}")
print(f"   Chance level: 50%")
print(f"   Above chance: +{(best_binary_accuracy - 0.5)*100:.1f} percentage points")

print("\n" + "-" * 60)
print("🔬 KEY FINDING 2: Multi-class Perturbation Type")
print("-" * 60)
print(f"   Best layer: Layer {best_multiclass_layer}")
print(f"   Best accuracy: {best_multiclass_accuracy:.1%}")
print(f"   Chance level: {100/len(perturbation_functions):.1f}%")
print(f"   Above chance: +{(best_multiclass_accuracy - 1/len(perturbation_functions))*100:.1f} percentage points")

print("\n" + "-" * 60)
print("🔬 KEY FINDING 3: Semantic Convergence")
print("-" * 60)
print(f"   Early layer (0) similarity: {mean_similarities[0]:.3f}")
print(f"   Middle layer ({n_layers//2}) similarity: {mean_similarities[n_layers//2]:.3f}")
print(f"   Late layer ({n_layers-1}) similarity: {mean_similarities[-1]:.3f}")
print(f"   Maximum similarity at: Layer {convergence_layer} ({mean_similarities[convergence_layer]:.3f})")

print("\n" + "-" * 60)
print("📝 INTERPRETATION FOR my WRITE-UP")
print("-" * 60)
print(f"""
1. PERTURBATION IS IMMEDIATELY DETECTABLE
   The model can detect perturbed text from Layer 0 with {best_binary_accuracy:.1%}
   accuracy (vs. 50% chance). This suggests perturbation information
   is encoded in the token embeddings themselves.

2. PERTURBATION TYPES ARE DISTINGUISHABLE  
   The model distinguishes WHICH perturbation was used with {best_multiclass_accuracy:.1%}
   accuracy at Layer {best_multiclass_layer} (vs. {100/len(perturbation_functions):.0f}% chance).
   Different perturbations create different internal patterns.

3. SEMANTIC SIMILARITY PATTERN
   Clean and perturbed versions of the same claim have {mean_similarities[0]:.1%}
   similarity at Layer 0, {"increasing" if mean_similarities[-1] > mean_similarities[0] else "staying relatively stable"} 
   to {mean_similarities[-1]:.1%} at Layer {n_layers-1}.
""")

print("\n" + "="*60)
print("🎉 EXPERIMENT COMPLETE!")
print("="*60)
print("""
📁 Files generated in my folder:
   • graph1_binary_probe_accuracy.png
   • graph2_semantic_similarity.png
   • graph3_probe_comparison.png
   • graph4_tsne_visualization.png
   • experiment_summary.txt
""")

# Save summary to file
with open('experiment_summary.txt', 'w', encoding='utf-8') as f:
    f.write("PERTURBATION INTERPRETABILITY EXPERIMENT - SUMMARY\n")
    f.write("="*60 + "\n\n")
    f.write(f"Dataset: {len(dataset)} examples ({n_clean} clean, {n_perturbed} perturbed)\n")
    f.write(f"Model: GPT-2 Small ({n_layers} layers, {d_model} hidden dim)\n\n")
    f.write("KEY FINDINGS:\n")
    f.write(f"1. Binary probe: Layer {best_binary_layer} achieves {best_binary_accuracy:.1%} accuracy (chance=50%)\n")
    f.write(f"2. Multi-class probe: Layer {best_multiclass_layer} achieves {best_multiclass_accuracy:.1%} accuracy (chance={100/len(perturbation_functions):.0f}%)\n")
    f.write(f"3. Semantic similarity: {mean_similarities[0]:.3f} (layer 0) → {mean_similarities[-1]:.3f} (layer {n_layers-1})\n")
    f.write(f"4. Maximum similarity at Layer {convergence_layer}: {mean_similarities[convergence_layer]:.3f}\n")

print("📄 Summary saved to: experiment_summary.txt")
print("\n" + "="*60)