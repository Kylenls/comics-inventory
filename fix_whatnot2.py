with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

whatnot_html = """
    <div class="card" style="margin-top:1rem">
      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">📺 Log Whatnot Show</div>
      <p style="font-size:13px;color:#6c757d;margin-bottom:1rem">Log total revenue from a Whatnot liquidation show.</p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
        <div>
          <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">SHOW DATE</label>
          <input type="date" id="whatnot-date" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
        </div>
        <div>
          <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">TOTAL REVENUE</label>
          <input type="number" id="whatnot-revenue" placeholder="0.00" step="0.01" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
        <div>
          <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">ITEMS SOLD</label>
          <input type="number" id="whatnot-items" placeholder="0" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
        </div>
        <div>
          <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">SHOW TYPE</label>
          <select id="whatnot-type" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px">
            <option>$1 Moderns</option>
            <option>$2 NCBD Variants</option>
            <option>Blind Bags</option>
            <option>Mixed Liquidation</option>
            <option>Other</option>
          </select>
        </div>
      </div>
      <div style="margin-bottom:8px">
        <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">NOTES</label>
        <input type="text" id="whatnot-notes" placeholder="Optional notes..." style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
      </div>
      <button class="btn btn-primary" onclick="logWhatnotShow()" style="width:100%">Log Show to Watcher</button>
      <div class="status" id="whatnot-status"></div>
    </div>"""

whatnot_js = """
async function logWhatnotShow() {
  const date = document.getElementById('whatnot-date').value;
  const revenue = parseFloat(document.getElementById('whatnot-revenue').value) || 0;
  const items = parseInt(document.getElementById('whatnot-items').value) || 0;
  const showType = document.getElementById('whatnot-type').value;
  const notes = document.getElementById('whatnot-notes').value;
  if (!date || revenue === 0) {
    showStatus('whatnot-status', 'Please enter date and revenue', 'error');
    return;
  }
  showStatus('whatnot-status', 'Logging show...', 'loading');
  try {
    const avgSale = items > 0 ? (revenue / items).toFixed(2) : 0;
    await fetch('/.netlify/functions/agent3', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trigger: 'sale',
        platform: 'Whatnot',
        title: 'Whatnot Show - ' + showType,
        salePrice: revenue,
        itemCount: items,
        saleDate: date,
        netProfit: revenue * 0.92 - (items * 0.50),
        platformFee: revenue * 0.08,
        daysOnMarket: 0,
        notes: notes
      })
    });
    showStatus('whatnot-status', 'Show logged! The Watcher has been notified.', 'success');
    document.getElementById('whatnot-revenue').value = '';
    document.getElementById('whatnot-items').value = '';
    document.getElementById('whatnot-notes').value = '';
  } catch(e) {
    showStatus('whatnot-status', 'Error: ' + e.message, 'error');
  }
}"""

# Find the end of the ebay summary card area and insert Whatnot after it
old = '<div class="status" id="ebay-age'
idx = content.find(old)
if idx > 0:
    # Find the end of that status div and the closing of the panel
    close = content.find('</div>\n\n  <!-- SELL', idx)
    if close > 0:
        content = content[:close] + whatnot_html + '\n' + content[close:]
        print("Whatnot HTML added to Sales tab")
    else:
        close2 = content.find('</div>\n\n  <!-- ', idx)
        print(f"Alt close at: {close2}")
        content = content[:close2] + whatnot_html + '\n' + content[close2:]
        print("Whatnot HTML added (alt)")
else:
    print(f"Could not find insertion point, ebay-age idx: {idx}")

# Add JS before barcode scanner
old_js = '</script>\n\n<!-- Barcode S'
if old_js in content:
    content = content.replace(old_js, whatnot_js + '\n</script>\n\n<!-- Barcode S', 1)
    print("Whatnot JS added")
else:
    print("JS insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)