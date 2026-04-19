with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Rename eBay tab to Sales
content = content.replace(
    "onclick=\"switchTab('ebay')\">eBay</button>",
    "onclick=\"switchTab('ebay')\">Sales</button>",
    1
)
print("Tab renamed" if "Sales</button>" in content else "Tab rename failed")

# Update the eBay panel header
content = content.replace(
    '<div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">Import eBay Sales History</div>',
    '<div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">📦 Import eBay Sales History</div>',
    1
)

# Move Whatnot log from Sold tab to eBay/Sales panel
# First find and extract the whatnot card from sell panel
whatnot_start = content.find('\n    <div class="card" style="margin-top:1rem">\n      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">📺 Log Whatnot Show</div>')
if whatnot_start > 0:
    whatnot_end = content.find('\n    <div class="card"', whatnot_start + 100)
    if whatnot_end == -1:
        whatnot_end = content.find('\n  </div>\n\n  <!-- ', whatnot_start)
    whatnot_block = content[whatnot_start:whatnot_end]
    # Remove from sell panel
    content = content.replace(whatnot_block, '', 1)
    print(f"Whatnot block extracted: {len(whatnot_block)} chars")
    
    # Add to end of ebay panel before closing
    old_ebay_end = '<div class="status" id="ebay-age'
    idx = content.find(old_ebay_end)
    if idx > 0:
        # Find the closing div of ebay panel
        close_idx = content.find('\n  </div>\n\n  <!-- SELL', idx)
        if close_idx > 0:
            content = content[:close_idx] + '\n' + whatnot_block + content[close_idx:]
            print("Whatnot moved to Sales tab")
        else:
            print("Could not find ebay panel end")
    else:
        print("Could not find ebay status div")
else:
    print("Whatnot block not found in sell panel")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)