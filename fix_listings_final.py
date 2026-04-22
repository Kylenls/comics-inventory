with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix 1: Call lgenRenderQueue when listings tab is activated
old_switch = "if (tab === 'listings') {"
new_switch = "if (tab === 'listings') { if (typeof lgenRenderQueue === 'function') lgenRenderQueue();"

if old_switch in content:
    content = content.replace(old_switch, new_switch, 1)
    print("Fix 1: lgenRenderQueue called on tab switch")
else:
    # Try finding switchTab and adding it
    old_switch2 = "if (tab === 'agents') loadAgentLog('1');"
    new_switch2 = "if (tab === 'agents') loadAgentLog('1');\n  if (tab === 'listings' && typeof lgenRenderQueue === 'function') lgenRenderQueue();"
    if old_switch2 in content:
        content = content.replace(old_switch2, new_switch2, 1)
        print("Fix 1 (alt): lgenRenderQueue called on tab switch")
    else:
        print("Fix 1 FAILED")

# Fix 2: Change listings panel from side-by-side to top-bottom
old_grid = 'display:grid;grid-template-columns:45% 55%;gap:16px;min-height:calc(100vh - 120px)'
new_grid = 'display:flex;flex-direction:column;gap:16px'

if old_grid in content:
    content = content.replace(old_grid, new_grid, 1)
    print("Fix 2: Layout changed to top-bottom")
else:
    print("Fix 2 FAILED")

# Fix 3: Remove the overflow/padding constraints from left panel
old_left = '<div style="overflow-y:auto;padding-right:8px">'
new_left = '<div>'
if old_left in content:
    content = content.replace(old_left, new_left, 1)
    print("Fix 3: Left panel constraints removed")

old_right = '<div style="overflow-y:auto">'
new_right = '<div>'
if old_right in content:
    content = content.replace(old_right, new_right, 1)
    print("Fix 3b: Right panel constraints removed")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)