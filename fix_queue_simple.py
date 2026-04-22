with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Step 1: Initialize queue at top of script so it never resets
old_top = 'const FUNCTION_URL = '
new_top = '''// ── PERSISTENT QUEUE ─────────────────────────────────
if (!window._arc2Queue) window._arc2Queue = [];
if (window._arc2ActiveIdx === undefined) window._arc2ActiveIdx = -1;

const FUNCTION_URL = '''

if old_top in content:
    content = content.replace(old_top, new_top, 1)
    print("Step 1: Queue initialized at top of script")
else:
    print("Step 1: FAILED - FUNCTION_URL not found")

# Step 2: Add "→ Queue" button to each bundle card in renderBundlePlanner
# Find the draftBtn section and add a queue button before it
old_draft_btn = "'<button onclick=\"agent2BuildDraftByKey(\\'' + safeKey + '\\')\" style=\"width:100%;margin-top:8px;padding:8px;background:#0066cc"
new_draft_btn = """'<button onclick=\"lgenQueueFromBundle(\\'' + safeKey + '\\')\" style=\"width:100%;margin-top:4px;padding:8px;background:#198754;border:none;color:white;border-radius:8px;font-size:12px;font-weight:600;font-family:inherit;cursor:pointer\">📋 Add to Listing Queue</button>' +
        '<button onclick=\"agent2BuildDraftByKey(\\'' + safeKey + '\\')\" style=\"width:100%;margin-top:8px;padding:8px;background:#0066cc"""

if old_draft_btn in content:
    content = content.replace(old_draft_btn, new_draft_btn, 1)
    print("Step 2: Queue button added to bundle cards")
else:
    print("Step 2: FAILED - draft button not found")
    idx = content.find('agent2BuildDraftByKey')
    print("  agent2BuildDraftByKey at:", idx)

# Step 3: Add lgenQueueFromBundle function and listings tab queue display
queue_js = """
// ── LISTING QUEUE FROM BUNDLES ────────────────────────
function lgenQueueFromBundle(safeKey) {
  const d = (window._bundleData || {})[safeKey];
  if (!d) { alert('Bundle data not found - reload the invoice first'); return; }

  const ratios = ['10','25','50','100'].filter(r => {
    const el = document.getElementById('ratio-' + safeKey + '-' + r);
    return el && el.checked;
  }).map(r => '1:' + r);

  const bundlePlanGroup = window.bundlePlan && window.bundlePlan[d.bundleKey];
  const byBundle = {};
  if (bundlePlanGroup) {
    bundlePlanGroup.skus.forEach(function(s) {
      if (s.assignment && s.assignment.startsWith('B')) {
        if (!byBundle[s.assignment]) byBundle[s.assignment] = [];
        byBundle[s.assignment].push(s);
      }
    });
  }

  const bundleNums = Object.keys(byBundle).sort();
  if (!bundleNums.length) {
    alert('No comics assigned to bundles yet. Use the dropdowns to assign to Bundle 1, 2, 3 etc first.');
    return;
  }

  // Remove existing entries for this title
  window._arc2Queue = window._arc2Queue.filter(function(b) { return b.seriesKey !== d.bundleKey; });

  bundleNums.forEach(function(bNum) {
    const skus = byBundle[bNum];
    const isPremium = bNum === 'B1' && ratios.length > 0;
    const bundleNum = parseInt(bNum.replace('B', ''));
    const ratioStr = isPremium ? ' (Ratio: ' + ratios.join(', ') + ')' : '';
    const coverTotal = skus.reduce(function(sum, s) { return sum + (s.coverPrice || 0); }, 0);
    const variantList = skus.map(function(s) { return 'CVR ' + s.variant; }).join(', ');

    window._arc2Queue.push({
      seriesKey: d.bundleKey,
      name: d.series + ' #' + d.issue + (isPremium ? ' - Premium Bundle' : ' - Bundle ' + bundleNum),
      comicsString: d.series + ' #' + d.issue + ' ' + variantList + ratioStr,
      comicCount: skus.length,
      isPremium: isPremium,
      coverTotal: coverTotal,
      status: 'Pending',
      photos: [],
      draft: null
    });
  });

  lgenUpdateQueueDisplay();

  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ ' + bundleNums.length + ' bundle(s) added to listing queue</span>';
  }
}

function lgenUpdateQueueDisplay() {
  // Update queue count badge if it exists
  const badge = document.getElementById('lgen-queue-badge');
  if (badge) badge.textContent = window._arc2Queue.length;
}

// ── LISTINGS TAB QUEUE FUNCTIONS ─────────────────────
function lgenRenderQueue() {
  const list = document.getElementById('lgen-queue-list');
  const count = document.getElementById('lgen-queue-count');
  if (!list) return;
  if (count) count.textContent = window._arc2Queue.length;
  if (!window._arc2Queue.length) {
    list.innerHTML = '<p style="font-size:13px;color:#6c757d">No listings queued. Use the Bundles tab to assign and queue bundles.</p>';
    return;
  }
  list.innerHTML = window._arc2Queue.map(function(item, idx) {
    const isActive = idx === window._arc2ActiveIdx;
    const statusColor = item.status === 'Done' ? '#198754' : item.status === 'Draft Ready' ? '#0066cc' : '#6c757d';
    return '<div onclick="lgenActivate(' + idx + ')" style="display:flex;justify-content:space-between;align-items:center;padding:8px;margin-bottom:4px;border-radius:6px;cursor:pointer;border:2px solid ' + (isActive ? '#0066cc' : '#dee2e6') + ';background:' + (isActive ? '#e8f4fd' : '#fff') + '">' +
      '<div><div style="font-size:13px;font-weight:600">' + item.name + '</div>' +
      '<div style="font-size:11px;color:#6c757d">' + (item.comicCount || '?') + ' comics | $' + (item.coverTotal || 0).toFixed(2) + ' cover</div></div>' +
      '<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:' + statusColor + '20;color:' + statusColor + '">' + item.status + '</span>' +
      '</div>';
  }).join('');
}

function lgenActivate(idx) {
  window._arc2ActiveIdx = idx;
  const item = window._arc2Queue[idx];
  if (!item) return;
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
  // Update active banner
  const nameEl = document.getElementById('lgen-active-name');
  const detailEl = document.getElementById('lgen-active-detail');
  if (nameEl) nameEl.textContent = item.name;
  if (detailEl) detailEl.textContent = item.comicsString || '';
  lgenRenderQueue();
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
    showStatus('listing-status', 'Draft ready - review and copy or mark done', 'success');
  } catch(e) {
    showStatus('listing-status', 'Error: ' + e.message, 'error');
  }
}

function lgenCopyDraft() {
  const title = document.getElementById('listing-title').value;
  const price = document.getElementById('listing-price').value;
  const desc = document.getElementById('listing-description').value;
  const text = 'TITLE: ' + title + '\\n\\nPRICE: $' + price + ' (Free Shipping)\\n\\nDESCRIPTION:\\n' + desc;
  navigator.clipboard.writeText(text).then(function() { showStatus('listing-status', 'Copied to clipboard', 'success'); });
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
  const nextIdx = window._arc2Queue.findIndex(function(item, i) { return i > idx && item.status !== 'Done'; });
  if (nextIdx >= 0) {
    lgenActivate(nextIdx);
  } else {
    showStatus('listing-status', 'All listings complete!', 'success');
    window._arc2ActiveIdx = -1;
    lgenRenderQueue();
  }
}

function lgenReusePhotos() {
  if (window._arc2Queue.length > 0 && window._arc2Queue[0].photos && window._arc2Queue[0].photos.length) {
    listingPhotos = [...window._arc2Queue[0].photos];
    renderListingPhotoGrid();
    showStatus('listing-status', 'Photos copied from Bundle 1', 'success');
  } else {
    showStatus('listing-status', 'No photos in Bundle 1 yet', 'error');
  }
}
"""

old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + queue_js + '\n</script>\n\n<!-- Barcode', 1)
    print("Step 3: Queue JS added")
else:
    print("Step 3: FAILED - JS insertion point not found")

# Step 4: Replace the listings panel with the new two-panel layout
old_listings_start = '  <div class="panel" id="panel-listings">'
old_listings_end = '  <div class="panel" id="panel-agents">'

ls = content.find(old_listings_start)
le = content.find(old_listings_end)

new_listings = '''  <div class="panel" id="panel-listings">
    <div style="display:grid;grid-template-columns:45% 55%;gap:16px;min-height:calc(100vh - 120px)">

      <!-- LEFT: QUEUE -->
      <div style="overflow-y:auto;padding-right:8px">
        <div class="card">
          <div class="defaults-title" style="font-size:13px;font-weight:600;margin-bottom:4px">📋 Listing Queue</div>
          <p style="font-size:12px;color:#6c757d;margin-bottom:12px">Assign bundles in the <strong>Bundles</strong> tab then click "Add to Listing Queue". They appear here.</p>
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">QUEUE (<span id="lgen-queue-count">0</span> listings)</div>
          <div id="lgen-queue-list"><p style="font-size:13px;color:#6c757d">No listings queued. Go to Bundles tab, assign comics to bundles, then click "Add to Listing Queue".</p></div>
        </div>

        <!-- Active Banner -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:6px">ACTIVE LISTING</div>
          <div style="font-size:13px;font-weight:700" id="lgen-active-name">None selected</div>
          <div style="font-size:11px;color:#6c757d;margin-top:2px" id="lgen-active-detail">Click a queue item to activate it</div>
        </div>

        <!-- Manual Add -->
        <div class="card" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">ADD MANUALLY</div>
          <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;margin-bottom:6px">
            <input type="text" id="lgen-manual-title" placeholder="Series title" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="lgen-manual-issue" placeholder="Issue #" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <button class="btn btn-secondary" onclick="lgenAddManual()" style="width:100%;font-size:13px">+ Add to Queue</button>
        </div>
      </div>

      <!-- RIGHT: FINALIZE -->
      <div style="overflow-y:auto">

        <!-- Watermark Logo -->
        <div class="card">
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

if ls > 0 and le > 0:
    content = content[:ls] + new_listings + content[le:]
    print("Step 4: Listings panel replaced")
else:
    print("Step 4: FAILED - panel not found, ls:", ls, "le:", le)

# Also add lgenAddManual function
old_close = '\n</script>\n\n<!-- Barcode'
manual_fn = """
function lgenAddManual() {
  const title = document.getElementById('lgen-manual-title').value.trim();
  const issue = document.getElementById('lgen-manual-issue').value.trim();
  if (!title) { alert('Please enter a series title'); return; }
  const name = title + (issue ? ' #' + issue : '');
  window._arc2Queue.push({ name, comicsString: name, comicCount: 1, isPremium: false, coverTotal: 0, status: 'Pending', photos: [], draft: null });
  lgenRenderQueue();
  if (window._arc2Queue.length === 1) lgenActivate(0);
  document.getElementById('lgen-manual-title').value = '';
  document.getElementById('lgen-manual-issue').value = '';
}
"""
# Already added in step 3, skip if already there
if 'function lgenAddManual' not in content:
    if old_close in content:
        content = content.replace(old_close, '\n' + manual_fn + '\n</script>\n\n<!-- Barcode', 1)
        print("lgenAddManual added")

# Also make sure bundlePlan is on window when set
content = content.replace(
    'bundlePlan = bySeries;\n    renderBundlePlanner',
    'bundlePlan = bySeries;\n    window.bundlePlan = bySeries;\n    renderBundlePlanner',
    1
)
print("Step 5: bundlePlan exposed to window")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)