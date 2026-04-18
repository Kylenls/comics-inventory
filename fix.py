with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

start = content.find('async function parseLunarCSV(csvText) {')
end = content.find('\nasync function parseLunarPDF', start)
old_func = content[start:end]

new_func = """async function parseLunarCSV(csvText) {
  showStatus('inv-status', 'Parsing Lunar CSV...', 'loading');

  const pubMap = {
    'DC': 'DC', 'IM': 'Image', 'MA': 'Mad Cave', 'TN': 'Titan',
    'DE': 'Dynamite', 'EX': 'Vault', 'ON': 'Oni Press', 'MP': 'Mad Cave',
    'MR': 'Marvel', 'DH': 'Dark Horse', 'ID': 'IDW', 'BM': 'BOOM! Studios',
    'AF': 'Aftershock', 'SC': 'Scout', 'VL': 'Valiant', 'AW': 'AWA',
    'ZE': 'Zenescope', 'DY': 'Dynamite', 'HC': 'Humanoids'
  };

  function parseCSVLine(line) {
    const result = [];
    let current = '', inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i+1] === '"') { current += '"'; i++; }
        else inQuotes = !inQuotes;
      } else if (ch === ',' && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += ch;
      }
    }
    result.push(current.trim());
    return result;
  }

  const lines = csvText.split('\\n');

  for (const line of lines.slice(0, 15)) {
    const dateMatch = line.match(/Invoice Date:\\s*(\\d+\\/\\d+\\/\\d+)/i);
    if (dateMatch) {
      const parts = dateMatch[1].split('/');
      if (parts.length === 3) {
        const invoiceDate = parts[2] + '-' + parts[0].padStart(2,'0') + '-' + parts[1].padStart(2,'0');
        document.getElementById('inv-date').value = invoiceDate;
      }
      break;
    }
  }

  let headerIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (/^("?)Code\\1,/i.test(lines[i])) {
      headerIdx = i;
      break;
    }
  }

  if (headerIdx === -1) {
    showStatus('inv-status', 'Could not find data section in CSV', 'error');
    return;
  }

  const headers = parseCSVLine(lines[headerIdx]).map(h => h.toLowerCase());
  const items = [];

  for (let i = headerIdx + 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const cols = parseCSVLine(line);
    if (cols.length < 3) continue;
    const row = {};
    headers.forEach((h, idx) => row[h] = (cols[idx] || '').trim());
    if (!row['code'] || !row['code'].match(/[A-Z0-9]/i)) continue;
    const qty = parseInt(row['qty']) || 0;
    if (qty === 0) continue;
    const title = row['title'] || '';
    if (!title) continue;
    const retail = parseFloat(row['retail']) || 0;
    const issueMatch = title.match(/#(\\d+)/);
    let series = issueMatch ? title.substring(0, issueMatch.index).trim().replace(/:$/, '').trim() : title;
    series = series.replace(/\\s*\\(OF \\d+\\)\\s*/gi, ' ').replace(/\\s*\\(2026\\)\\s*/gi, ' ').trim();
    const issue = issueMatch ? issueMatch[1] : '';
    const cvrMatch = title.match(/CVR\\s+([A-Z])(?:\\s|$)/);
    const variant = cvrMatch ? cvrMatch[1] : '';
    let variantDesc = '';
    if (cvrMatch) {
      variantDesc = title.substring(title.indexOf(cvrMatch[0]) + cvrMatch[0].length).trim();
      variantDesc = variantDesc.replace(/\\s*\\(MR\\)\\s*$/, '').replace(/\\s*VAR\\s*$/, '').trim();
    }
    const code = (row['code'] || '').toUpperCase();
    const pubCode = code.substring(4, 6);
    const publisher = pubMap[pubCode] || '';
    let finalQty = qty;
    if (title.toUpperCase().includes('BUNDLE OF 25')) finalQty = qty * 25;
    else if (title.toUpperCase().includes('BUNDLE OF 50')) finalQty = qty * 50;
    if (retail === 0 && !title.toUpperCase().includes('BUNDLE OF')) continue;
    items.push({
      lunarCode: row['code'], series, issue, variant,
      variantDescription: variantDesc, qty: finalQty,
      coverPrice: retail,
      purchasePrice: parseFloat(row['discounted price']) || 0,
      publisher, upc: row['upc'] || ''
    });
  }

  if (!items.length) {
    showStatus('inv-status', 'No items found in CSV', 'error');
    return;
  }

  const totalSkus = items.reduce((s, i) => s + i.qty, 0);
  parsedInvoiceItems = items;
  showInvoicePreview(items, totalSkus);
}

"""

content = content.replace(old_func, new_func)

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)

print("Fix applied! Lines now: " + str(content.count('\\n')))