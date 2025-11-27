"""
=============================================================================
DEMO 4: LIABILITY EXPOSURE
=============================================================================
This demo shows legal risks of AI without security and real lawsuit examples.
"""

import streamlit as st

def show_liability_demo():
    """
    This function displays the Liability Exposure demo.
    """
    
    # Page Title
    st.title("⚖️ Liability Exposure: AI Lawsuits")
    st.markdown("### You WILL Be Sued - Real Cases Are Happening Now")
    
    # Warning Box
    st.error("""
    🚨 **LEGAL REALITY**: Courts are ruling that companies ARE LIABLE for their 
    AI's outputs. "We used a third-party AI" is NOT a valid defense.
    """)
    
    # Real Cases
    st.markdown("---")
    st.header("📚 Real Lawsuit Cases")
    
    # Case 1
    st.markdown("""
    ### 📌 Case 1: Air Canada Chatbot (2024)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **What Happened:**
        - Customer asked AI chatbot about bereavement fares
        - AI gave WRONG information about refund policy
        - Customer booked flight based on AI's advice
        - Airline refused refund (AI was wrong)
        - Customer sued Air Canada
        """)
    
    with col2:
        st.error("""
        **Court Ruling:**
        
        ⚖️ **AIRLINE LIABLE** for AI's statements
        
        The court said:
        *"Air Canada is responsible for all 
        information on its website, including 
        information provided by its chatbot."*
        
        **Damages:** Full refund + legal costs
        """)
    
    # Case 2
    st.markdown("""
    ### 📌 Case 2: Lawyer Uses ChatGPT (2023)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **What Happened:**
        - Lawyer used ChatGPT for legal research
        - AI invented FAKE court cases that don't exist
        - Lawyer submitted these fake cases to court
        - Judge discovered the cases were fabricated
        - Lawyer faced sanctions
        """)
    
    with col2:
        st.error("""
        **Consequences:**
        
        ⚖️ **LAWYER SANCTIONED**
        
        - $5,000 fine
        - Professional discipline
        - Reputation destroyed
        - Potential malpractice lawsuit from client
        
        *"There is nothing 'artificial' about the
        consequences of submitting fake cases."*
        - Judge
        """)
    
    # Case 3
    st.markdown("""
    ### 📌 Case 3: Healthcare AI Misdiagnosis (Ongoing)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **What's Happening:**
        - AI systems used for medical diagnoses
        - AI misses critical conditions
        - Patients harmed by delayed treatment
        - Lawsuits being filed across the country
        """)
    
    with col2:
        st.error("""
        **Legal Exposure:**
        
        ⚖️ **MULTIPLE LIABILITY THEORIES**
        
        - Medical malpractice
        - Product liability
        - Negligence
        - Failure to warn
        
        **Potential damages:** Millions per case
        """)
    
    # Liability Matrix
    st.markdown("---")
    st.header("📊 Your Liability Exposure")
    
    st.markdown("""
    | Scenario | Without CogniGuard | With CogniGuard |
    |----------|-------------------|-----------------|
    | AI leaks customer data | 🔴 GDPR fines + class action | ✅ Blocked, logged, prevented |
    | AI gives harmful advice | 🔴 Product liability lawsuit | ✅ Detected, flagged, stopped |
    | AI is manipulated by attacker | 🔴 Negligence claims | ✅ Attack detected and blocked |
    | AI discriminates in decisions | 🔴 Civil rights violations | ✅ Bias patterns detected |
    | AI reveals trade secrets | 🔴 Breach of confidentiality | ✅ DLP prevents disclosure |
    | AI makes unauthorized commitments | 🔴 Contract liability | ✅ Output monitoring catches it |
    """)
    
    # Interactive Risk Calculator
    st.markdown("---")
    st.header("🧮 Interactive: Liability Risk Calculator")
    
    st.info("Estimate your potential liability exposure from AI risks.")
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        users = st.number_input(
            "Number of AI users in your organization:",
            min_value=1,
            max_value=100000,
            value=100
        )
        
        interactions = st.number_input(
            "Average AI interactions per user per day:",
            min_value=1,
            max_value=1000,
            value=10
        )
    
    with col2:
        customer_data = st.selectbox(
            "Does your AI access customer data?",
            ["Yes - Sensitive data (PII, financial, health)", 
             "Yes - Basic data only",
             "No customer data access"]
        )
        
        industry = st.selectbox(
            "Your industry:",
            ["Healthcare", "Financial Services", "Legal", 
             "Technology", "Retail", "Other"]
        )
    
    if st.button("⚖️ Calculate Risk Exposure", type="primary"):
        
        # Calculate daily interactions
        daily_interactions = users * interactions
        annual_interactions = daily_interactions * 365
        
        # Base risk factors
        base_risk = 0.0001  # 0.01% base incident rate
        
        # Adjust for data sensitivity
        if "Sensitive" in customer_data:
            data_multiplier = 10
            fine_multiplier = 5
        elif "Basic" in customer_data:
            data_multiplier = 3
            fine_multiplier = 2
        else:
            data_multiplier = 1
            fine_multiplier = 1
        
        # Adjust for industry
        industry_multipliers = {
            "Healthcare": 15,
            "Financial Services": 12,
            "Legal": 10,
            "Technology": 5,
            "Retail": 3,
            "Other": 2
        }
        industry_mult = industry_multipliers[industry]
        
        # Calculate exposure
        incident_probability = min(base_risk * data_multiplier * industry_mult * 100, 25)
        avg_incident_cost = 50000 * fine_multiplier * industry_mult
        annual_risk_exposure = incident_probability / 100 * avg_incident_cost * (annual_interactions / 1000000)
        
        # Display results
        st.markdown("### 📊 Your Risk Assessment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Annual AI Interactions",
                f"{annual_interactions:,}"
            )
        
        with col2:
            st.metric(
                "Incident Probability",
                f"{incident_probability:.1f}%"
            )
        
        with col3:
            st.metric(
                "Estimated Annual Risk",
                f"${annual_risk_exposure:,.0f}"
            )
        
        # Risk breakdown
        st.markdown("### 💰 Potential Incident Costs")
        
        st.markdown(f"""
        | Incident Type | Average Cost | Your Exposure |
        |---------------|--------------|---------------|
        | Data breach (per record) | $164 | ${164 * users * data_multiplier:,} |
        | Regulatory fine | ${100000 * fine_multiplier:,} | ${100000 * fine_multiplier:,} |
        | Litigation (per case) | ${500000 * industry_mult:,} | ${500000 * industry_mult:,} |
        | Reputation damage | ${1000000 * data_multiplier:,} | ${1000000 * data_multiplier:,} |
        """)
        
        st.error(f"""
        ### 🚨 Total Maximum Exposure: ${(164 * users * data_multiplier) + (100000 * fine_multiplier) + (500000 * industry_mult) + (1000000 * data_multiplier):,}
        
        Without AI security controls, you could face this amount in damages from a single major incident.
        """)
        
        st.success("""
        ### ✅ CogniGuard ROI
        
        CogniGuard costs a fraction of a single incident while:
        - Preventing data breaches
        - Blocking AI manipulation
        - Documenting due diligence
        - Providing legal defense evidence
        
        **The question isn't whether you can afford CogniGuard.
        It's whether you can afford NOT to have it.**
        """)
    
    # Legal Defense
    st.markdown("---")
    st.header("🛡️ CogniGuard as Legal Protection")
    
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │              COGNIGUARD LEGAL PROTECTION                        │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   📋 DUE DILIGENCE DOCUMENTATION                               │
    │   "We implemented industry-standard AI security controls"       │
    │                                                                 │
    │   📊 AUDIT TRAIL                                               │
    │   "Here are complete logs showing our security measures"        │
    │                                                                 │
    │   🛡️ INCIDENT PREVENTION                                       │
    │   "Our system blocked the attack before harm occurred"          │
    │                                                                 │
    │   📈 CONTINUOUS MONITORING                                      │
    │   "We actively monitor and improve our AI security"             │
    │                                                                 │
    │   ✅ BEST PRACTICES                                            │
    │   "We follow recognized AI security frameworks"                 │
    │                                                                 │
    │   These become your LEGAL DEFENSE in any lawsuit.              │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    ```
    """)


# This allows the demo to run on its own
if __name__ == "__main__":
    show_liability_demo()