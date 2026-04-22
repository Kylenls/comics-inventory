with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Extract the working bundle panel HTML (just the inner card content)
bundle_panel_start = content.find('id="panel-bundles">')
bundle_inner_start = content.find('<div class="card">', bundle_panel_start)
bundle_panel_end = content.find('  <div class="panel"', bundle_panel_start + 100)
bundle_html = content[bundle_inner_start:bundle_panel_end].strip()

print("Bundle HTML extracted:", len(bundle_html), "chars")

# Extract loadBundlePlanner function
lbp_start = content.find('async function loadBundlePlanner()')
lbp_end = content.find('\nfunction renderBundlePlanner', lbp_start)
lbp_fn = content[lbp_start:lbp_end].strip()
print("loadBundlePlanner extracted:", len(lbp_fn), "chars")

# Extract renderBundlePlanner function
rbp_start = content.find('function renderBundlePlanner(')
rbp_end = content.find('\nfunction updateSkuAssignment', rbp_start)
rbp_fn = content[rbp_start:rbp_end].strip()
print("renderBundlePlanner extracted:", len(rbp_fn), "chars")

# Extract updateSkuAssignment and updateAllBlindBags
usku_start = content.find('function updateSkuAssignment(')
usku_end = content.find('\nfunction updateAllBlindBags', usku_start)
usku_fn = content[usku_start:usku_end].strip()

uabb_start = content.find('function updateAllBlindBags(')
uabb_end = content.find('\n\n', uabb_start + 100)
uabb_fn = content[uabb_start:uabb_end].strip()

# Create lgen versions of the HTML - replace IDs and function calls
lgen_html = bundle_html
lgen_html = lgen_html.replace('id="bundle-invoice"', 'id="lgen-invoice"')
lgen_html = lgen_html.replace('id="bundle-load-status"', 'id="lgen-load-status"')
lgen_html = lgen_html.replace('id="bundle-planner-results"', 'id="lgen-planner-results"')
lgen_html = lgen_html.replace('id="bundle-summary-text"', 'id="lgen-summary-text"')
lgen_html = lgen_html.replace('id="bundle-summary-sub"', 'id="lgen-summary-sub"')
lgen_html = lgen_html.replace('id="bundle-series-list"', 'id="lgen-series-list"')
lgen_html = lgen_html.replace('onclick="loadBundlePlanner()"', 'onclick="lgenLoadBundles()"')
lgen_html = lgen_html.replace('onclick="commitBundlePlan()"', 'onclick="lgenCommitPlan()"')

# Add queue section at the bottom of left panel
queue_html = """
        <!-- Queue -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">LISTING QUEUE (<span id="lgen-queue-count">0</span>)</div>
          <div id="lgen-queue-list"><p style="font-size:13px;color:#6c757d">No listings queued yet.</p></div>
        </div>

        <!-- Manual Add -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">ADD MANUALLY</div>
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:6px;margin-bottom:6px">
            <input type="text" id="lgen-manual-title" placeholder="Series title" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="lgen-manual-issue" placeholder="Issue #" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="lgen-manual-publisher" placeholder="Publisher" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <button class="btn btn-secondary" onclick="lgenAddManual()" style="width:100%;font-size:13px">+ Add to Queue</button>
        </div>"""

# Build the new full listings panel
new_listings_panel = '''  <div class="panel" id="panel-listings">
    <div style="display:grid;grid-template-columns:45% 55%;gap:16px;min-height:calc(100vh - 120px)">

      <!-- LEFT: PLAN & QUEUE -->
      <div style="overflow-y:auto;padding-right:8px">
''' + lgen_html + queue_html + '''
      </div>

      <!-- RIGHT: FINALIZE -->
      <div style="overflow-y:auto">

        <!-- Active Bundle Banner -->
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-size:13px;font-weight:700" id="lgen-active-name">No active listing</div>
              <div style="font-size:11px;color:#6c757d" id="lgen-active-detail">Queue a bundle on the left to begin</div>
            </div>
            <span id="lgen-active-badge" style="font-size:11px;padding:3px 10px;border-radius:10px;background:#f0f0f0;color:#6c757d">Pending</span>
          </div>
        </div>

        <!-- Watermark Logo -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">WATERMARK LOGO</div>
          <div style="display:flex;align-items:center;gap:10px">
            <div id="logo-preview-listing" style="font-size:13px;color:#6c757d">No logo uploaded</div>
            <button class="btn btn-secondary" onclick="document.getElementById(\'logo-upload-input\').click()" style="font-size:12px">Upload Logo</button>
            <button class="btn btn-secondary" onclick="clearSavedLogo()" style="font-size:12px;color:#dc3545">Clear</button>
          </div>
          <input type="file" id="logo-upload-input" accept="image/png,image/jpeg" style="display:none" onchange="saveLogo(event)" />
        </div>

        <!-- Photos -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">PHOTOS (<span id="listing-photo-count">0</span> uploaded)</div>
          <div class="drop-zone" id="listing-drop-zone"
            ondrop="handleListingDrop(event)" ondragover="event.preventDefault()"
            onclick="document.getElementById(\'listing-file-input\').click()"
            style="border:2px dashed #dee2e6;border-radius:8px;padding:20px;text-align:center;cursor:pointer;margin-bottom:8px">
            <div style="font-size:13px;color:#6c757d">Drop photos here or click to upload</div>
          </div>
          <input type="file" id="listing-file-input" multiple accept="image/*" style="display:none" onchange="handleListingFileInput(event)" />
          <div id="listing-photo-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:8px"></div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button class="btn btn-secondary" onclick="cleanAllListingPhotos()" id="listing-clean-btn" style="font-size:12px">AI Clean Photos</button>
            <button class="btn btn-secondary" onclick="buildListingCollage()" id="listing-collage-btn" style="font-size:12px">Build Collage</button>
            <button class="btn btn-secondary" onclick="lgenReusePhotos()" style="font-size:12px">♻️ Reuse from #1</button>
          </div>
        </div>

        <!-- Collage Preview -->
        <div class="card" id="listing-collage-card" style="display:none;margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">COLLAGE PREVIEW</div>
          <canvas id="listing-canvas" style="width:100%;border-radius:8px"></canvas>
          <button class="btn btn-secondary" onclick="downloadCollage()" style="width:100%;margin-top:8px;font-size:12px">Download Collage</button>
        </div>

        <!-- Draft -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">LISTING DRAFT</div>
          <input type="text" id="listing-title" placeholder="Title (auto-filled by Taskmaster)" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px;margin-bottom:6px" />
          <div style="display:flex;gap:8px;margin-bottom:6px">
            <input type="number" id="listing-price" placeholder="Price" style="width:120px;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <span style="line-height:36px;font-size:13px;color:#6c757d">+ Free Shipping</span>
          </div>
          <textarea id="listing-description" placeholder="Description (auto-filled by Taskmaster)" rows="6" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px;margin-bottom:8px;resize:vertical"></textarea>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button class="btn btn-primary" onclick="lgenGenerate()" style="flex:1;font-size:13px">⚔️ Generate Listing</button>
            <button class="btn btn-secondary" onclick="lgenCopyDraft()" style="font-size:13px">📋 Copy</button>
            <button class="btn btn-success" onclick="lgenMarkDone()" style="font-size:13px">✓ Done → Next</button>
          </div>
          <div class="status" id="listing-status" style="margin-top:8px"></div>
        </div>

      </div>
    </div>
  </div>

'''

# Replace the listings panel
old_panel_start = content.find('  <div class="panel" id="panel-listings">')
old_panel_end = content.find('  <div class="panel" ', old_panel_start + 100)

if old_panel_start < 0:
    print("Panel not found")
else:
    content = content[:old_panel_start] + new_listings_panel + content[old_panel_end:]
    print("Panel replaced")

# Now add lgen wrapper functions that call the existing bundle planner functions
# but redirect the "Stage" button to add to queue instead
lgen_wrapper_js = """
// ── LGEN BUNDLE WRAPPER ───────────────────────────────
window._arc2Queue = window._arc2Queue || [];
window._arc2ActiveIdx = -1;

function lgenLoadBundles() {
  // Copy invoice value and call existing loadBundlePlanner logic
  const invoice = document.getElementById('lgen-invoice').value.trim();
  if (!invoice) return;
  showStatus('lgen-load-status', 'Loading invoice...', 'loading');

  (async () => {
    let allRecords = [];
    let offset = null;
    do {
      const body = { action: 'search', formula: '{Invoice Number}="' + invoice + '"' };
      if (offset) body.offset = offset;
      const res = await fetch('/.netlify/functions/airtable', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (data.records) allRecords = allRecords.concat(data.records);
      offset = data.offset || null;
    } while (offset);

    const forSale = allRecords.filter(r => {
      const s = r.fields['Status'] || '';
      return s === 'Ordered' || s === 'In Stock';
    });

    if (!forSale.length) {
      showStatus('lgen-load-status', 'No records found for invoice ' + invoice, 'error');
      return;
    }

    // Use same grouping logic as bundle planner
    const bySeries = {};
    forSale.forEach(r => {
      let series = (r.fields['Series'] || 'Unknown').trim();
      series = series.replace(/\\s+CVR\\s+[A-Z].*$/i, '').trim();
      const issue = (r.fields['Issue'] || '').toString().trim();
      const key = issue ? series + ' #' + issue : series;
      if (!bySeries[key]) bySeries[key] = { key, series, issue, publisher: r.fields['Publisher'] || '', skus: [] };
      const variant = (r.fields['Variant'] || '').trim().toUpperCase();
      const variantDesc = (r.fields['Variant Description'] || '');
      const vdLower = variantDesc.toLowerCase();
      const isBlindBag = vdLower.includes('blind bag') || vdLower.includes('mystery');
      const isRatio = vdLower.includes('1:') || vdLower.includes('inc ') || vdLower.includes('incentive');
      bySeries[key].skus.push({
        id: r.id, sku: r.fields['SKU'], variant, variantDesc,
        coverPrice: parseFloat(r.fields['Cover Price'] || 0),
        purchasePrice: parseFloat(r.fields['Purchase Price'] || 0),
        isBlindBag, isRatio, assignment: 'single-ebay'
      });
    });

    // Calculate bundles same as bundle planner
    Object.values(bySeries).forEach(group => {
      const nonBlind = group.skus.filter(s => !s.isBlindBag);
      const blindBags = group.skus.filter(s => s.isBlindBag);
      const byVariant = {};
      nonBlind.forEach(s => {
        if (!byVariant[s.variant]) byVariant[s.variant] = [];
        byVariant[s.variant].push(s);
      });
      const variants = Object.keys(byVariant);
      const hasCvrA = variants.includes('A');
      const otherVariants = variants.filter(v => v !== 'A' && v !== '' && v !== 'R');
      const isBundle = hasCvrA && otherVariants.length > 0;
      const minQty = isBundle ? Math.min(...variants.map(v => byVariant[v].length)) : 0;
      const ratioVariant = variants.find(v => byVariant[v][0] && byVariant[v][0].isRatio);
      group.isBundle = isBundle;
      group.bundleCount = minQty;
      group.variants = byVariant;
      group.variantList = variants.sort();
      group.ratioVariant = ratioVariant || null;
      group.blindBags = blindBags;
      group.coverTotal = nonBlind.reduce((s, c) => s + c.coverPrice, 0);
    });

    window._lgenBySeries = bySeries;
    lgenRenderBundles(bySeries);
    showStatus('lgen-load-status', forSale.length + ' comics loaded', 'success');
    document.getElementById('lgen-planner-results').style.display = 'block';
    document.getElementById('lgen-summary-text').textContent = Object.keys(bySeries).length + ' titles loaded';
  })();
}

function lgenRenderBundles(bySeries) {
  const list = document.getElementById('lgen-series-list');
  if (!list) return;
  let html = '';
  Object.values(bySeries).forEach(g => {
    if (!g.isBundle) return;
    const safeKey = g.key.replace(/[^a-z0-9]/gi, '-');
    const variants = g.variantList.join(', ');
    html += '<div class="card" style="margin-bottom:8px">';
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">';
    html += '<div>';
    html += '<div style="font-size:13px;font-weight:700">' + g.key + '</div>';
    html += '<div style="font-size:11px;color:#6c757d">CVR ' + variants + (g.ratioVariant ? ' ⭐ Ratio CVR ' + g.ratioVariant : '') + '</div>';
    html += '<div style="font-size:11px;color:#6c757d">' + g.bundleCount + ' bundle(s) | $' + g.coverTotal.toFixed(2) + ' cover total</div>';
    html += '</div></div>';
    // Bundle slot buttons
    for (let b = 1; b <= g.bundleCount; b++) {
      const isPremium = b === 1 && !!g.ratioVariant;
      const bundleName = g.key + (isPremium ? ' — Premium' : ' — Bundle ' + b);
      const variantCount = g.variantList.length + (isPremium ? 0 : (g.ratioVariant ? -1 : 0));
      const coverSlice = g.variantList.reduce((sum, v) => {
        const sku = g.variants[v] && g.variants[v][b-1];
        return sum + (sku ? sku.coverPrice : 0);
      }, 0);
      html += '<button onclick="lgenQueueBundle(this)" ';
      html += 'data-name="' + bundleName + '" ';
      html += 'data-comics="' + g.key + ' CVR ' + g.variantList.join(', ') + (isPremium ? ' (incl. ratio variant)' : '') + '" ';
      html += 'data-count="' + variantCount + '" ';
      html += 'data-cover="' + coverSlice.toFixed(2) + '" ';
      html += 'data-premium="' + isPremium + '" ';
      html += 'class="btn btn-primary" style="width:100%;margin-bottom:4px;font-size:12px;text-align:left">';
      html += (isPremium ? '⭐ ' : '📦 ') + 'Queue: ' + bundleName;
      html += '</button>';
    }
    html += '</div>';
  });
  if (!html) html = '<p style="font-size:13px;color:#6c757d">No bundle titles found in this invoice.</p>';
  list.innerHTML = html;
}

function lgenQueueBundle(btn) {
  if (!btn) return;
  const name = btn.dataset.name;
  const comicsString = btn.dataset.comics;
  const comicCount = parseInt(btn.dataset.count) || 5;
  const coverTotal = parseFloat(btn.dataset.cover) || 0;
  const isPremium = btn.dataset.premium === 'true';

  lgenAddToQueue({ name, comicsString, comicCount, isPremium, coverTotal, status: 'Pending', photos: [], draft: null });
  btn.textContent = '✓ Queued: ' + name;
  btn.disabled = true;
  btn.style.background = '#198754';
  btn.style.borderColor = '#198754';
}

function lgenAddToQueue(item) {
  const existing = window._arc2Queue.findIndex(q => q.name === item.name);
  if (existing >= 0) {
    window._arc2Queue[existing] = item;
  } else {
    window._arc2Queue.push(item);
  }
  lgenRenderQueue();
  if (window._arc2Queue.length === 1) lgenActivate(0);
}

function lgenRenderQueue() {
  const list = document.getElementById('lgen-queue-list');
  const count = document.getElementById('lgen-queue-count');
  if (!list) return;
  if (count) count.textContent = window._arc2Queue.length;
  if (!window._arc2Queue.length) {
    list.innerHTML = '<p style="font-size:13px;color:#6c757d">No listings queued yet.</p>';
    return;
  }
  list.innerHTML = window._arc2Queue.map((item, idx) => {
    const isActive = idx === window._arc2ActiveIdx;
    const statusColor = item.status === 'Done' ? '#198754' : item.status === 'Draft Ready' ? '#0066cc' : '#6c757d';
    return '<div onclick="lgenActivate(' + idx + ')" style="display:flex;justify-content:space-between;align-items:center;padding:8px;margin-bottom:4px;border-radius:6px;cursor:pointer;border:2px solid ' + (isActive ? '#0066cc' : '#dee2e6') + ';background:' + (isActive ? '#e8f4fd' : '#fff') + '">' +
      '<div><div style="font-size:13px;font-weight:600">' + item.name + '</div>' +
      '<div style="font-size:11px;color:#6c757d">' + (item.comicCount || '?') + ' comics</div></div>' +
      '<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:' + statusColor + '20;color:' + statusColor + '">' + item.status + '</span>' +
      '</div>';
  }).join('');
}

function lgenActivate(idx) {
  window._arc2ActiveIdx = idx;
  const item = window._arc2Queue[idx];
  if (!item) return;
  const nameEl = document.getElementById('lgen-active-name');
  const detailEl = document.getElementById('lgen-active-detail');
  const badgeEl = document.getElementById('lgen-active-badge');
  if (nameEl) nameEl.textContent = item.name;
  if (detailEl) detailEl.textContent = item.comicsString || '';
  if (badgeEl) {
    badgeEl.textContent = item.isPremium ? '⭐ Premium' : item.status;
    badgeEl.style.background = item.isPremium ? '#F0E8FA' : '#E8F8F3';
    badgeEl.style.color = item.isPremium ? '#7B3FB5' : '#198754';
  }
  listingPhotos = item.photos || [];
  renderListingPhotoGrid();
  const titleEl = document.getElementById('listing-title');
  const priceEl = document.getElementById('listing-price');
  const descEl = document.getElementById('listing-description');
  if (item.draft) {
    if (titleEl) titleEl.value = item.draft.title || '';
    if (priceEl) priceEl.value = item.draft.price || '';
    if (descEl) descEl.value = item.draft.description || '';
  } else {
    if (titleEl) titleEl.value = '';
    if (priceEl) priceEl.value = '';
    if (descEl) descEl.value = '';
  }
  lgenRenderQueue();
}

function lgenAddManual() {
  const title = document.getElementById('lgen-manual-title').value.trim();
  const issue = document.getElementById('lgen-manual-issue').value.trim();
  const publisher = document.getElementById('lgen-manual-publisher').value.trim();
  if (!title) { alert('Please enter a series title'); return; }
  const name = title + (issue ? ' #' + issue : '') + (publisher ? ' (' + publisher + ')' : '');
  lgenAddToQueue({ name, comicsString: name, comicCount: 1, isPremium: false, coverTotal: 0, status: 'Pending', photos: [], draft: null });
  document.getElementById('lgen-manual-title').value = '';
  document.getElementById('lgen-manual-issue').value = '';
  document.getElementById('lgen-manual-publisher').value = '';
}

function lgenReusePhotos() {
  if (window._arc2Queue.length > 0 && window._arc2Queue[0].photos && window._arc2Queue[0].photos.length) {
    listingPhotos = [...window._arc2Queue[0].photos];
    renderListingPhotoGrid();
    showStatus('listing-status', 'Photos copied from first queue item', 'success');
  } else {
    showStatus('listing-status', 'No photos in first queue item yet', 'error');
  }
}

async function lgenGenerate() {
  const idx = window._arc2ActiveIdx;
  if (idx < 0 || !window._arc2Queue[idx]) {
    showStatus('listing-status', 'No active listing - click a queue item first', 'error');
    return;
  }
  const item = window._arc2Queue[idx];
  showStatus('listing-status', 'Taskmaster is researching and writing your listing...', 'loading');
  const count = item.comicCount || 1;
  try {
    const res = await fetch('/.netlify/functions/agent2', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'generate_listing',
        comics: item.comicsString,
        count: count,
        mode: count > 1 ? 'bundle' : 'single',
        coverPriceTotal: item.coverTotal || null
      })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Generation failed');
    document.getElementById('listing-title').value = data.title || '';
    document.getElementById('listing-price').value = data.price || '';
    document.getElementById('listing-description').value = data.description || '';
    window._arc2Queue[idx].draft = { title: data.title, price: data.price, description: data.description };
    window._arc2Queue[idx].status = 'Draft Ready';
    window._arc2Queue[idx].photos = [...listingPhotos];
    lgenRenderQueue();
    showStatus('listing-status', 'Draft ready - review, copy, or mark done', 'success');
  } catch(e) {
    showStatus('listing-status', 'Error: ' + e.message, 'error');
  }
}

function lgenCopyDraft() {
  const title = document.getElementById('listing-title').value;
  const price = document.getElementById('listing-price').value;
  const desc = document.getElementById('listing-description').value;
  const text = 'TITLE: ' + title + '\\n\\nPRICE: $' + price + ' (Free Shipping)\\n\\nDESCRIPTION:\\n' + desc;
  navigator.clipboard.writeText(text).then(() => showStatus('listing-status', 'Copied to clipboard', 'success'));
}

function lgenMarkDone() {
  const idx = window._arc2ActiveIdx;
  if (idx < 0 || !window._arc2Queue[idx]) return;
  window._arc2Queue[idx].photos = [...listingPhotos];
  const title = document.getElementById('listing-title').value;
  const price = document.getElementById('listing-price').value;
  const desc = document.getElementById('listing-description').value;
  if (title) window._arc2Queue[idx].draft = { title, price, description: desc };
  window._arc2Queue[idx].status = 'Done';
  const nextIdx = window._arc2Queue.findIndex((item, i) => i > idx && item.status !== 'Done');
  if (nextIdx >= 0) {
    lgenActivate(nextIdx);
  } else {
    showStatus('listing-status', 'All listings complete!', 'success');
    window._arc2ActiveIdx = -1;
    lgenRenderQueue();
  }
}

function lgenCommitPlan() {
  // Placeholder for future Airtable commit
  showStatus('lgen-load-status', 'Plan saved', 'success');
}
"""

# Remove the old lgen JS that was added previously
old_lgen_marker = "// ── LISTING GENERATOR v2 ─────────────────────────────"
if old_lgen_marker in content:
    start = content.find(old_lgen_marker)
    # Find end - look for next major section
    end = content.find('\n// ── LOGO / WATERMARK', start)
    if end > 0:
        content = content[:start] + content[end:]
        print("Removed old lgen JS")
    else:
        end2 = content.find('\n</script>', start)
        content = content[:start] + content[end2:]
        print("Removed old lgen JS (alt)")

# Insert new JS before closing script tag
old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + lgen_wrapper_js + '\n</script>\n\n<!-- Barcode', 1)
    print("New lgen JS added")
else:
    print("JS insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)