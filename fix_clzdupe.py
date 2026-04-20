with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the import loop and add session tracking
old = """  let success = 0, failed = 0;

  for (let i = 0; i < parsedRows.length; i++) {
    const r = parsedRows[i];
    const series = r['series'] || '';
    const issue = r['issue'] || '';
    if (!series) { failed++; continue; }"""

new = """  let success = 0, failed = 0;
  const sessionCounts = {}; // track how many we've created this session per key

  for (let i = 0; i < parsedRows.length; i++) {
    const r = parsedRows[i];
    const series = r['series'] || '';
    const issue = r['issue'] || '';
    if (!series) { failed++; continue; }
    
    const dupKey = (series + '|||' + issue + '|||' + (r['variant'] || '')).toLowerCase().trim();
    sessionCounts[dupKey] = (sessionCounts[dupKey] || 0);"""

if old in content:
    content = content.replace(old, new, 1)
    print("Step 1 done - added session tracking")
else:
    print("Step 1 FAILED - not found")

# Now fix the upsert call to pass session count
old2 = """    try {
      const data = await callAirtable({ action: 'upsert', fields });
      if (data.id) {
        const wasSkipped = data._action === 'skipped';
        if (wasSkipped) { skipped = (skipped||0) + 1; nextSkuNum--; } // don't burn a SKU on skip
        else success++;"""

new2 = """    try {
      const data = await callAirtable({ action: 'upsert', fields, sessionCount: sessionCounts[dupKey] });
      if (data.id) {
        const wasSkipped = data._action === 'skipped';
        if (wasSkipped) { skipped = (skipped||0) + 1; nextSkuNum--; } // don't burn a SKU on skip
        else { success++; sessionCounts[dupKey]++; }"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Step 2 done - pass session count to upsert")
else:
    print("Step 2 FAILED - not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)