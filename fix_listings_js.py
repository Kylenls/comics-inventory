with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

lgen_js = """
// ── LISTING GENERATOR v2 ─────────────────────────────
window._arc2Queue = window._arc2Queue || [];
window._arc2ActiveIdx = -1;

function lgenRenderQueue() {
  const list = document.getElementById('lgen-queue-list');
  const count = document.getElementById('lgen-queue-count');
  if (!list) return;
  count.textContent = window._arc2Queue.length;
  if (!window._arc2Queue.length) {
    list.innerHTML = '<p style="font-size:13px;color:#6c757d">No listings queued yet.</p>';
    return;
  }
  list.innerHTML = window._arc2Queue.map((item, idx) => {
    const isActive = idx === window._arc2ActiveIdx;
    const statusColor = item.status === 'Done' ? '#198754' : item.status === 'Draft Ready' ? '#0066cc' : '#6c757d';
    return '<div onclick="lgenActivate(' + idx + ')" style="display:flex;justify-content:space-between;align-items:center;padding:8px;margin-bottom:4px;border-radius:6px;cursor:pointer;border:2px solid ' + (isActive ? '#0066cc' : '#dee2e6') + ';background:' + (isActive ? '#e8f4fd' : '#fff') + '">' +
      '<div>' +
      '<div style="font-size:13px;font-weight:600">' + item.name + '</div>' +
      '<div style="font-size:11px;color:#6c757d">' + (item.comicCount || '?') + ' comics</div>' +
      '</div>' +
      '<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:' + statusColor + '20;color:' + statusColor + '">' + item.status + '</span>' +
      '</div>';
  }).join('');
}

function lgenActivate(idx) {
  window._arc2ActiveIdx = idx;
  const item = window._arc2Queue[idx];
  if (!item) return;

  // Update banner
  const nameEl = document.getElementById('lgen-active-name');
  const detailEl = document.getElementById('lgen-active-detail');
  const badgeEl = document.getElementById('lgen-active-badge');
  if (nameEl) nameEl.textContent = item.name;
  if (detailEl) detailEl.textContent = item.comicsString || '';
  if (badgeEl) {
    badgeEl.textContent = item.status;
    badgeEl.style.background = item.isPremium ? '#F0E8FA' : '#E8F8F3';
    badgeEl.style.color = item.isPremium ? '#7B3FB5' : '#198754';
  }

  // Restore photos
  listingPhotos = item.photos || [];
  renderListingPhotoGrid();

  // Restore draft
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

function lgenAddToQueue(item) {
  // Check if already in queue by name
  const existing = window._arc2Queue.findIndex(q => q.name === item.name);
  if (existing >= 0) {
    window._arc2Queue[existing] = item;
  } else {
    window._arc2Queue.push(item);
  }
  lgenRenderQueue();
  // Auto-activate if first item
  if (window._arc2Queue.length === 1) lgenActivate(0);
}

async function lgenLoadInvoice() {
  const invoice = document.getElementById('lgen-invoice').value.trim();
  if (!invoice) return;
  showStatus('lgen-load-status', 'Loading invoice...', 'loading');

  try {
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

    // Group by Series+Issue
    const groups = {};
    forSale.forEach(r => {
      const series = (r.fields['Series'] || '').trim();
      const issue = (r.fields['Issue'] || '').toString().trim();
      const key = series + ' #' + issue;
      if (!groups[key]) groups[key] = { key, series, issue, skus: [] };
      const variant = (r.fields['Variant'] || '').trim().toUpperCase();
      const variantDesc = (r.fields['Variant Description'] || '');
      const isRatio = variantDesc.toLowerCase().includes('1:') || variantDesc.toLowerCase().includes('inc ') || variantDesc.toLowerCase().includes('incentive');
      groups[key].skus.push({
        id: r.id, sku: r.fields['SKU'], variant, variantDesc,
        coverPrice: parseFloat(r.fields['Cover Price'] || 0),
        purchasePrice: parseFloat(r.fields['Purchase Price'] || 0),
        isRatio, assignment: 'single'
      });
    });

    // Render bundle list
    const bundleCard = document.getElementById('lgen-bundles-card');
    const bundleList = document.getElementById('lgen-bundle-list');
    const bundleCount = document.getElementById('lgen-bundle-count');
    bundleCard.style.display = 'block';
    bundleCount.textContent = '(' + Object.keys(groups).length + ' titles)';

    bundleList.innerHTML = Object.values(groups).map(g => {
      const safeKey = g.key.replace(/[^a-z0-9]/gi, '-');
      const variants = [...new Set(g.skus.map(s => s.variant))].sort();
      const coverTotal = g.skus.reduce((sum, s) => sum + s.coverPrice, 0);
      const hasRatio = g.skus.some(s => s.isRatio);
      return '<div style="padding:10px;border:1px solid #dee2e6;border-radius:8px;margin-bottom:8px">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
        '<div>' +
        '<div style="font-size:13px;font-weight:700">' + g.key + '</div>' +
        '<div style="font-size:11px;color:#6c757d">CVR ' + variants.join(', ') + (hasRatio ? ' ⭐' : '') + ' | ' + g.skus.length + ' copies | $' + coverTotal.toFixed(2) + ' cover total</div>' +
        '</div>' +
        '<button onclick="lgenStageBundle(\'' + safeKey + '\')" data-key="' + g.key + '" data-series="' + g.series + '" data-issue="' + g.issue + '" data-cover="' + coverTotal.toFixed(2) + '" data-count="' + g.skus.length + '" data-variants="' + variants.join(',') + '" data-premium="' + hasRatio + '" class="btn btn-primary" style="font-size:12px;white-space:nowrap">+ Queue</button>' +
        '</div>' +
        '</div>';
    }).join('');

    showStatus('lgen-load-status', forSale.length + ' comics loaded across ' + Object.keys(groups).length + ' titles', 'success');

  } catch(e) {
    showStatus('lgen-load-status', 'Error: ' + e.message, 'error');
  }
}

function lgenStageBundle(safeKey) {
  const btn = document.querySelector('[onclick="lgenStageBundle(\'' + safeKey + '\')"]');
  if (!btn) return;
  const series = btn.dataset.series;
  const issue = btn.dataset.issue;
  const coverTotal = parseFloat(btn.dataset.cover);
  const comicCount = parseInt(btn.dataset.count);
  const variants = btn.dataset.variants;
  const isPremium = btn.dataset.premium === 'true';
  const name = series + ' #' + issue + (isPremium ? ' — Premium' : '');
  const comicsString = series + ' #' + issue + ' CVR ' + variants;

  lgenAddToQueue({
    name, comicsString, comicCount, isPremium,
    coverTotal, status: 'Pending',
    photos: [], draft: null
  });

  btn.textContent = '✓ Queued';
  btn.disabled = true;
  btn.style.background = '#198754';
}

function lgenAddManual() {
  const title = document.getElementById('lgen-manual-title').value.trim();
  const issue = document.getElementById('lgen-manual-issue').value.trim();
  const publisher = document.getElementById('lgen-manual-publisher').value.trim();
  if (!title) { alert('Please enter a series title'); return; }
  const name = title + (issue ? ' #' + issue : '') + (publisher ? ' (' + publisher + ')' : '');
  lgenAddToQueue({
    name, comicsString: name, comicCount: 1,
    isPremium: false, coverTotal: 0, status: 'Pending',
    photos: [], draft: null
  });
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
    showStatus('listing-status', 'No photos found in first queue item', 'error');
  }
}

async function lgenGenerate() {
  const idx = window._arc2ActiveIdx;
  if (idx < 0 || !window._arc2Queue[idx]) {
    showStatus('listing-status', 'No active listing selected', 'error');
    return;
  }
  const item = window._arc2Queue[idx];
  showStatus('listing-status', 'Taskmaster is researching and writing your listing...', 'loading');

  // Determine shipping tier
  const count = item.comicCount || 1;
  const shipping = count <= 9 ? 12.99 : count <= 15 ? 15.99 : count <= 25 ? 19.99 : 0;

  try {
    const res = await fetch('/.netlify/functions/agent2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

    // Save draft to queue item
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
  navigator.clipboard.writeText(text).then(() => {
    showStatus('listing-status', 'Copied to clipboard', 'success');
  });
}

function lgenMarkDone() {
  const idx = window._arc2ActiveIdx;
  if (idx < 0 || !window._arc2Queue[idx]) return;

  // Save current photos and draft
  window._arc2Queue[idx].photos = [...listingPhotos];
  const title = document.getElementById('listing-title').value;
  const price = document.getElementById('listing-price').value;
  const desc = document.getElementById('listing-description').value;
  if (title) window._arc2Queue[idx].draft = { title, price, description: desc };
  window._arc2Queue[idx].status = 'Done';

  // Move to next pending
  const nextIdx = window._arc2Queue.findIndex((item, i) => i > idx && item.status !== 'Done');
  if (nextIdx >= 0) {
    lgenActivate(nextIdx);
    // Clear photos for next item
    listingPhotos = window._arc2Queue[nextIdx].photos || [];
    renderListingPhotoGrid();
  } else {
    showStatus('listing-status', 'All listings complete!', 'success');
    window._arc2ActiveIdx = -1;
    lgenRenderQueue();
  }
}
"""

# Insert before closing script tag
old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + lgen_js + '\n</script>\n\n<!-- Barcode', 1)
    print("JS added")
else:
    print("Insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)