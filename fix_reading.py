# This script fixes reading patterns in app.py

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix reading patterns (NOT followed by =)
# We need to be careful to only replace reading, not assignment

import re

# Pattern: st.session_state.NAME where NAME is followed by : or ) or \n or space (not =)
reading_patterns = [
    # In if statements and other reading contexts
    (r"st\.session_state\.database([^=\w])", r"st.session_state.get('database')\1"),
    (r"st\.session_state\.ai_manager([^=\w])", r"st.session_state.get('ai_manager')\1"),
    (r"st\.session_state\.engine([^=\w])", r"st.session_state.get('engine')\1"),
    (r"st\.session_state\.semantic_engine([^=\w])", r"st.session_state.get('semantic_engine')\1"),
    (r"st\.session_state\.conversation_analyzer([^=\w])", r"st.session_state.get('conversation_analyzer')\1"),
    (r"st\.session_state\.threat_learner([^=\w])", r"st.session_state.get('threat_learner')\1"),
    (r"st\.session_state\.enhanced_engine([^=\w])", r"st.session_state.get('enhanced_engine')\1"),
]

for pattern, replacement in reading_patterns:
    content = re.sub(pattern, replacement, content)

# But we need to undo any that are part of assignment (fix double .get)
# Fix patterns like: st.session_state.get('name') = 
assignment_fixes = [
    ("st.session_state.get('database') =", "st.session_state.database ="),
    ("st.session_state.get('ai_manager') =", "st.session_state.ai_manager ="),
    ("st.session_state.get('engine') =", "st.session_state.engine ="),
    ("st.session_state.get('semantic_engine') =", "st.session_state.semantic_engine ="),
    ("st.session_state.get('conversation_analyzer') =", "st.session_state.conversation_analyzer ="),
    ("st.session_state.get('threat_learner') =", "st.session_state.threat_learner ="),
    ("st.session_state.get('enhanced_engine') =", "st.session_state.enhanced_engine ="),
]

for wrong, correct in assignment_fixes:
    content = content.replace(wrong, correct)

# Save
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Fixed reading patterns in app.py")