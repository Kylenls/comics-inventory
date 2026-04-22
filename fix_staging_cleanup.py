with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix 1: Remove checkPCDeepLink calls
content = content.replace('\ncheckPCDeepLink();\n', '\n')
content = content.replace('checkPCDeepLink();\n', '')
content = content.replace('checkPCDeepLink();', '')
remaining = content.count('checkPCDeepLink')
print("checkPCDeepLink remaining:", remaining)

# Fix 2: Update button label
old_btn = '⚔️ Taskmaster — Build Draft Listing'
new_btn = '📋 Stage for Listing Generator'
count = content.count(old_btn)
content = content.replace(old_btn, new_btn)
print("Button renamed:", count, "instances")

# Fix 3: Remove setListingMode call from agent2BuildDraftByKey
content = content.replace(
    "  // Load bundle into listing generator\n  listingBundle = item.bundleData;\n  setListingMode('bundle');",
    "  // Load bundle data\n  listingBundle = item.bundleData;",
    1
)
print("Removed setListingMode call from activateQueueItem")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)