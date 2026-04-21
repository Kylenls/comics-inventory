with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# 1. Add eBay Listing Generator tab button after Agents
old_tabs = "      <button class=\"tab\" onclick=\"switchTab('agents')\">Agents</button>"
new_tabs = "      <button class=\"tab\" onclick=\"switchTab('agents')\">Agents</button>\n      <button class=\"tab\" onclick=\"switchTab('listings')\">eBay Listings</button>"
if old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("Tab button added")
else:
    print("Tab button NOT found")

# 2. Add listings to tabs array
old_arr = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','agents'];"
new_arr = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','agents','listings'];"
if old_arr in content:
    content = content.replace(old_arr, new_arr, 1)
    print("Tabs array updated")
else:
    print("Tabs array NOT found")

# 3. Add Quick Bundle builder to Bundles panel
quick_bundle_html = """
    <div class="card" style="margin-top:1rem">
      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:4px">🔗 Quick Bundle Builder</div>
      <p style="font-size:13px;color:#666;margin-bottom:12px">Search inventory and add any comics to a custom bundle for listing.</p>
      <div class="field">
        <label>Search Comics</label>
        <input type="text" id="qb-search" placeholder="Series, SKU, or keyword..." oninput="quickBundleSearch()" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
      </div>
      <div id="qb-results" style="max-height:200px;overflow-y:auto;margin-bottom:12px"></div>
      <div class="defaults-title" style="font-size:11px;margin-bottom:8px">BUNDLE QUEUE (<span id="qb-count">0</span> comics)</div>
      <div id="qb-queue" style="max-height:200px;overflow-y:auto;margin-bottom:12px"></div>
      <div class="row">
        <div class="field">
          <label>Bundle Name</label>
          <input type="text" id="qb-name" placeholder="e.g. Indie Horror Lot" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px;width:100%" />
        </div>
      </div>
      <button class="btn btn-primary" onclick="sendBundleToListings()" style="width:100%">Send to eBay Listing Generator</button>
      <div class="status" id="qb-status"></div>
    </div>
"""

old_bundles_end = '  <div class="panel" id="panel-update">'
if old_bundles_end in content:
    content = content.replace(old_bundles_end, quick_bundle_html + '\n  <div class="panel" id="panel-update">', 1)
    print("Quick bundle added to Bundles tab")
else:
    print("Bundles panel end NOT found")

# 4. Add eBay Listing Generator panel before closing div
listings_panel = """
  <div class="panel" id="panel-listings">
    <div class="card">
      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">🏷️ eBay Listing Generator</div>
      <p style="font-size:13px;color:#6c757d;margin-bottom:1rem">Upload photos, generate AI-cleaned covers, build collage, and let Taskmaster write your listing.</p>

      <div id="listing-source-card">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">LISTING SOURCE</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:1rem">
          <button class="btn btn-secondary" onclick="setListingMode('bundle')" id="mode-bundle">From Bundle</button>
          <button class="btn btn-secondary" onclick="setListingMode('single')" id="mode-single">Single Issue</button>
          <button class="btn btn-secondary" onclick="setListingMode('custom')" id="mode-custom">Custom</button>
        </div>

        <div id="listing-bundle-picker" style="display:none">
          <div class="field">
            <label>Bundle Name</label>
            <input type="text" id="listing-bundle-name" placeholder="Bundle will appear here from Bundles tab" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" readonly />
          </div>
          <div id="listing-bundle-comics" style="font-size:13px;color:#6c757d;margin-top:8px"></div>
        </div>

        <div id="listing-single-picker" style="display:none">
          <div class="field">
            <label>Search Comic</label>
            <input type="text" id="listing-single-search" placeholder="SKU or series..." oninput="searchSingleListing()" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <div id="listing-single-results"></div>
        </div>
      </div>

      <div style="margin-top:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">PHOTOS (<span id="listing-photo-count">0</span> uploaded)</div>
        <div class="drop-zone" id="listing-drop-zone"
          onclick="document.getElementById('listing-photos').click()"
          ondragover="event.preventDefault()"
          ondrop="handleListingDrop(event)"
          style="margin-bottom:1rem">
          <div style="font-size:32px;margin-bottom:8px">📸</div>
          <strong>Drop photos here or tap to select</strong>
          <p style="color:#6c757d;font-size:13px">One photo per comic — AI will clean and crop each one</p>
          <input type="file" id="listing-photos" accept="image/*" multiple style="display:none" onchange="handleListingPhotos(event)" />
        </div>
        <div id="listing-photo-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:1rem"></div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem">
        <button class="btn btn-secondary" onclick="buildListingCollage()" id="listing-collage-btn">Build Collage</button>
        <button class="btn btn-primary" onclick="generateListing()" id="listing-generate-btn">Generate Listing</button>
      </div>

      <div id="listing-collage-output" style="display:none;margin-bottom:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">HERO COLLAGE</div>
        <canvas id="listing-canvas" style="width:100%;border-radius:8px;border:1px solid #dee2e6"></canvas>
      </div>

      <div id="listing-draft" style="display:none">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">LISTING DRAFT</div>
        <div class="field">
          <label>Title</label>
          <input type="text" id="listing-title" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
        </div>
        <div class="field" style="margin-top:8px">
          <label>Price</label>
          <input type="number" id="listing-price" step="0.01" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
        </div>
        <div class="field" style="margin-top:8px">
          <label>Description</label>
          <textarea id="listing-description" rows="6" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px;resize:vertical"></textarea>
        </div>
        <button class="btn btn-primary" onclick="publishListing()" style="width:100%;margin-top:12px">Publish to eBay</button>
      </div>

      <div class="status" id="listing-status"></div>
    </div>
  </div>
"""

old_agents = '  <div class="panel" id="panel-agents">'
if old_agents in content:
    content = content.replace(old_agents, listings_panel + '\n  <div class="panel" id="panel-agents">', 1)
    print("Listings panel added")
else:
    print("Agents panel NOT found")

# 5. Add JS for listings tab
listings_js = """
// ── eBay LISTING GENERATOR ──────────────────────────
let listingMode = 'bundle';
let listingPhotos = [];
let listingBundle = null;
let listingSingleComic = null;

function setListingMode(mode) {
  listingMode = mode;
  document.getElementById('listing-bundle-picker').style.display = mode === 'bundle' ? 'block' : 'none';
  document.getElementById('listing-single-picker').style.display = mode === 'single' ? 'block' : 'none';
  ['bundle','single','custom'].forEach(m => {
    document.getElementById('mode-' + m).className = m === mode ? 'btn btn-primary' : 'btn btn-secondary';
  });
}

function handleListingDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'));
  addListingPhotos(files);
}

function handleListingPhotos(event) {
  addListingPhotos(Array.from(event.target.files));
  event.target.value = '';
}

function addListingPhotos(files) {
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        listingPhotos.push({ file, img, src: e.target.result, cleaned: null });
        renderListingPhotoGrid();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function renderListingPhotoGrid() {
  document.getElementById('listing-photo-count').textContent = listingPhotos.length;
  const grid = document.getElementById('listing-photo-grid');
  grid.innerHTML = listingPhotos.map((p, i) =>
    '<div style="position:relative">' +
    '<img src="' + (p.cleaned || p.src) + '" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px">' +
    (p.cleaned ? '<div style="position:absolute;top:2px;left:2px;background:#198754;color:white;border-radius:4px;font-size:9px;padding:1px 4px">AI</div>' : '') +
    '<button onclick="removeListingPhoto(' + i + ')" style="position:absolute;top:2px;right:2px;background:rgba(0,0,0,0.6);color:white;border:none;border-radius:50%;width:20px;height:20px;font-size:11px;cursor:pointer">x</button>' +
    '</div>'
  ).join('');
}

function removeListingPhoto(idx) {
  listingPhotos.splice(idx, 1);
  renderListingPhotoGrid();
}

function getGridDimensions(count) {
  if (count <= 2) return { cols: count, rows: 1 };
  if (count <= 4) return { cols: 2, rows: 2 };
  if (count <= 6) return { cols: 3, rows: 2 };
  if (count <= 9) return { cols: 3, rows: 3 };
  if (count <= 12) return { cols: 4, rows: 3 };
  if (count <= 16) return { cols: 4, rows: 4 };
  if (count <= 20) return { cols: 5, rows: 4 };
  return { cols: 6, rows: Math.ceil(count / 6) };
}

async function buildListingCollage() {
  if (!listingPhotos.length) {
    showStatus('listing-status', 'Please add photos first', 'error');
    return;
  }
  showStatus('listing-status', 'Building collage...', 'loading');
  const { cols, rows } = getGridDimensions(listingPhotos.length);
  const cellSize = 600;
  const padding = 8;
  const canvas = document.getElementById('listing-canvas');
  canvas.width = (cols * cellSize) + ((cols + 1) * padding);
  canvas.height = (rows * cellSize) + ((rows + 1) * padding);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  listingPhotos.forEach((p, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = padding + col * (cellSize + padding);
    const y = padding + row * (cellSize + padding);
    const img = p.img;
    const scale = Math.min(cellSize / img.width, cellSize / img.height);
    const drawW = img.width * scale;
    const drawH = img.height * scale;
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(x, y, cellSize, cellSize);
    ctx.drawImage(img, x + (cellSize - drawW) / 2, y + (cellSize - drawH) / 2, drawW, drawH);
  });
  const fontSize = Math.max(20, canvas.width * 0.02);
  ctx.font = 'bold ' + fontSize + 'px Arial';
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.textAlign = 'right';
  ctx.fillText('ARC2', canvas.width - 16, canvas.height - 16);
  document.getElementById('listing-collage-output').style.display = 'block';
  showStatus('listing-status', 'Collage ready - ' + listingPhotos.length + ' photos in ' + cols + 'x' + rows + ' grid', 'success');
}

async function generateListing() {
  if (!listingPhotos.length) {
    showStatus('listing-status', 'Please add photos first', 'error');
    return;
  }
  showStatus('listing-status', 'Taskmaster is writing your listing...', 'loading');

  const comicTitles = listingBundle
    ? (listingBundle.comics || []).map(c => c.series + ' #' + c.issue + (c.variant ? ' CVR ' + c.variant : '')).join(', ')
    : listingSingleComic
    ? listingSingleComic.fields['Series'] + ' #' + listingSingleComic.fields['Issue']
    : 'Comic Bundle';

  try {
    const res = await fetch('/.netlify/functions/agent2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'generate_listing',
        comics: comicTitles,
        count: listingPhotos.length,
        mode: listingMode
      })
    });
    const data = await res.json();
    if (data.title) {
      document.getElementById('listing-title').value = data.title;
      document.getElementById('listing-description').value = data.description || '';
      document.getElementById('listing-price').value = data.price || '';
      document.getElementById('listing-draft').style.display = 'block';
      showStatus('listing-status', 'Listing draft ready - review and publish', 'success');
    } else {
      showStatus('listing-status', 'Error: ' + (data.error || 'Unknown error'), 'error');
    }
  } catch(e) {
    showStatus('listing-status', 'Error: ' + e.message, 'error');
  }
}

async function publishListing() {
  showStatus('listing-status', 'Publishing to eBay...', 'loading');
  const title = document.getElementById('listing-title').value;
  const price = document.getElementById('listing-price').value;
  const description = document.getElementById('listing-description').value;
  const canvas = document.getElementById('listing-canvas');
  const collageBase64 = canvas.width > 0 ? canvas.toDataURL('image/jpeg', 0.92).split(',')[1] : null;

  try {
    const res = await fetch('/.netlify/functions/agent2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'publish_listing',
        title, price, description,
        collageImage: collageBase64
      })
    });
    const data = await res.json();
    if (data.success) {
      showStatus('listing-status', 'Published to eBay! Listing ID: ' + (data.listingId || 'pending'), 'success');
    } else {
      showStatus('listing-status', 'Error: ' + (data.error || 'Unknown'), 'error');
    }
  } catch(e) {
    showStatus('listing-status', 'Error: ' + e.message, 'error');
  }
}

// ── QUICK BUNDLE BUILDER ─────────────────────────────
let quickBundleItems = [];

async function quickBundleSearch() {
  const q = document.getElementById('qb-search').value.trim();
  if (q.length < 2) { document.getElementById('qb-results').innerHTML = ''; return; }
  const formula = `OR(SEARCH(LOWER("${q}"),LOWER({Series})),SEARCH(LOWER("${q}"),LOWER({SKU})))`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 10 });
  const results = document.getElementById('qb-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d;padding:8px">No results</p>';
    return;
  }
  results.innerHTML = data.records.map(r =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +
    '<button onclick="addToQuickBundle(' + JSON.stringify(JSON.stringify(r)).slice(1,-1) + ')" class="btn btn-secondary" style="font-size:11px;padding:4px 8px">Add</button>' +
    '</div>'
  ).join('');
}

function addToQuickBundle(recordJson) {
  try {
    const r = JSON.parse(recordJson);
    if (quickBundleItems.find(i => i.id === r.id)) return;
    quickBundleItems.push(r);
    renderQuickBundleQueue();
  } catch(e) {}
}

function removeFromQuickBundle(idx) {
  quickBundleItems.splice(idx, 1);
  renderQuickBundleQueue();
}

function renderQuickBundleQueue() {
  document.getElementById('qb-count').textContent = quickBundleItems.length;
  const queue = document.getElementById('qb-queue');
  if (!quickBundleItems.length) {
    queue.innerHTML = '<p style="font-size:13px;color:#6c757d;padding:8px">No comics added yet</p>';
    return;
  }
  queue.innerHTML = quickBundleItems.map((r, i) =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +
    '<button onclick="removeFromQuickBundle(' + i + ')" class="btn btn-secondary" style="font-size:11px;padding:4px 8px;color:#dc3545">Remove</button>' +
    '</div>'
  ).join('');
}

function sendBundleToListings() {
  if (!quickBundleItems.length) {
    showStatus('qb-status', 'Add some comics first', 'error');
    return;
  }
  const name = document.getElementById('qb-name').value || 'Custom Bundle';
  listingBundle = { name, comics: quickBundleItems.map(r => ({ series: r.fields['Series'], issue: r.fields['Issue'], variant: r.fields['Variant'], sku: r.fields['SKU'] })) };
  document.getElementById('listing-bundle-name').value = name;
  document.getElementById('listing-bundle-comics').innerHTML = listingBundle.comics.map(c => c.series + ' #' + c.issue).join(', ');
  setListingMode('bundle');
  switchTab('listings');
  showStatus('qb-status', 'Bundle sent to eBay Listing Generator', 'success');
}

async function searchSingleListing() {
  const q = document.getElementById('listing-single-search').value.trim();
  if (q.length < 2) { document.getElementById('listing-single-results').innerHTML = ''; return; }
  const formula = `OR(SEARCH(LOWER("${q}"),LOWER({Series})),{SKU}="${q}")`;
  const data = await callAirtable({ action: 'search', formula, maxRecords: 5 });
  const results = document.getElementById('listing-single-results');
  if (!data.records || !data.records.length) {
    results.innerHTML = '<p style="font-size:13px;color:#6c757d">No results</p>';
    return;
  }
  results.innerHTML = data.records.map(r =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +
    '<button onclick=\'selectSingleListing(' + JSON.stringify(JSON.stringify(r)) + ')\' class="btn btn-primary" style="font-size:11px;padding:4px 8px">Select</button>' +
    '</div>'
  ).join('');
}

function selectSingleListing(recordJson) {
  try {
    listingSingleComic = JSON.parse(recordJson);
    document.getElementById('listing-single-results').innerHTML =
      '<div style="padding:8px;background:#f0f9f0;border-radius:6px;font-size:13px">Selected: ' +
      listingSingleComic.fields['Series'] + ' #' + listingSingleComic.fields['Issue'] + '</div>';
  } catch(e) {}
}
"""

# Insert JS before closing script tag
old_script_end = '\n</script>\n\n<!-- Barcode'
if old_script_end in content:
    content = content.replace(old_script_end, '\n' + listings_js + '\n</script>\n\n<!-- Barcode', 1)
    print("JS added")
else:
    # Try alternate
    old_script_end2 = '\n</script>\n<script src='
    if old_script_end2 in content:
        content = content.replace(old_script_end2, '\n' + listings_js + '\n</script>\n<script src=', 1)
        print("JS added (alt)")
    else:
        print("JS insertion point NOT found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)