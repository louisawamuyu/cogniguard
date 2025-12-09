"""Fix AI Integration in app.py"""

print("=" * 50)
print("FIXING AI INTEGRATION")
print("=" * 50)

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ============================================================
# FIX 1: Add AI Integration import if missing
# ============================================================
if 'from ai_integration import AIIntegrationManager' not in content:
    import_code = '''
# AI Integration import
try:
    from ai_integration import AIIntegrationManager
    AI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    AI_INTEGRATION_AVAILABLE = False
    AIIntegrationManager = None
    print(f"AI Integration not available: {e}")
'''
    # Add after streamlit import
    content = content.replace(
        'import streamlit as st',
        'import streamlit as st' + import_code,
        1
    )
    changes += 1
    print("[OK] Added AI Integration import")
else:
    print("[SKIP] AI Integration import already exists")

# ============================================================
# FIX 2: Add AI Manager initialization if missing
# ============================================================
if "'ai_manager' not in st.session_state" not in content:
    init_code = '''
# Initialize AI Integration Manager
if 'ai_manager' not in st.session_state:
    try:
        from ai_integration import AIIntegrationManager
        st.session_state.ai_manager = AIIntegrationManager()
    except Exception as e:
        st.session_state.ai_manager = None
        print(f"AI Manager error: {e}")

'''
    # Find where to add it
    if "'engine' not in st.session_state" in content:
        # Add after engine initialization
        import re
        pattern = r"(if 'engine' not in st\.session_state:.*?st\.session_state\.engine = None)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            end_pos = match.end()
            content = content[:end_pos] + "\n" + init_code + content[end_pos:]
            changes += 1
            print("[OK] Added AI Manager initialization")
    else:
        print("[WARN] Could not find where to add AI Manager init")
else:
    print("[SKIP] AI Manager initialization already exists")

# ============================================================
# Save
# ============================================================
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[DONE] Made {changes} changes")
print("Now run: streamlit run app.py")
print("=" * 50)