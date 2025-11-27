"""
=============================================================================
DEMO 7: CYBER INSURANCE REQUIREMENTS
=============================================================================
This demo shows how cyber insurance is changing for AI.
"""

import streamlit as st

def show_insurance_demo():
    """
    This function displays the Cyber Insurance demo.
    """
    
    # Page Title
    st.title("🛡️ Cyber Insurance: Coverage Requires Controls")
    st.markdown("### Insurance Companies Are Getting Strict About AI")
    
    # Warning Box
    st.warning("""
    📋 **INSURANCE REALITY**: Cyber insurers now require specific security controls.
    Without them, you pay higher premiums - or get denied coverage entirely.
    """)
    
    # How Insurance Has Changed
    st.markdown("---")
    st.header("📈 How Cyber Insurance Has Changed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🕐 Before (2019):
        
        **Application Question:**
        "Do you have antivirus software?"
        
        **Answer:** "Yes"
        
        **Result:** ✅ Approved! Here's your policy.
        
        ---
        
        *It was easy to get coverage with minimal security.*
        """)
    
    with col2:
        st.markdown("""
        ### 🕐 Now (2024):
        
        **Application Questions:**
        - "Show MFA implementation evidence"
        - "Provide penetration test results"
        - "Document incident response plan"
        - "Prove endpoint detection is active"
        - "Demonstrate backup procedures"
        
        **Result:** 📋 Extensive review, higher premiums
        
        *Insurance now requires PROOF of security.*
        """)
    
    # Coming Soon
    st.markdown("---")
    st.header("🔮 What's Coming: AI-Specific Requirements")
    
    st.error("""
    ### Insurance Companies Will Ask:
    
    ❓ "What AI security controls do you have?"
    
    ❓ "How do you prevent AI data leakage?"
    
    ❓ "What's your AI incident response plan?"
    
    ❓ "Show audit trails for AI interactions."
    
    ❓ "How do you detect prompt injection attacks?"
    
    ❓ "What controls prevent AI from making unauthorized decisions?"
    
    **Companies without answers will face higher premiums or denied coverage.**
    """)
    
    # Impact Table
    st.markdown("---")
    st.header("💰 Financial Impact")
    
    st.markdown("""
    | Scenario | Without AI Security | With CogniGuard |
    |----------|--------------------:|----------------:|
    | Annual premium | +25-50% higher | Standard rate |
    | Deductible | Higher | Standard |
    | Coverage limits | Lower | Full coverage |
    | Claim approval | May be denied | Smooth process |
    """)
    
    # The Claim Denial Scenario
    st.markdown("---")
    st.header("🚫 The Nightmare Scenario: Claim Denied")
    
    st.markdown("""
    ### What Happens When AI Security Is Inadequate:
    """)
    
    # Timeline
    st.error("""
    **1. AI-Related Incident Occurs:**
    - Your AI assistant leaks customer data
    - Attacker exploited prompt injection vulnerability
    - Thousands of customer records exposed
    
    **2. You File Insurance Claim:**
    - Notify your cyber insurance carrier
    - Claim: $500,000 in breach costs
    
    **3. Insurance Investigates:**
    - "What AI security controls did you have?"
    - "Show us your AI monitoring logs"
    - "Where's your prompt injection protection?"
    
    **4. Claim DENIED:**
    - "Policyholder failed to implement reasonable AI security controls"
    - "This incident was preventable with standard precautions"
    - "Policy exclusion: Failure to maintain adequate security"
    
    **5. You Pay Everything:**
    - Breach notification costs: $50,000
    - Legal fees: $100,000
    - Regulatory fines: $200,000
    - Lawsuit settlements: $500,000+
    - **All out of pocket.**
    """)
    
    # Interactive Premium Calculator
    st.markdown("---")
    st.header("🧮 Interactive: Insurance Premium Estimator")
    
    st.info("See how AI security affects your cyber insurance costs.")
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        revenue = st.selectbox(
            "Annual Revenue:",
            ["Under $1M", "$1M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"]
        )
        
        industry = st.selectbox(
            "Industry:",
            ["Healthcare", "Financial Services", "Technology", "Retail", "Manufacturing", "Other"]
        )
    
    with col2:
        ai_usage = st.selectbox(
            "AI Usage Level:",
            ["Heavy - Core to business", "Moderate - Regular use", "Light - Occasional use", "None"]
        )
        
        current_security = st.selectbox(
            "Current AI Security:",
            ["Comprehensive (CogniGuard or equivalent)", "Basic monitoring", "None"]
        )
    
    if st.button("📊 Estimate Premium Impact", type="primary"):
        
        # Base premium by revenue
        base_premiums = {
            "Under $1M": 2500,
            "$1M - $10M": 7500,
            "$10M - $50M": 25000,
            "$50M - $100M": 75000,
            "Over $100M": 150000
        }
        base = base_premiums[revenue]
        
        # Industry multiplier
        industry_mult = {
            "Healthcare": 1.8,
            "Financial Services": 1.7,
            "Technology": 1.4,
            "Retail": 1.3,
            "Manufacturing": 1.2,
            "Other": 1.1
        }
        
        # AI risk multiplier
        ai_mult = {
            "Heavy - Core to business": 1.5,
            "Moderate - Regular use": 1.3,
            "Light - Occasional use": 1.1,
            "None": 1.0
        }
        
        # Security discount
        security_disc = {
            "Comprehensive (CogniGuard or equivalent)": 0.8,
            "Basic monitoring": 1.0,
            "None": 1.4
        }
        
        # Calculate
        premium_with_security = base * industry_mult[industry] * ai_mult[ai_usage] * 0.8
        premium_without = base * industry_mult[industry] * ai_mult[ai_usage] * 1.4
        
        savings = premium_without - premium_with_security
        
        # Display
        st.markdown("### 💰 Premium Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "With CogniGuard",
                f"${premium_with_security:,.0f}/year",
                "-20% discount"
            )
        
        with col2:
            st.metric(
                "Without AI Security",
                f"${premium_without:,.0f}/year",
                "+40% surcharge"
            )
        
        with col3:
            st.metric(
                "Annual Savings",
                f"${savings:,.0f}",
                "With CogniGuard"
            )
        
        st.success(f"""
        ### ✅ CogniGuard ROI from Insurance Alone:
        
        **Annual premium savings: ${savings:,.0f}**
        
        This doesn't even count:
        - Prevented breach costs
        - Avoided claim denials
        - Reduced deductibles
        - Better coverage terms
        
        **CogniGuard often pays for itself just in insurance savings.**
        """)
    
    # What Insurers Want to See
    st.markdown("---")
    st.header("✅ What Insurance Companies Want to See")
    
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │         CYBER INSURANCE AI SECURITY REQUIREMENTS                │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   ✅ AI INTERACTION MONITORING                                 │
    │   CogniGuard logs all AI inputs and outputs                   │
    │                                                                 │
    │   ✅ THREAT DETECTION                                          │
    │   CogniGuard detects prompt injection and attacks             │
    │                                                                 │
    │   ✅ DATA LOSS PREVENTION                                      │
    │   CogniGuard prevents sensitive data leakage                  │
    │                                                                 │
    │   ✅ INCIDENT RESPONSE CAPABILITY                              │
    │   CogniGuard enables rapid response to AI incidents           │
    │                                                                 │
    │   ✅ AUDIT TRAIL                                               │
    │   CogniGuard provides complete compliance documentation       │
    │                                                                 │
    │   ✅ CONTINUOUS IMPROVEMENT                                    │
    │   CogniGuard updates threat detection automatically           │
    │                                                                 │
    │   Show insurers your CogniGuard deployment = Better terms     │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    ```
    """)


# This allows the demo to run on its own
if __name__ == "__main__":
    show_insurance_demo()