"""
CogniGuard Claim Analyzer Page
"""

import streamlit as st
import sys
from pathlib import Path

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Claim Analyzer",
    page_icon="🔬",
    layout="wide"
)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import - handle errors gracefully
try:
    from core.claim_analyzer import ClaimAnalyzer, PerturbationType, NoiseBudget
    IMPORT_SUCCESS = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)

# Title
st.title("🔬 Claim Analyzer")
st.markdown("**Based on ACL 2025 Paper:** Detecting 6 perturbation types")

# Check import status
if not IMPORT_SUCCESS:
    st.error(f"""
    ### ⚠️ Import Error
    
    Could not load the Claim Analyzer module.
    
    **Error:** `{IMPORT_ERROR}`
    
    **To fix this:**
    1. Make sure `core/claim_analyzer.py` exists
    2. Check for syntax errors in that file
    3. Try running: `python core/claim_analyzer.py`
    """)
    
    st.info("Showing demo mode instead...")
    
    # Demo mode without imports
    st.subheader("📝 The 6 Perturbation Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. 🔤 CASING**
        - Low: TrueCasing
        - High: ALL CAPS
        
        **2. ✏️ TYPOS**
        - Low: Minor typos
        - High: Leetspeak (v4cc1ne)
        
        **3. 🚫 NEGATION**
        - Low: "is not"
        - High: "not untrue"
        """)
    
    with col2:
        st.markdown("""
        **4. 👤 ENTITY REPLACEMENT**
        - Low: 1 entity changed
        - High: All vague references
        
        **5. 🤖 LLM REWRITE**
        - Low: Slight paraphrase
        - High: Complete rewrite
        
        **6. 🌍 DIALECT**
        - AAE, Nigerian Pidgin
        - Singlish, Jamaican Patois
        """)
    
    st.stop()

# If imports worked, show the full analyzer
st.success("✅ Claim Analyzer loaded successfully!")

# Initialize analyzer
@st.cache_resource
def get_analyzer():
    return ClaimAnalyzer()

try:
    analyzer = get_analyzer()
except Exception as e:
    st.error(f"Error initializing analyzer: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📊 About")
    st.markdown("""
    This tool detects **6 perturbation types**
    that bad actors use to evade fact-checking:
    
    1. Casing changes
    2. Typos/Leetspeak
    3. Negation tricks
    4. Entity swaps
    5. LLM rewrites
    6. Dialect variations
    """)

# Main interface
tab1, tab2 = st.tabs(["📝 Analyze Text", "🎯 Examples"])

with tab1:
    st.subheader("Enter text to analyze")
    
    user_input = st.text_area(
        "Paste a claim here:",
        placeholder="Example: Th3 vaxx is not unsafe fr fr no cap",
        height=100
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    with col2:
        if st.button("📋 Example 1", use_container_width=True):
            user_input = "THE VACCINE IS COMPLETELY SAFE!!!"
    with col3:
        if st.button("📋 Example 2", use_container_width=True):
            user_input = "Th3 vaxx is s4fe fr fr no cap"
    
    if analyze_btn and user_input.strip():
        with st.spinner("Analyzing..."):
            try:
                result = analyzer.analyze(user_input)
                
                # Show results
                st.divider()
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Status", "⚠️ PERTURBED" if result.is_perturbed else "✅ CLEAN")
                with c2:
                    st.metric("Perturbations", len(result.perturbations_detected))
                with c3:
                    st.metric("Robustness", f"{result.robustness_score:.0%}")
                
                # Details
                if result.is_perturbed:
                    st.subheader("⚠️ Detected Perturbations")
                    for p in result.perturbations_detected:
                        with st.expander(f"{p.perturbation_type.value.upper()} ({p.noise_budget.value} noise)"):
                            st.write(f"**Explanation:** {p.explanation}")
                            st.write(f"**Confidence:** {p.confidence:.0%}")
                            st.write("**Evidence:**")
                            for e in p.evidence:
                                st.code(e)
                else:
                    st.success("No perturbations detected!")
                
                # Recommendations
                st.subheader("💡 Recommendations")
                for rec in result.recommendations:
                    st.write(f"• {rec}")
                    
            except Exception as e:
                st.error(f"Analysis error: {e}")

with tab2:
    st.subheader("🎯 Example Perturbations")
    
    try:
        demos = analyzer.demo_perturbations()
        
        st.markdown("### Original")
        st.code(demos["original"][0])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔤 Casing")
            st.code(demos["casing_high"][0])
            
            st.markdown("### 🚫 Negation")
            st.code(demos["negation_high"][0])
            
            st.markdown("### 🤖 LLM Rewrite")
            st.code(demos["llm_rewrite_high"][0][:60] + "...")
        
        with col2:
            st.markdown("### ✏️ Typos")
            st.code(demos["typos_high"][0])
            
            st.markdown("### 👤 Entity")
            st.code(demos["entity_high"][0])
            
            st.markdown("### 🌍 Dialect (AAE)")
            st.code(demos["dialect_aae"][0])
            
    except Exception as e:
        st.error(f"Error loading examples: {e}")

# Footer
st.divider()
st.caption("🔬 Claim Analyzer | CogniGuard | Based on ACL 2025 Research")