with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the sell/sold tab panel and add Whatnot show log section
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
    </div>
"""

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
    
    // Log to Airtable Cash Flow table
    const res = await callAirtable({
      action: 'create',
      table: 'tblZ4JKl5J2SHdxak',
      fields: {
        'Date': date,
        'Description': 'Whatnot Show - ' + showType,
        'Amount': revenue,
        'Type': 'Income',
        'Notes': items + ' items @ avg $' + avgSale + (notes ? ' | ' + notes : ''),
        'Platform': 'Whatnot'
      }
    });

    // Notify Watcher
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
}
"""

# Add Whatnot HTML to the sell panel
old_html = '<!-- SELL TAB -->'
if old_html not in content:
    # Find sell panel differently
    idx = content.find('panel-sell')
    if idx > 0:
        # Find end of first card in sell panel
        end_card = content.find('</div>\n\n    <div class="card"', idx)
        if end_card == -1:
            end_card = content.find('</div>\n  </div>\n\n  <!-- ', idx)
        print(f"Sell panel at {idx}, inserting at {end_card}")
        content = content[:end_card+6] + '\n' + whatnot_html + content[end_card+6:]
    else:
        print("Sell panel not found")
else:
    print("Found sell tab comment")

# Add Whatnot JS
old_js = '</script>\n\n<!-- Barcode S'
new_js = whatnot_js + '\n</script>\n\n<!-- Barcode S'
content = content.replace(old_js, new_js, 1)

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)

print("Done")