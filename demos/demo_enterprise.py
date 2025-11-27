"""
=============================================================================
DEMO 6: ENTERPRISE SALES ENABLEMENT
=============================================================================
This demo shows how CogniGuard helps win enterprise deals.
"""

import streamlit as st

def show_enterprise_demo():
    """
    This function displays the Enterprise Sales demo.
    """
    
    # Page Title
    st.title("🏢 Enterprise Sales: Win or Lose on Security")
    st.markdown("### You CAN'T Sell to Enterprises Without AI Security")
    
    # Warning Box
    st.warning("""
    💼 **SALES REALITY**: Enterprise customers now require AI security controls. 
    Without them, your deal goes to a competitor who has them.
    """)
    
    # The Problem
    st.markdown("---")
    st.header("🚫 The Deal Killer")
    
    st.error("""
    ### What Your Prospect's Security Team Says:
    
    *"We love your AI product, but our security team won't approve it 
    without AI-specific security controls and documentation."*
    
    **This is happening NOW. Companies are losing deals every day.**
    """)
    
    # Enterprise Requirements
    st.markdown("---")
    st.header("📋 What Enterprise Customers Require")
    
    st.markdown("""
    ### Security Questionnaire (200+ Questions Including):
    
    | Requirement | What They Want | Can You Provide It? |
    |-------------|----------------|---------------------|
    | SOC 2 Type II | Audit certification | ❓ |
    | AI/ML Security Controls | Protection against AI attacks | ❓ |
    | Prompt Injection Protection | Defense against injection | ❓ |
    | AI Output Monitoring | Track what AI produces | ❓ |
    | Audit Logging | Complete interaction history | ❓ |
    | Data Loss Prevention | Prevent sensitive data leaks | ❓ |
    | Incident Response Plan | How you handle AI attacks | ❓ |
    | Bias Detection | Catch discriminatory outputs | ❓ |
    """)
    
    # Interactive Demo
    st.markdown("---")
    st.header("🧪 Interactive: Security Questionnaire Simulator")
    
    st.info("See how you'd answer a typical enterprise security questionnaire.")
    
    # Questions
    st.markdown("### Sample Security Questions:")
    
    q1 = st.radio(
        "1. How do you monitor AI inputs and outputs?",
        [
            "We have comprehensive real-time monitoring with CogniGuard",
            "We do periodic manual reviews",
            "We rely on the AI provider's built-in safety",
            "We don't currently monitor AI interactions"
        ],
        index=3
    )
    
    q2 = st.radio(
        "2. What controls prevent prompt injection attacks?",
        [
            "CogniGuard scans all inputs for injection patterns",
            "We have basic input validation",
            "We trust our users not to attack",
            "We don't have specific controls"
        ],
        index=3
    )
    
    q3 = st.radio(
        "3. How do you prevent sensitive data from leaking through AI?",
        [
            "CogniGuard DLP scans all inputs and outputs",
            "We have policies telling users to be careful",
            "The AI provider handles this",
            "We don't have DLP for AI"
        ],
        index=3
    )
    
    q4 = st.radio(
        "4. Can you provide audit logs of AI interactions?",
        [
            "Yes - CogniGuard logs everything, searchable and exportable",
            "We have some logging but it's not comprehensive",
            "Logs are with our AI provider",
            "We don't maintain AI interaction logs"
        ],
        index=3
    )
    
    if st.button("📊 See Evaluation Results", type="primary"):
        
        # Count good answers
        good_answers = 0
        if "CogniGuard" in q1: good_answers += 1
        if "CogniGuard" in q2: good_answers += 1
        if "CogniGuard" in q3: good_answers += 1
        if "CogniGuard" in q4: good_answers += 1
        
        st.markdown("### 📋 Security Team Evaluation")
        
        if good_answers >= 3:
            st.success("""
            ## ✅ APPROVED
            
            **Security Team Notes:**
            "This vendor demonstrates comprehensive AI security controls.
            They have monitoring, threat detection, DLP, and audit capabilities.
            Recommend proceeding with evaluation."
            
            **Result: DEAL MOVES FORWARD** 🎉
            """)
        elif good_answers >= 1:
            st.warning("""
            ## ⚠️ CONDITIONAL APPROVAL
            
            **Security Team Notes:**
            "Vendor has some security controls but gaps remain.
            Require additional documentation and possibly security improvements
            before final approval."
            
            **Result: DEAL DELAYED 3-6 MONTHS** ⏳
            """)
        else:
            st.error("""
            ## ❌ REJECTED
            
            **Security Team Notes:**
            "Vendor lacks adequate AI security controls.
            Cannot approve for use with our data or systems.
            Significant security investment required before reconsideration."
            
            **Result: DEAL LOST TO COMPETITOR** 💔
            """)
    
    # The Winning Pitch
    st.markdown("---")
    st.header("✅ The Winning Sales Pitch")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.error("""
        ### ❌ Without CogniGuard:
        
        **Prospect:** "What AI security do you have?"
        
        **You:** "ChatGPT has safety features built in..."
        
        **Prospect:** "Can you show audit logs?"
        
        **You:** "We can request them from OpenAI..."
        
        **Prospect:** "What about prompt injection?"
        
        **You:** "We tell users to be careful..."
        
        ---
        
        **Result:** ❌ Deal lost
        **Prospect:** "Going with competitor who has proper security"
        """)
    
    with col2:
        st.success("""
        ### ✅ With CogniGuard:
        
        **Prospect:** "What AI security do you have?"
        
        **You:** "Let me show you our CogniGuard dashboard..."
        
        **Prospect:** "Can you show audit logs?"
        
        **You:** "Here's our complete searchable history..."
        
        **Prospect:** "What about prompt injection?"
        
        **You:** "Real-time detection - watch this demo..."
        
        ---
        
        **Result:** ✅ Deal closed
        **Prospect:** "Your security exceeded our requirements"
        """)
    
    # Sales Materials
    st.markdown("---")
    st.header("📁 CogniGuard Sales Enablement")
    
    st.markdown("""
    ### What CogniGuard Provides for Your Sales Team:
    
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │              SALES ENABLEMENT PACKAGE                           │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   📄 SECURITY DOCUMENTATION                                    │
    │   • Pre-filled security questionnaire responses                │
    │   • Architecture diagrams                                      │
    │   • Compliance certifications                                  │
    │                                                                 │
    │   🎬 DEMO MATERIALS                                            │
    │   • Live threat detection demos                                │
    │   • Audit log walkthrough                                      │
    │   • ROI calculator                                             │
    │                                                                 │
    │   📊 PROOF POINTS                                              │
    │   • Customer case studies                                      │
    │   • Third-party validation                                     │
    │   • Benchmark reports                                          │
    │                                                                 │
    │   🤝 SALES SUPPORT                                             │
    │   • Security team call support                                 │
    │   • Custom demo environments                                   │
    │   • Technical deep-dives                                       │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.success("""
    ### 💰 The ROI of CogniGuard for Sales:
    
    **One enterprise deal saved = CogniGuard pays for itself many times over**
    
    Average enterprise AI deal: $100,000+/year
    CogniGuard cost: A fraction of that
    
    **Don't lose deals to security objections.**
    """)


# This allows the demo to run on its own
if __name__ == "__main__":
    show_enterprise_demo()