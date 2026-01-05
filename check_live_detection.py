"""Check Live Detection Page Issues"""

print("=" * 60)
print("LIVE DETECTION PAGE DIAGNOSTIC")
print("=" * 60)

# Check 1: Can we find the Live Detection page code?
print("\n[1] Checking app.py for Live Detection page...")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'Live Detection' in content:
    print("    [OK] Found 'Live Detection' in app.py")
else:
    print("    [ERROR] 'Live Detection' not found!")

if 'elif page == "🔬 Live Detection"' in content:
    print("    [OK] Found Live Detection page handler")
else:
    print("    [WARN] Page handler might be missing or different")

# Check 2: Look for the analyze button
if 'Analyze Message' in content:
    print("    [OK] Found 'Analyze Message' button")
else:
    print("    [WARN] Analyze button might be missing")

# Check 3: Check for engine usage
if 'engine.detect' in content or 'st.session_state.engine' in content:
    print("    [OK] Found engine usage")
else:
    print("    [WARN] Engine might not be used")

# Check 4: Look for common issues
if 'st.session_state.get(' in content:
    print("    [OK] Using safe session state access")

# Count the page
import re
live_detection_count = len(re.findall(r'Live Detection', content))
print(f"\n    'Live Detection' appears {live_detection_count} times in app.py")

# Find the line number of the page handler
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'elif page == "🔬 Live Detection"' in line or "elif page == '🔬 Live Detection'" in line:
        print(f"\n    Page handler found at line {i+1}")
        print(f"    Next 5 lines:")
        for j in range(i, min(i+5, len(lines))):
            print(f"      {j+1}: {lines[j][:70]}")
        break

print("\n" + "=" * 60)
input("Press Enter to close...")