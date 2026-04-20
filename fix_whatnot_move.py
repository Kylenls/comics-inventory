with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the Whatnot card in the Sold panel
whatnot_start = content.find('\n    <div class="card" style="margin-top:1rem">\n      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">📺 Log Whatnot Show</div>')
whatnot_end = content.find('\n    <div class="card">', whatnot_start + 100)

if whatnot_start > 0 and whatnot_end > 0:
    whatnot_block = content[whatnot_start:whatnot_end]
    print(f"Found Whatnot block: {len(whatnot_block)} chars")
    
    # Remove from Sold panel
    content = content.replace(whatnot_block, '', 1)
    
    # Add to end of Sales panel (before closing div of panel-ebay)
    # Find the ebay-agent-status div which is the last thing in Sales
    insert_after = '<div class="status" id="ebay-agent-status"></div>\n    </div>'
    new_insert = '<div class="status" id="ebay-agent-status"></div>\n    </div>\n' + whatnot_block
    
    if insert_after in content:
        content = content.replace(insert_after, new_insert, 1)
        print("Whatnot moved to Sales tab")
    else:
        print("Could not find insertion point")
        idx = content.find('ebay-agent-status')
        print(content[idx:idx+100])
else:
    print(f"Whatnot not found: start={whatnot_start} end={whatnot_end}")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)