import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from core.detection_engine import CogniGuardEngine, ThreatLevel
from simulations.sydney_simulation import SydneySimulation
from simulations.samsung_simulation import SamsungSimulation
from simulations.autogpt_simulation import AutoGPTSimulation

# Page config
st.set_page_config(
    page_title="CogniGuard - AI Safety Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS WITH SPACE/TECH FONTS
st.markdown("""
<style>
    /* Import Space/Tech Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap');
    
    /* Main Header with Orbitron Font */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    /* Threat Badges */
    .threat-critical {
        background-color: #ff4444;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .threat-high {
        background-color: #ff8800;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .threat-safe {
        background-color: #00C851;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Apply Tech Mono to all text */
    .main * {
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        font-family: 'Share Tech Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'engine' not in st.session_state:
    with st.spinner("🧠 Initializing CogniGuard Engine..."):
        st.session_state.engine = CogniGuardEngine()
    st.success("✅ Engine initialized!")

if 'threat_log' not in st.session_state:
    st.session_state.threat_log = []

# Sidebar
with st.sidebar:
    st.markdown("# 🛡️ CogniGuard")
    st.markdown("### AI Safety Platform")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", 
         "⚡ AGI Escalation Demo", 
         "🎯 Real-World Simulations", 
         "📚 Threat Vector Library", 
         "📡 Threat Intel Feed", 
         "🔬 Live Detection"]
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    st.success("✅ All Systems Operational")
    st.metric("Threats Blocked Today", len(st.session_state.threat_log))

# Main content - Dashboard
if page == "🏠 Dashboard":
    st.markdown('<h1 class="main-header">🛡️ CogniGuard AI Safety Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### The First Multi-Agent AI Communication Security Platform
    
    **SPACE/TECH THEME ACTIVE** - Fonts should look futuristic!
    
    CogniGuard protects against emerging threats in AI-to-AI communication:
    - 🎯 **Goal Hijacking Detection** - Prevents Sydney-style persona breaks
    - 🔒 **Data Exfiltration Prevention** - Stops Samsung-style leaks
    - ⚡ **Power-Seeking Containment** - Controls Auto-GPT chaos
    - 🤝 **Collusion Detection** - Identifies emergent agent coordination
    """)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Agents", "1,247", "+12")
    with col2:
        st.metric("Threats Blocked", "38", "+5")
    with col3:
        st.metric("Detection Speed", "12ms", "-3ms")
    with col4:
        st.metric("Accuracy", "94.7%", "+2.1%")
    
    # Font Test Section
    st.markdown("---")
    st.markdown("## 🔤 Font Display Test")
    
    st.markdown("**Header Font (Orbitron):**")
    st.markdown('<div style="font-family: \'Orbitron\', sans-serif; font-size: 2rem; font-weight: 900;">COGNIGUARD SPACE TECH THEME</div>', unsafe_allow_html=True)
    
    st.markdown("**Body Font (Share Tech Mono):**")
    st.markdown('<div style="font-family: \'Share Tech Mono\', monospace; font-size: 1.2rem;">The quick brown fox jumps over the lazy dog 0123456789</div>', unsafe_allow_html=True)
    
    # Threat level demo
    st.markdown("---")
    st.markdown("## 🚨 Threat Level Display Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="threat-critical">CRITICAL THREAT</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="threat-high">HIGH THREAT</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="threat-safe">SAFE</div>', unsafe_allow_html=True)

# Other pages
elif page == "⚡ AGI Escalation Demo":
    st.markdown('<h1 class="main-header">⚡ AGI Escalation Demo</h1>', unsafe_allow_html=True)
    st.info("Demo page - fonts should be Space/Tech theme!")

elif page == "🎯 Real-World Simulations":
    st.markdown('<h1 class="main-header">🎯 Real-World Simulations</h1>', unsafe_allow_html=True)
    st.info("Simulations page - fonts should be Space/Tech theme!")

elif page == "📚 Threat Vector Library":
    st.markdown('<h1 class="main-header">📚 Threat Vector Library</h1>', unsafe_allow_html=True)
    st.info("Library page - fonts should be Space/Tech theme!")

elif page == "📡 Threat Intel Feed":
    st.markdown('<h1 class="main-header">📡 Threat Intel Feed</h1>', unsafe_allow_html=True)
    st.info("Feed page - fonts should be Space/Tech theme!")

elif page == "🔬 Live Detection":
    st.markdown('<h1 class="main-header">🔬 Live Detection</h1>', unsafe_allow_html=True)
    st.info("Detection page - fonts should be Space/Tech theme!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <p style='font-family: "Orbitron", sans-serif; font-size: 1.5rem; font-weight: 900;'>🛡️ COGNIGUARD AI SAFETY PLATFORM</p>
    <p>Protecting the Future of Multi-Agent AI Communication</p>
</div>
""", unsafe_allow_html=True)