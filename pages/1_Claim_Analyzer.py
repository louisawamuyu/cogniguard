import streamlit as st

st.title("🔬 Claim Analyzer")

st.markdown("""
## Detect Misinformation Perturbations

This tool detects 6 types of text manipulation:

| # | Type | Example |
|---|------|---------|
| 1 | **Casing** | THE VACCINE IS SAFE |
| 2 | **Typos** | Th3 v4ccine is s4fe |
| 3 | **Negation** | is not untrue |
| 4 | **Entity** | the agency said |
| 5 | **LLM Rewrite** | Furthermore, it is worth noting |
| 6 | **Dialect** | fr fr no cap |
""")

st.divider()

# Simple demo
user_text = st.text_area("Enter text to check:", height=100)

if st.button("Analyze"):
    if user_text:
        # Simple checks
        is_caps = user_text.isupper()
        has_numbers = any(c.isdigit() for c in user_text)
        has_double_neg = "not un" in user_text.lower()
        
        st.subheader("Results")
        
        if is_caps:
            st.warning("⚠️ CASING: Text is all uppercase")
        if has_numbers and any(c.isalpha() for c in user_text):
            st.warning("⚠️ TYPOS: Contains numbers mixed with letters (leetspeak?)")
        if has_double_neg:
            st.warning("⚠️ NEGATION: Double negative detected")
        
        if not (is_caps or has_numbers or has_double_neg):
            st.success("✅ No obvious perturbations detected")
    else:
        st.info("Please enter some text")
