with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# 1. Add listing queue UI to the listings panel - insert before photo section
old_source = """      <div id="listing-source-card">"""
new_source = """      <div id="listing-queue-card" style="margin-bottom:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">LISTING QUEUE (<span id="queue-count">0</span> bundles)</div>
        <div id="listing-queue-list" style="max-height:200px;overflow-y:auto;margin-bottom:8px">
          <p style="font-size:13px;color:#6c757d">No bundles queued yet. Send bundles from the Bundles tab.</p>
        </div>
        <div id="active-listing-banner" style="display:none;padding:8px;background:#e8f4fd;border-radius:6px;font-size:13px;margin-bottom:8px">
          <strong>Active: </strong><span id="active-listing-name"></span>
          <span id="active-listing-badge" style="margin-left:8px;padding:2px 8px;border-radius:10px;font-size:11px"></span>
        </div>
      </div>

      <div id="listing-source-card">"""

if old_source in content:
    content = content.replace(old_source, new_source, 1)
    print("Queue UI added")
else:
    print("Source card not found")

# 2. Replace agent2BuildDraftByKey with queue-based version
old_fn = """// ── BUNDLE TO LISTING GENERATOR ─────────────────────
function agent2BuildDraftByKey(safeKey) {"""

new_fn = """// ── LISTING QUEUE ────────────────────────────────────
let listingQueue = [];
let activeQueueIdx = -1;

function renderListingQueue() {
  document.getElementById('queue-count').textContent = listingQueue.length;
  const list = document.getElementById('listing-queue-list');
  if (!listingQueue.length) {
    list.innerHTML = '<p style="font-size:13px;color:#6c757d">No bundles queued. Send from Bundles tab.</p>';
    return;
  }
  list.innerHTML = listingQueue.map((item, idx) => {
    const isActive = idx === activeQueueIdx;
    const statusColor = item.status === 'Published' ? '#198754' : item.status === 'Draft Ready' ? '#0066cc' : item.status === 'Photos Added' ? '#fd7e14' : '#6c757d';
    return '<div onclick="activateQueueItem(' + idx + ')" style="display:flex;justify-content:space-between;align-items:center;padding:8px;margin-bottom:4px;border-radius:6px;cursor:pointer;border:2px solid ' + (isActive ? '#0066cc' : '#dee2e6') + ';background:' + (isActive ? '#e8f4fd' : '#fff') + '">' +
      '<div>' +
      '<div style="font-size:13px;font-weight:600">' + item.name + '</div>' +
      '<div style="font-size:11px;color:#6c757d">' + item.comicCount + ' comics | ' + (item.isPremium ? '⭐ Premium' : 'Standard') + '</div>' +
      '</div>' +
      '<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:' + statusColor + '20;color:' + statusColor + '">' + item.status + '</span>' +
      '</div>';
  }).join('');
}

function activateQueueItem(idx) {
  activeQueueIdx = idx;
  const item = listingQueue[idx];
  
  // Update banner
  document.getElementById('active-listing-banner').style.display = 'block';
  document.getElementById('active-listing-name').textContent = item.name;
  const badge = document.getElementById('active-listing-badge');
  badge.textContent = item.isPremium ? '⭐ Premium Bundle' : 'Standard Bundle';
  badge.style.background = item.isPremium ? '#F0E8FA' : '#E8F8F3';
  badge.style.color = item.isPremium ? '#7B3FB5' : '#198754';
  
  // Load bundle into listing generator
  listingBundle = item.bundleData;
  setListingMode('bundle');
  document.getElementById('listing-bundle-name').value = item.name;
  document.getElementById('listing-bundle-comics').innerHTML = 
    '<div style="font-size:12px;color:#6c757d;margin-top:4px">' + item.variantSummary + '</div>';
  
  // If standard bundle and we have photos from premium, offer to reuse
  if (!item.isPremium && listingQueue[0] && listingQueue[0].photos && listingQueue[0].photos.length) {
    showStatus('listing-status', 'Tip: This is a standard bundle. You can reuse photos from Bundle 1 or upload new ones.', 'loading');
  } else {
    showStatus('listing-status', 'Bundle loaded - upload photos then generate listing', 'success');
  }
  
  // Restore photos if already uploaded for this item
  if (item.photos && item.photos.length) {
    listingPhotos = item.photos;
    renderListingPhotoGrid();
  } else {
    listingPhotos = [];
    renderListingPhotoGrid();
  }
  
  // Restore draft if exists
  if (item.draft) {
    document.getElementById('listing-title').value = item.draft.title || '';
    document.getElementById('listing-price').value = item.draft.price || '';
    document.getElementById('listing-description').value = item.draft.description || '';
    document.getElementById('listing-draft').style.display = 'block';
  } else {
    document.getElementById('listing-draft').style.display = 'none';
  }
  
  renderListingQueue();
}

function saveActiveQueuePhotos() {
  if (activeQueueIdx >= 0 && listingQueue[activeQueueIdx]) {
    listingQueue[activeQueueIdx].photos = [...listingPhotos];
    if (listingPhotos.length > 0 && listingQueue[activeQueueIdx].status === 'Pending') {
      listingQueue[activeQueueIdx].status = 'Photos Added';
      renderListingQueue();
    }
  }
}

function reuseStandardPhotos() {
  if (listingQueue[0] && listingQueue[0].photos && listingQueue[0].photos.length) {
    // Copy photos from bundle 1 but exclude ratio-only photos
    listingPhotos = [...listingQueue[0].photos];
    renderListingPhotoGrid();
    showStatus('listing-status', 'Photos copied from Bundle 1 - remove any ratio variant photos that don\\'t apply', 'success');
  }
}

// ── BUNDLE TO LISTING GENERATOR ─────────────────────
function agent2BuildDraftByKey(safeKey) {"""

if old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    print("Queue functions added")
else:
    print("agent2BuildDraftByKey not found")

# 3. Update agent2BuildDraftByKey body to add to queue instead of switching tab
old_body = """  // Switch to listings tab
  switchTab('listings');

  // Show confirmation in bundle planner
  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ Sent to eBay Listing Generator</span>';
  }
}"""

new_body = """  // Determine if this is a premium bundle (has ratio variants)
  const isPremium = ratios.length > 0;
  
  // Add to queue
  const queueItem = {
    id: safeKey + '_' + Date.now(),
    name: bundleData.series + ' #' + bundleData.issue + (isPremium ? ' — Premium Bundle' : ' — Standard Bundle ' + (listingQueue.filter(i => !i.isPremium).length + 1)),
    comicCount,
    isPremium,
    status: 'Pending',
    bundleData: listingBundle,
    variantSummary: variantDetails + ratioStr,
    photos: [],
    draft: null
  };
  
  listingQueue.push(queueItem);
  renderListingQueue();

  // Switch to listings tab and activate this item
  switchTab('listings');
  activateQueueItem(listingQueue.length - 1);

  // Show confirmation in bundle planner
  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ Added to listing queue (' + listingQueue.length + ' total)</span>';
  }
}"""

if old_body in content:
    content = content.replace(old_body, new_body, 1)
    print("agent2BuildDraftByKey updated for queue")
else:
    print("agent2BuildDraftByKey body not found")

# 4. Add "Reuse Photos" button to listing generator
old_photo_section = """        <div class="drop-zone" id="listing-drop-zone\""""
new_photo_section = """        <div id="reuse-photos-banner" style="display:none;margin-bottom:8px">
          <button class="btn btn-secondary" onclick="reuseStandardPhotos()" style="width:100%;font-size:13px">♻️ Reuse Photos from Bundle 1</button>
        </div>
        <div class="drop-zone" id="listing-drop-zone\""""

if old_photo_section in content:
    content = content.replace(old_photo_section, new_photo_section, 1)
    print("Reuse photos button added")
else:
    print("Photo section not found")

# 5. Save photos to queue when building collage
old_collage_fn = """async function buildListingCollage() {"""
new_collage_fn = """async function buildListingCollage() {
  saveActiveQueuePhotos();"""

if old_collage_fn in content:
    content = content.replace(old_collage_fn, new_collage_fn, 1)
    print("Collage saves photos to queue")
else:
    print("buildListingCollage not found")

# 6. Save draft to queue when generated
old_draft_save = """      document.getElementById('listing-title').value = data.title;
      document.getElementById('listing-description').value = data.description || '';
      document.getElementById('listing-price').value = data.price || '';
      document.getElementById('listing-draft').style.display = 'block';
      showStatus('listing-status', 'Listing draft ready - review and publish', 'success');"""

new_draft_save = """      document.getElementById('listing-title').value = data.title;
      document.getElementById('listing-description').value = data.description || '';
      document.getElementById('listing-price').value = data.price || '';
      document.getElementById('listing-draft').style.display = 'block';
      showStatus('listing-status', 'Listing draft ready - review and publish', 'success');
      // Save draft to queue
      if (activeQueueIdx >= 0 && listingQueue[activeQueueIdx]) {
        listingQueue[activeQueueIdx].draft = { title: data.title, price: data.price, description: data.description };
        listingQueue[activeQueueIdx].status = 'Draft Ready';
        renderListingQueue();
      }"""

if old_draft_save in content:
    content = content.replace(old_draft_save, new_draft_save, 1)
    print("Draft saves to queue")
else:
    print("Draft save not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)