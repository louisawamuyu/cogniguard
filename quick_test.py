"""
Quick test to verify models work
"""

print("🧪 Quick Model Test")
print("=" * 50)

# Load secrets
secrets = {}
with open(".streamlit/secrets.toml", 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            secrets[key.strip()] = value.strip().strip('"').strip("'")

# Test Claude
print("\n🧠 Testing Claude (claude-sonnet-4-20250514)...")
try:
    from anthropic import Anthropic
    client = Anthropic(api_key=secrets['ANTHROPIC_API_KEY'])
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'Claude works!' in 3 words"}]
    )
    print(f"   ✅ Response: {response.content[0].text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Gemini
print("\n✨ Testing Gemini (gemini-pro-latest)...")
try:
    import google.generativeai as genai
    genai.configure(api_key=secrets['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-pro-latest')
    response = model.generate_content("Say 'Gemini works!' in 3 words")
    print(f"   ✅ Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test OpenAI
print("\n🤖 Testing OpenAI (gpt-4o)...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'GPT works!' in 3 words"}]
    )
    print(f"   ✅ Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test complete!")
input("\nPress Enter to close...")