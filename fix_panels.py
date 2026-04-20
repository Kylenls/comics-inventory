with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the Mark Sold card inside panel-ebay
sell_marker = '<div class="card">\n      <div class="defaults-title" style="font-size:13px;font-weight:600;margin-bottom:8px">💰 Mark Sold</div>'

sell_start = content.find(sell_marker)
if sell_start == -1:
    print("Sell marker not found")
else:
    # Find the closing of panel-ebay before the sell content
    # We need to close panel-ebay and open panel-sell at sell_start
    old = content[sell_start:sell_start+len(sell_marker)]
    new = '</div>\n\n  <div class="panel" id="panel-sell">\n    ' + sell_marker
    content = content.replace(old, new, 1)
    print("Panel split done")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)