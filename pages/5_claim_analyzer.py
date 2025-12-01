"""
=============================================================================
COGNIGUARD - CLAIM ANALYZER PAGE
=============================================================================
This page demonstrates the 6 perturbation types from the ACL 2025 paper:
"When Claims Evolve: Evaluating and Enhancing the Robustness of 
Embedding Models Against Misinformation Edits"

The 6 Perturbation Types:
1. CASING - TrueCasing vs. UPPERCASE
2. TYPOS - Minor typos vs. leetspeak/slang  
3. NEGATION - Single vs. double negation
4. ENTITY REPLACEMENT - Partial vs. full entity swapping
5. LLM REWRITE - Minimal vs. maximal paraphrasing
6. DIALECT - AAE, Nigerian Pidgin, Singlish, Jamaican Patois
=============================================================================
"""

import streamlit as st
import sys
from pathlib import Path

# =============================================================================
# SETUP: Add project root to Python path
# =============================================================================
# This tells Python where to find our core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now we can import our modules
try:
    from core.claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget
    CLAIM_ANALYZER_AVAILABLE = True
except ImportError as e:
    CLAIM_ANALYZER_AVAILABLE = False
    import_error = str(e)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Claim Analyzer - CogniGuard",
    page_icon="🔬",
    layout="wide"
)

# =============================================================================
# CUSTOM CSS FOR BEAUTIFUL STYLING
# =============================================================================
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling for each perturbation type */
    .perturbation-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid;
    }
    
    .casing-card { border-left-color: #FF6B6B; }
    .typos-card { border-left-color: #4ECDC4; }
    .negation-card { border-left-color: #45B7D1; }
    .entity-card { border-left-color: #96CEB4; }
    .llm-card { border-left-color: #FFEAA7; }
    .dialect-card { border-left-color: #DDA0DD; }
    
    /* Result box styling */
    .result-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .result-clean {
        border-left: 5px solid #28a745;
        background: #d4edda;
    }
    
    .result-perturbed {
        border-left: 5px solid #ffc107;
        background: #fff3cd;
    }
    
    .result-high-noise {
        border-left: 5px solid #dc3545;
        background: #f8d7da;
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Evidence list */
    .evidence-item {
        background: #e9ecef;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.3rem 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER SECTION
# =============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔬 Claim Analyzer</h1>
    <p>Based on "When Claims Evolve" - ACL 2025 Paper</p>
    <p>Detecting the 6 Perturbation Types Used to Evade Fact-Checking</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CHECK IF CLAIM ANALYZER IS AVAILABLE
# =============================================================================
if not CLAIM_ANALYZER_AVAILABLE:
    st.error(f"""
    ⚠️ **Claim Analyzer Module Not Found**
    
    The claim_analyzer.py file is missing from your core folder.
    
    **How to fix:**
    1. Make sure you have `core/claim_analyzer.py` in your project
    2. Check the import error: `{import_error}`
    
    Please go back and create the claim_analyzer.py file first.
    """)
    st.stop()

# =============================================================================
# INITIALIZE THE CLAIM ANALYZER
# =============================================================================
@st.cache_resource
def get_analyzer():
    """
    Create and cache the ClaimAnalyzer instance
    cache_resource means it only loads once, saving memory
    """
    return ClaimAnalyzer()

analyzer = get_analyzer()

# =============================================================================
# SIDEBAR - NAVIGATION AND SETTINGS
# =============================================================================
with st.sidebar:
    st.header("🎛️ Analysis Options")
    
    # Mode selection
    mode = st.radio(
        "Choose Mode",
        ["📝 Analyze Custom Claim", "🎯 See Examples", "📚 Learn About Types"],
        index=0
    )
    
    st.divider()
    
    # Information box
    st.info("""
    **What is a Perturbation?**
    
    A perturbation is a small change made to text 
    that tries to trick AI systems while keeping 
    the meaning similar to humans.
    
    Bad actors use these tricks to spread 
    misinformation that evades detection.
    """)
    
    # Legend
    st.subheader("📊 Noise Budget Legend")
    st.markdown("""
    - 🟢 **Low Noise**: Minor changes
    - 🔴 **High Noise**: Major changes
    """)

# =============================================================================
# MODE 1: ANALYZE CUSTOM CLAIM
# =============================================================================
if mode == "📝 Analyze Custom Claim":
    st.header("📝 Analyze Your Own Claim")
    
    st.markdown("""
    Enter any text below to check if it contains perturbations that might 
    indicate an attempt to evade misinformation detection.
    """)
    
    # Text input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_claim = st.text_area(
            "Enter a claim to analyze:",
            placeholder="Example: Th3 vaxx is not unsafe according 2 the govt...",
            height=120,
            help="Paste any text you want to check for perturbations"
        )
    
    with col2:
        st.markdown("### Quick Examples")
        
        # Quick paste buttons
        if st.button("📌 Normal Text"):
            st.session_state.example_text = "The COVID-19 vaccine is safe and effective according to the CDC."
        
        if st.button("📌 All Caps"):
            st.session_state.example_text = "THE VACCINE IS SAFE AND EFFECTIVE!"
        
        if st.button("📌 Leetspeak"):
            st.session_state.example_text = "Th3 vaxx is s4fe according 2 the CDC lol"
        
        if st.button("📌 Double Negation"):
            st.session_state.example_text = "It is not untrue that vaccines are not ineffective."
    
    # Handle example text
    if 'example_text' in st.session_state:
        user_claim = st.session_state.example_text
        del st.session_state.example_text
        st.rerun()
    
    # Analyze button
    if st.button("🔍 Analyze Claim", type="primary", use_container_width=True):
        if user_claim.strip():
            with st.spinner("Analyzing claim for perturbations..."):
                # Run analysis
                result = analyzer.analyze(user_claim)
            
            # Display results
            st.divider()
            st.subheader("📊 Analysis Results")
            
            # Top metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status = "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN"
                st.metric("Status", status)
            
            with col2:
                st.metric("Perturbations Found", len(result.perturbations_detected))
            
            with col3:
                st.metric("Confidence", f"{result.overall_confidence:.0%}")
            
            with col4:
                # Color the robustness score
                robustness_pct = result.robustness_score * 100
                st.metric("Robustness", f"{robustness_pct:.0f}%")
            
            st.divider()
            
            # Detailed results
            if result.is_perturbed:
                st.subheader("⚠️ Perturbations Detected")
                
                for p in result.perturbations_detected:
                    # Choose color based on noise budget
                    if p.noise_budget == NoiseBudget.HIGH:
                        box_class = "result-high-noise"
                        noise_icon = "🔴"
                    else:
                        box_class = "result-perturbed"
                        noise_icon = "🟢"
                    
                    # Display perturbation card
                    with st.expander(
                        f"{noise_icon} {p.perturbation_type.value.upper()} "
                        f"({p.noise_budget.value} noise) - {p.confidence:.0%} confidence",
                        expanded=True
                    ):
                        st.markdown(f"**Explanation:** {p.explanation}")
                        
                        st.markdown("**Evidence:**")
                        for e in p.evidence:
                            st.code(e)
                        
                        if p.normalized_claim != user_claim:
                            st.markdown("**Suggested Normalization:**")
                            st.success(p.normalized_claim)
            else:
                st.success("""
                ✅ **No Perturbations Detected**
                
                This claim appears to be in its canonical form without 
                any detected manipulation attempts.
                """)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(result.recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Show normalized form
            st.subheader("📝 Normalized Claim")
            st.info(result.normalized_claim)
        
        else:
            st.warning("Please enter a claim to analyze.")

# =============================================================================
# MODE 2: SEE EXAMPLES
# =============================================================================
elif mode == "🎯 See Examples":
    st.header("🎯 Perturbation Examples")
    
    st.markdown("""
    See real examples of each perturbation type. Click on any example 
    to see how the analyzer detects it.
    """)
    
    # Get demo perturbations
    demos = analyzer.demo_perturbations()
    
    # Create tabs for each perturbation type
    tabs = st.tabs([
        "1️⃣ Casing",
        "2️⃣ Typos", 
        "3️⃣ Negation",
        "4️⃣ Entity",
        "5️⃣ LLM Rewrite",
        "6️⃣ Dialect"
    ])
    
    # Tab 1: Casing
    with tabs[0]:
        st.subheader("🔤 Casing Perturbations")
        
        st.markdown("""
        **What is it?** Changing the capitalization of text.
        
        **Why do bad actors use it?** Some AI systems are case-sensitive, 
        so changing case can evade detection.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Low Noise (TrueCasing)**")
            low_example = demos["casing_low"][0]
            st.code(low_example)
            if st.button("Analyze", key="casing_low"):
                result = analyzer.analyze(low_example)
                st.json({
                    "perturbed": result.is_perturbed,
                    "confidence": f"{result.overall_confidence:.0%}",
                    "robustness": f"{result.robustness_score:.0%}"
                })
        
        with col2:
            st.markdown("**🔴 High Noise (ALL CAPS)**")
            high_example = demos["casing_high"][0]
            st.code(high_example)
            if st.button("Analyze", key="casing_high"):
                result = analyzer.analyze(high_example)
                st.json({
                    "perturbed": result.is_perturbed,
                    "types": [p.perturbation_type.value for p in result.perturbations_detected],
                    "confidence": f"{result.overall_confidence:.0%}"
                })
    
    # Tab 2: Typos
    with tabs[1]:
        st.subheader("✏️ Typo Perturbations")
        
        st.markdown("""
        **What is it?** Introducing spelling errors, leetspeak (replacing 
        letters with numbers), or slang.
        
        **Why do bad actors use it?** Text matching systems look for 
        exact keywords, so "v4ccine" won't match "vaccine".
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Low Noise (Minor Typo)**")
            low_example = demos["typos_low"][0]
            st.code(low_example)
            if st.button("Analyze", key="typos_low"):
                result = analyzer.analyze(low_example)
                st.write(f"Detected: {result.is_perturbed}")
        
        with col2:
            st.markdown("**🔴 High Noise (Leetspeak/Slang)**")
            high_example = demos["typos_high"][0]
            st.code(high_example)
            if st.button("Analyze", key="typos_high"):
                result = analyzer.analyze(high_example)
                for p in result.perturbations_detected:
                    st.warning(f"{p.perturbation_type.value}: {p.evidence}")
    
    # Tab 3: Negation
    with tabs[2]:
        st.subheader("🚫 Negation Perturbations")
        
        st.markdown("""
        **What is it?** Adding or manipulating negative words to confuse 
        the meaning.
        
        **Why do bad actors use it?** Double negatives ("not unsafe") are 
        logically equivalent to positives ("safe") but confuse AI systems.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Low Noise (Single Negation)**")
            low_example = demos["negation_low"][0]
            st.code(low_example)
            st.caption("'is not unsafe' = single negation")
        
        with col2:
            st.markdown("**🔴 High Noise (Double Negation)**")
            high_example = demos["negation_high"][0]
            st.code(high_example)
            st.caption("Multiple negations = very confusing!")
            if st.button("Analyze", key="neg_high"):
                result = analyzer.analyze(high_example)
                st.error(f"Confidence: {result.overall_confidence:.0%}")
    
    # Tab 4: Entity Replacement
    with tabs[3]:
        st.subheader("👤 Entity Replacement Perturbations")
        
        st.markdown("""
        **What is it?** Replacing specific names (people, organizations, 
        places) with vague terms or synonyms.
        
        **Why do bad actors use it?** Fact-checkers often search for 
        specific entity names. "CDC" → "the health agency" evades this.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Low Noise (1 Entity)**")
            st.code(demos["entity_low"][0])
        
        with col2:
            st.markdown("**🔴 High Noise (All Entities)**")
            st.code(demos["entity_high"][0])
    
    # Tab 5: LLM Rewrite
    with tabs[4]:
        st.subheader("🤖 LLM Rewrite Perturbations")
        
        st.markdown("""
        **What is it?** Using AI (like ChatGPT) to paraphrase claims 
        while keeping the meaning.
        
        **Why do bad actors use it?** Each rewrite is unique, making 
        it impossible to match against a database of known false claims.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Low Noise (Slight Reword)**")
            st.code(demos["llm_rewrite_low"][0])
        
        with col2:
            st.markdown("**🔴 High Noise (Full Rewrite)**")
            st.code(demos["llm_rewrite_high"][0][:100] + "...")
    
    # Tab 6: Dialect
    with tabs[5]:
        st.subheader("🌍 Dialect Perturbations")
        
        st.markdown("""
        **What is it?** Rewriting claims in regional dialects or 
        vernacular English.
        
        **Why do bad actors use it?** Most fact-checking systems are 
        trained only on Standard American English.
        """)
        
        st.markdown("**Supported Dialects:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**African American English (AAE)**")
            st.code(demos["dialect_aae"][0])
        
        with col2:
            st.markdown("**Nigerian Pidgin**")
            st.code(demos["dialect_nigerian_pidgin"][0])

# =============================================================================
# MODE 3: LEARN ABOUT TYPES
# =============================================================================
elif mode == "📚 Learn About Types":
    st.header("📚 Understanding the 6 Perturbation Types")
    
    st.markdown("""
    This educational section explains each perturbation type in detail, 
    based on the ACL 2025 research paper.
    """)
    
    # Interactive learning cards
    st.subheader("1️⃣ CASING Perturbations")
    with st.expander("Click to learn about Casing", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### What is Casing?
            
            Casing refers to whether letters are uppercase (ABC) or 
            lowercase (abc).
            
            ### The Two Noise Budgets:
            
            | Budget | Description | Example |
            |--------|-------------|---------|
            | Low | Normal capitalization (TrueCasing) | "The Vaccine Works" |
            | High | ALL CAPS or all lowercase | "THE VACCINE WORKS" |
            
            ### Why It Matters:
            
            Some text matching systems are case-sensitive. By changing 
            "COVID" to "covid" or "COVID", the same claim might evade 
            detection systems that look for specific capitalization.
            """)
        
        with col2:
            st.image("https://via.placeholder.com/200x150?text=Aa+→+AA", 
                     caption="Casing transformation")
    
    st.subheader("2️⃣ TYPO Perturbations")
    with st.expander("Click to learn about Typos"):
        st.markdown("""
        ### What are Typos?
        
        Intentional or unintentional misspellings that change how 
        text is written but not what it means.
        
        ### Types of Typos:
        
        1. **Character substitution**: "vaccine" → "vacine"
        2. **Leetspeak**: "vaccine" → "v4cc1ne" (numbers for letters)
        3. **Slang/Abbreviations**: "you are" → "ur"
        4. **Evasion spellings**: "COVID" → "c0vid" (to avoid filters)
        
        ### Example Leetspeak Table:
        
        | Letter | Leetspeak |
        |--------|-----------|
        | A | 4 or @ |
        | E | 3 |
        | I | 1 |
        | O | 0 |
        | S | 5 or $ |
        """)
    
    st.subheader("3️⃣ NEGATION Perturbations")
    with st.expander("Click to learn about Negation"):
        st.markdown("""
        ### What is Negation?
        
        Adding "not", "never", or other negative words to flip the 
        meaning of a statement.
        
        ### Single vs Double Negation:
        
        | Type | Example | Real Meaning |
        |------|---------|--------------|
        | None | "The vaccine is safe" | Safe |
        | Single | "The vaccine is not unsafe" | Safe (but confusing) |
        | Double | "It is not untrue that it's not ineffective" | Probably safe? |
        
        ### Why It's Tricky:
        
        Double negatives are grammatically valid but extremely confusing. 
        AI systems often misclassify them because they get confused by 
        the multiple negative words.
        """)
    
    st.subheader("4️⃣ ENTITY REPLACEMENT Perturbations")
    with st.expander("Click to learn about Entity Replacement"):
        st.markdown("""
        ### What is Entity Replacement?
        
        Swapping specific names (entities) with vague references or 
        synonyms.
        
        ### Examples:
        
        | Original Entity | Replaced With |
        |-----------------|---------------|
        | CDC | "the health agency" |
        | Dr. Fauci | "the official" |
        | United States | "that country" |
        | Pfizer | "the company" |
        
        ### Why It's Used:
        
        Fact-checkers often search for specific names. If a false 
        claim about "WHO" is known, changing it to "the global health 
        organization" might evade detection.
        """)
    
    st.subheader("5️⃣ LLM REWRITE Perturbations")
    with st.expander("Click to learn about LLM Rewrites"):
        st.markdown("""
        ### What is an LLM Rewrite?
        
        Using AI language models (like ChatGPT) to paraphrase text 
        while keeping the same meaning.
        
        ### Low vs High Noise:
        
        **Low Noise (Minimal rewrite):**
        - Original: "The vaccine is effective."
        - Rewrite: "The vaccine works effectively."
        
        **High Noise (Full rewrite):**
        - Original: "The vaccine is effective."
        - Rewrite: "According to available data, the immunization 
          treatment has demonstrated significant efficacy in preventing 
          the targeted disease."
        
        ### Detection Clues:
        
        LLM rewrites often have:
        - Overly formal language ("it is worth noting that")
        - Perfect grammar
        - Consistent sentence structure
        """)
    
    st.subheader("6️⃣ DIALECT Perturbations")
    with st.expander("Click to learn about Dialect"):
        st.markdown("""
        ### What is Dialect?
        
        Rewriting text in regional varieties of English that differ 
        from Standard American English.
        
        ### The Four Dialects Studied:
        
        | Dialect | Region | Example Phrase |
        |---------|--------|----------------|
        | AAE | African American English | "finna", "fr fr", "no cap" |
        | Nigerian Pidgin | Nigeria | "wetin dey happen", "na true" |
        | Singlish | Singapore | "can lah", "very sian" |
        | Jamaican Patois | Jamaica | "wah gwaan", "mi nuh know" |
        
        ### Why It Matters:
        
        Most NLP systems are trained primarily on Standard American 
        English. Claims written in other dialects often receive lower 
        accuracy in detection, creating a fairness issue.
        """)
    
    # Summary table
    st.subheader("📊 Summary Table")
    
    st.dataframe({
        "Type": ["Casing", "Typos", "Negation", "Entity", "LLM Rewrite", "Dialect"],
        "Low Noise": ["TrueCasing", "1-2 char typos", "Single 'not'", "1 entity", "Slight reword", "N/A"],
        "High Noise": ["ALL CAPS", "Leetspeak", "Double negative", "All entities", "Full rewrite", "Any dialect"],
        "Detection Difficulty": ["Easy", "Medium", "Hard", "Hard", "Very Hard", "Very Hard"],
    })

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🔬 Claim Analyzer | Based on ACL 2025 Research</p>
    <p>"When Claims Evolve: Evaluating and Enhancing the Robustness of 
    Embedding Models Against Misinformation Edits"</p>
    <p>Part of the CogniGuard AI Safety Platform</p>
</div>
""", unsafe_allow_html=True)