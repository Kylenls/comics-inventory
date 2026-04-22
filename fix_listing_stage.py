with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix 1: Remove checkPCDeepLink calls since function is gone
content = content.replace('\ncheckPCDeepLink();\n', '\n', )
print("Removed checkPCDeepLink calls:", content.count('checkPCDeepLink'))

# Fix 2: Fix agent2BuildDraftByKey to not call setListingMode
old_stage = """  renderStagedBar();

  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ Staged (' + stagedBundles.length + ' total) — click the blue bar to send all</span>';
  }
}"""

new_stage = """  renderStagedBar();

  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">📋 Staged (' + stagedBundles.length + ' total) — click blue bar at bottom to send all</span>';
  }
}"""

if old_stage in content:
    content = content.replace(old_stage, new_stage, 1)
    print("Stage message updated")

# Fix 3: Update button label
old_btn = '⚔️ Taskmaster — Build Draft Listing'
new_btn = '📋 Stage for Listing Generator'
content = content.replace(old_btn, new_btn)
print("Button renamed")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)