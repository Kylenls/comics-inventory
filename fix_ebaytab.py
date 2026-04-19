with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

new_functions = """
async function handleEbayFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  handleEbayCSV(file);
  event.target.value = '';
}

function handleEbayDrop(event) {
  event.preventDefault();
  document.getElementById('ebay-drop-zone').classList.remove('drag-over');
  const file = event.dataTransfer.files[0];
  if (file) handleEbayCSV(file);
}

async function handleEbayCSV(file) {
  showStatus('ebay-status', 'Reading eBay orders...', 'loading');
  const reader = new FileReader();
  reader.onload = async (e) => {
    const text = e.target.result;
    const lines = text.split('\\n');
    let headerIdx = -1;
    let headers = [];
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes('order number') || lines[i].toLowerCase().includes('sales record')) {
        headerIdx = i;
        headers = lines[i].split(',').map(h => h.replace(/"/g,'').trim().toLowerCase());
        break;
      }
    }
    if (headerIdx === -1) {
      showStatus('ebay-status', 'Could not find order data in CSV', 'error');
      return;
    }
    const sales = [];
    for (let i = headerIdx + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      const cols = line.split(',').map(c => c.replace(/"/g,'').trim());
      const row = {};
      headers.forEach((h, idx) => row[h] = cols[idx] || '');
      const salePrice = parseFloat(row['sale price'] || row['total price'] || row['item total price'] || 0);
      if (salePrice === 0) continue;
      sales.push({
        orderNumber: row['order number'] || row['sales record number'] || '',
        title: row['item title'] || row['title'] || '',
        salePrice,
        quantity: parseInt(row['quantity'] || 1),
        saleDate: row['sale date'] || row['paid on date'] || '',
        shippingCost: parseFloat(row['shipping and handling'] || row['postage and packaging'] || 0),
        platform: 'eBay'
      });
    }
    if (!sales.length) {
      showStatus('ebay-status', 'No sales found in CSV', 'error');
      return;
    }
    const totalRevenue = sales.reduce((s, r) => s + r.salePrice, 0);
    const avgPrice = totalRevenue / sales.length;
    const topSale = Math.max(...sales.map(s => s.salePrice));
    document.getElementById('ebay-summary-card').style.display = 'block';
    document.getElementById('ebay-total-revenue').textContent = '$' + totalRevenue.toFixed(2);
    document.getElementById('ebay-order-count').textContent = sales.length + ' orders';
    document.getElementById('ebay-avg-price').textContent = '$' + avgPrice.toFixed(2);
    document.getElementById('ebay-top-sale').textContent = '$' + topSale.toFixed(2);
    document.getElementById('ebay-bundles').textContent = sales.filter(s => s.quantity > 1 || s.title.toLowerCase().includes('bundle')).length;
    document.getElementById('ebay-avg-ship').textContent = '$' + (sales.reduce((s,r) => s + r.shippingCost, 0) / sales.length).toFixed(2);
    window._ebaySales = sales;
    showStatus('ebay-status', sales.length + ' orders loaded. Click Send to Watcher to analyze.', 'success');
  };
  reader.readAsText(file);
}

async function sendEbayToWatcher() {
  const sales = window._ebaySales;
  if (!sales || !sales.length) {
    showStatus('ebay-status', 'No sales data loaded', 'error');
    return;
  }
  showStatus('ebay-status', 'Sending to The Watcher...', 'loading');
  try {
    const res = await fetch('/.netlify/functions/agent3', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger: 'ebay_analysis', ebaySales: sales })
    });
    const data = await res.json();
    if (data.success) {
      showStatus('ebay-status', 'Sent! The Watcher is analyzing your sales history.', 'success');
    } else {
      showStatus('ebay-status', 'Error: ' + (data.error || 'Unknown'), 'error');
    }
  } catch(e) {
    showStatus('ebay-status', 'Error: ' + e.message, 'error');
  }
}
"""

old = '</script>\n\n<!-- Barcode S'
new = new_functions + '\n</script>\n\n<!-- Barcode S'

if old in content:
    content = content.replace(old, new, 1)
    print("Functions added successfully")
else:
    print("Not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)