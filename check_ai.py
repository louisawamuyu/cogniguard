"""Diagnose AI Integration Issues"""

print("=" * 60)
print("AI INTEGRATION DIAGNOSTIC")
print("=" * 60)

import os

# ============================================================
# CHECK 1: Secrets File
# ============================================================
print("\n[1] Checking secrets file...")

secrets_path = ".streamlit/secrets.toml"

if os.path.exists(secrets_path):
    print(f"    [OK] Found: {secrets_path}")
    
    with open(secrets_path, 'r') as f:
        content = f.read()
    
    # Check for API keys
    keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic", 
        "GEMINI_API_KEY": "Gemini"
    }
    
    for key_name, provider in keys.items():
        if key_name in content:
            print(f"    [OK] {provider} key found")
        else:
            print(f"    [MISSING] {provider} key NOT found")
else:
    print(f"    [ERROR] Secrets file not found!")

# ============================================================
# CHECK 2: Import ai_integration
# ============================================================
print("\n[2] Checking ai_integration.py import...")

try:
    from ai_integration import AIIntegrationManager
    print("    [OK] AIIntegrationManager imported successfully!")
except ImportError as e:
    print(f"    [ERROR] Import failed: {e}")
except Exception as e:
    print(f"    [ERROR] Other error: {e}")

# ============================================================
# CHECK 3: Create AIIntegrationManager
# ============================================================
print("\n[3] Creating AIIntegrationManager...")

try:
    # We need to mock streamlit secrets for testing outside streamlit
    import sys
    
    # Read secrets manually
    secrets = {}
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    secrets[key] = value
    
    print(f"    Loaded {len(secrets)} secrets from file")
    
    # Set as environment variables for testing
    for key, value in secrets.items():
        os.environ[key] = value
        if "KEY" in key:
            print(f"    Set {key} = {value[:15]}...")

except Exception as e:
    print(f"    [ERROR] {e}")

# ============================================================
# CHECK 4: Test each provider
# ============================================================
print("\n[4] Testing AI providers...")

# Test OpenAI
openai_key = os.environ.get("OPENAI_API_KEY")
if openai_key:
    print("\n    --- OpenAI ---")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        print("    [OK] OpenAI client created!")
    except Exception as e:
        print(f"    [ERROR] OpenAI: {e}")
else:
    print("\n    --- OpenAI ---")
    print("    [SKIP] No API key")

# Test Anthropic
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if anthropic_key:
    print("\n    --- Anthropic ---")
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        print("    [OK] Anthropic client created!")
    except Exception as e:
        print(f"    [ERROR] Anthropic: {e}")
else:
    print("\n    --- Anthropic ---")
    print("    [SKIP] No API key")

# Test Gemini
gemini_key = os.environ.get("GEMINI_API_KEY")
if gemini_key:
    print("\n    --- Gemini ---")
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        print("    [OK] Gemini configured!")
    except Exception as e:
        print(f"    [ERROR] Gemini: {e}")
else:
    print("\n    --- Gemini ---")
    print("    [SKIP] No API key")

# ============================================================
# CHECK 5: Check ai_integration.py exists
# ============================================================
print("\n[5] Checking ai_integration.py file...")

if os.path.exists("ai_integration.py"):
    print("    [OK] ai_integration.py exists")
    
    # Check file size
    size = os.path.getsize("ai_integration.py")
    print(f"    File size: {size} bytes")
    
    if size < 100:
        print("    [WARN] File seems too small - might be empty or corrupted")
else:
    print("    [ERROR] ai_integration.py NOT FOUND!")

print("\n" + "=" * 60)
input("Press Enter to close...")