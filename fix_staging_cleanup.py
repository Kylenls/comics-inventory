with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old_fn = """function agent2BuildDraftByKey(safeKey) {
  const bundleData = window._bundleData && window._bundleData[safeKey];
  if (!bundleData) {
    alert('Bundle data not found - please reload the invoice');
    return;
  }

  // Get ratio checkboxes
  const ratios = [];
  ['10','25','50','100'].forEach(r => {
    const cb = document.getElementById('ratio-' + safeKey + '-' + r);
    if (cb && cb.checked) ratios.push('1:' + r);
  });

  // Get pricing mode
  const modeEl = document.querySelector('input[name="mode-' + safeKey + '"]:checked');
  const pricingMode = modeEl ? modeEl.value : 'standard';

  // Build comics string with all variant details
  const variantDetails = bundleData.richCoverDesc || bundleData.coverStr;
  const ratioStr = ratios.length ? ' (Ratio variants: ' + ratios.join(', ') + ')' : '';
  const comicsString = bundleData.series + ' #' + bundleData.issue + ' - ' + variantDetails + ratioStr;

  // Count comics in bundle (from assigned SKUs)
  const bundlePlanGroup = window.bundlePlan && window.bundlePlan[bundleData.bundleKey];
  let comicCount = 1;
  if (bundlePlanGroup) {
    const assignedToBundle = bundlePlanGroup.skus.filter(s => s.assignment && s.assignment.startsWith('B'));
    comicCount = assignedToBundle.length || bundlePlanGroup.skus.length;
  }

  // Send to listing generator
  listingBundle = {
    name: bundleData.series + ' #' + bundleData.issue + ' Complete Bundle',
    comics: bundleData.richCoverDesc.split(', ').map(c => ({
      series: bundleData.series,
      issue: bundleData.issue,
      variant: c.replace('CVR ', '').split(' ')[0],
      variantDesc: c
    })),
    comicsString,
    comicCount,
    coverPriceTotal: bundleData.costBasis ? (bundleData.costBasis * (1/0.5)).toFixed(2) : null,
    pricingMode,
    ratios
  };

  // Update listing generator UI
  setListingMode('bundle');
  document.getElementById('listing-bundle-name').value = listingBundle.name;
  document.getElementById('listing-bundle-comics').innerHTML = 
    '<div style="font-size:12px;color:#6c757d;margin-top:4px">' + variantDetails + '</div>' +
    (ratios.length ? '<div style="font-size:12px;color:#7B3FB5;margin-top:2px">Ratio variants: ' + ratios.join(', ') + '</div>' : '');

  // Determine if this is a premium bundle (has ratio variants)
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

new_fn = """function agent2BuildDraftByKey(safeKey) {
  const bundleData = window._bundleData && window._bundleData[safeKey];
  if (!bundleData) {
    alert('Bundle data not found - please reload the invoice');
    return;
  }

  const ratios = [];
  ['10','25','50','100'].forEach(r => {
    const cb = document.getElementById('ratio-' + safeKey + '-' + r);
    if (cb && cb.checked) ratios.push('1:' + r);
  });

  const modeEl = document.querySelector('input[name="mode-' + safeKey + '"]:checked');
  const pricingMode = modeEl ? modeEl.value : 'standard';
  const variantDetails = bundleData.richCoverDesc || bundleData.coverStr;
  const ratioStr = ratios.length ? ' (Ratio variants: ' + ratios.join(', ') + ')' : '';
  const comicsString = bundleData.series + ' #' + bundleData.issue + ' - ' + variantDetails + ratioStr;
  const isPremium = ratios.length > 0;
  const standardCount = stagedBundles.filter(b => !b.isPremium).length;

  const bundlePlanGroup = window.bundlePlan && window.bundlePlan[bundleData.bundleKey];
  let comicCount = 5;
  if (bundlePlanGroup) {
    const assigned = bundlePlanGroup.skus.filter(s => s.assignment && s.assignment.startsWith('B'));
    comicCount = assigned.length || bundlePlanGroup.skus.length;
  }

  const stagedItem = {
    id: safeKey + '_' + Date.now(),
    name: bundleData.series + ' #' + bundleData.issue + (isPremium ? ' — Premium' : ' — Standard ' + (standardCount + 1)),
    comicCount,
    isPremium,
    status: 'Pending',
    bundleData: { name: bundleData.series + ' #' + bundleData.issue, comics: [] },
    comicsString,
    variantSummary: variantDetails + ratioStr,
    coverPriceTotal: bundleData.costBasis ? (bundleData.costBasis * 2).toFixed(2) : null,
    pricingMode,
    photos: [],
    draft: null
  };

  const existingIdx = stagedBundles.findIndex(b => b.id.startsWith(safeKey));
  if (existingIdx >= 0) {
    stagedBundles[existingIdx] = stagedItem;
  } else {
    stagedBundles.push(stagedItem);
  }

  renderStagedBar();

  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">📋 Staged (' + stagedBundles.length + ' total) — click blue bar at bottom to send all</span>';
  }
}"""

if old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    print("Function replaced successfully")
else:
    print("NOT FOUND - checking")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)