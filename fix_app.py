# This script fixes the wrong .get() replacements in app.py

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix wrong patterns (assignment with .get)
wrong_patterns = [
    ("st.session_state.get('semantic_engine') =", "st.session_state.semantic_engine ="),
    ("st.session_state.get('conversation_analyzer') =", "st.session_state.conversation_analyzer ="),
    ("st.session_state.get('threat_learner') =", "st.session_state.threat_learner ="),
    ("st.session_state.get('engine') =", "st.session_state.engine ="),
    ("st.session_state.get('ai_manager') =", "st.session_state.ai_manager ="),
    ("st.session_state.get('database') =", "st.session_state.database ="),
    ("st.session_state.get('chat_history') =", "st.session_state.chat_history ="),
    ("st.session_state.get('threat_log') =", "st.session_state.threat_log ="),
    ("st.session_state.get('current_conversation_id') =", "st.session_state.current_conversation_id ="),
    ("st.session_state.get('reported_threats') =", "st.session_state.reported_threats ="),
    ("st.session_state.get('enhanced_engine') =", "st.session_state.enhanced_engine ="),
]

for wrong, correct in wrong_patterns:
    content = content.replace(wrong, correct)

# Save the fixed file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Fixed all wrong .get() patterns in app.py")