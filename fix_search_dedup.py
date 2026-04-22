with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix quickBundleSearch to deduplicate by Series+Issue+Variant
old = """async function quickBundleSearch() {
  const q = document.getElementById('qb-search').value.trim();
  if (q.length < 2) { document.getElementById('qb-results').innerHTML = ''; return; }
  const formula = `OR(SEARCH(LOWER("${q}"),LOWER({Series})),SEARCH(LOWER("${q}"),LOWER({SKU})))`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 10 });
  const results = document.getElementById('qb-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d;padding:8px">No results</p>';
    return;
  }
  window._qbSearchResults = data.records;
  results.innerHTML = data.records.map((r, idx) =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +
    '<button onclick="addToQuickBundleByIdx(' + idx + ')" class="btn btn-secondary" style="font-size:11px;padding:4px 8px">Add</button>' +
    '</div>'
  ).join('');
}"""

new = """async function quickBundleSearch() {
  const q = document.getElementById('qb-search').value.trim();
  if (q.length < 2) { document.getElementById('qb-results').innerHTML = ''; return; }
  const formula = `AND(OR(SEARCH(LOWER("${q}"),LOWER({Series})),SEARCH(LOWER("${q}"),LOWER({SKU}))),{Status}!='Sold')`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 100 });
  const results = document.getElementById('qb-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d;padding:8px">No results</p>';
    return;
  }
  
  // Deduplicate by Series+Issue+Variant, keep count and one representative record
  const groups = {};
  for (const r of data.records) {
    const key = (r.fields['Series'] || '') + '|||' + (r.fields['Issue'] || '') + '|||' + (r.fields['Variant'] || '');
    if (!groups[key]) {
      groups[key] = { record: r, count: 0 };
    }
    groups[key].count++;
  }
  
  const deduped = Object.values(groups);
  window._qbSearchResults = deduped.map(g => g.record);
  
  results.innerHTML = deduped.map((g, idx) => {
    const r = g.record;
    const variantInfo = (r.fields['Variant'] ? ' CVR ' + r.fields['Variant'] : '') + 
                       (r.fields['Variant Description'] ? ' - ' + r.fields['Variant Description'] : '');
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<div>' +
    '<div style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + variantInfo + '</div>' +
    '<div style="font-size:11px;color:#6c757d">' + (r.fields['Publisher'] || '') + ' | ' + g.count + ' in stock | $' + (r.fields['Cover Price'] || '?') + ' cover</div>' +
    '</div>' +
    '<button onclick="addToQuickBundleByIdx(' + idx + ')" class="btn btn-secondary" style="font-size:11px;padding:4px 8px">Add</button>' +
    '</div>';
  }).join('');
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("QB search dedup fixed")
else:
    print("QB search not found")

# Also fix single listing search to deduplicate
old2 = """async function searchSingleListing() {
  const q = document.getElementById('listing-single-search').value.trim();
  if (q.length < 2) { document.getElementById('listing-single-results').innerHTML = ''; return; }
  const formula = `OR(SEARCH(LOWER("${q}"),LOWER({Series})),{SKU}="${q}")`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 5 });
  const results = document.getElementById('listing-single-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d">No results</p>';
    return;
  }
  window._singleSearchResults = data.records;
  results.innerHTML = data.records.map((r, idx) =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +
    '<button onclick="selectSingleListingByIdx(' + idx + ')" class="btn btn-primary" style="font-size:11px;padding:4px 8px">Select</button>' +
    '</div>'
  ).join('');
}"""

new2 = """async function searchSingleListing() {
  const q = document.getElementById('listing-single-search').value.trim();
  if (q.length < 2) { document.getElementById('listing-single-results').innerHTML = ''; return; }
  const formula = `AND(OR(SEARCH(LOWER("${q}"),LOWER({Series})),{SKU}="${q}"),{Status}!='Sold')`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 100 });
  const results = document.getElementById('listing-single-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d">No results</p>';
    return;
  }
  
  // Deduplicate by Series+Issue+Variant
  const groups = {};
  for (const r of data.records) {
    const key = (r.fields['Series'] || '') + '|||' + (r.fields['Issue'] || '') + '|||' + (r.fields['Variant'] || '');
    if (!groups[key]) groups[key] = { record: r, count: 0 };
    groups[key].count++;
  }
  
  const deduped = Object.values(groups);
  window._singleSearchResults = deduped.map(g => g.record);
  
  results.innerHTML = deduped.map((g, idx) => {
    const r = g.record;
    const variantInfo = (r.fields['Variant'] ? ' CVR ' + r.fields['Variant'] : '') +
                       (r.fields['Variant Description'] ? ' - ' + r.fields['Variant Description'] : '');
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<div>' +
    '<div style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + variantInfo + '</div>' +
    '<div style="font-size:11px;color:#6c757d">' + (r.fields['Publisher'] || '') + ' | ' + g.count + ' in stock</div>' +
    '</div>' +
    '<button onclick="selectSingleListingByIdx(' + idx + ')" class="btn btn-primary" style="font-size:11px;padding:4px 8px">Select</button>' +
    '</div>';
  }).join('');
}"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Single listing search dedup fixed")
else:
    print("Single listing search not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)