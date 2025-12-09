"""Fix all database issues in app.py"""

import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = 0

# ============================================================
# FIX 1: Add database import if missing
# ============================================================
if 'from database import ThreatDatabase' not in content:
    # Find where to add it (after streamlit import)
    import_code = '''
# Database import
try:
    from database import ThreatDatabase
    DATABASE_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    ThreatDatabase = None
'''
    # Add after "import streamlit as st"
    content = content.replace(
        'import streamlit as st',
        'import streamlit as st' + import_code,
        1
    )
    changes_made += 1
    print("[OK] Added database import")

# ============================================================
# FIX 2: Add database initialization if missing
# ============================================================
if "'database' not in st.session_state" not in content:
    init_code = '''
# Initialize Database
if 'database' not in st.session_state:
    try:
        from database import ThreatDatabase
        db = ThreatDatabase()
        if db.is_connected():
            st.session_state.database = db
        else:
            st.session_state.database = None
    except Exception as e:
        st.session_state.database = None

'''
    # Find where to add it (after other session state inits)
    if "'engine' not in st.session_state" in content:
        # Find the end of engine init and add after
        # Look for the pattern where engine is set to None
        pattern = r"(st\.session_state\.engine = None)"
        if re.search(pattern, content):
            content = re.sub(pattern, r"\1\n" + init_code, content, count=1)
            changes_made += 1
            print("[OK] Added database initialization")
    else:
        # Add at a reasonable place
        if "st.set_page_config" in content:
            content = content.replace(
                "st.set_page_config",
                init_code + "\nst.set_page_config",
                1
            )
            changes_made += 1
            print("[OK] Added database initialization")

# ============================================================
# FIX 3: Fix sidebar database status check
# ============================================================

# Pattern for wrong checks
wrong_patterns = [
    r"if DATABASE_AVAILABLE and st\.session_state\.database:",
    r"if st\.session_state\.database:",
    r"if DATABASE_AVAILABLE and st\.session_state\.get\('database'\):",
]

correct_check = "if st.session_state.get('database') is not None and hasattr(st.session_state.get('database'), 'is_connected') and st.session_state.get('database').is_connected():"

for pattern in wrong_patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, correct_check, content)
        changes_made += 1
        print("[OK] Fixed database status check")
        break

# ============================================================
# Save changes
# ============================================================
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[DONE] Made {changes_made} changes to app.py")
print("Now run: streamlit run app.py")