with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """function agent2BuildDraftByKey(safeKey) {
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

new = """function agent2BuildDraftByKey(safeKey) {
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

  // Read actual bundle assignments from bundlePlan
  const bundlePlanGroup = window.bundlePlan && window.bundlePlan[bundleData.bundleKey];

  // Group SKUs by bundle number
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
    alert('No comics assigned to bundles yet. Use the dropdowns to assign comics to Bundle 1, 2, 3 etc first.');
    return;
  }

  // Remove previously staged bundles for this title
  stagedBundles = stagedBundles.filter(function(b) { return b.id.indexOf(safeKey) !== 0; });

  // Create one staged item per bundle number
  bundleNums.forEach(function(bNum) {
    const skus = byBundle[bNum];
    const comicCount = skus.length;
    const isPremium = bNum === 'B1' && ratios.length > 0;
    const ratioStr = isPremium ? ' (Ratio variants: ' + ratios.join(', ') + ')' : '';
    const bundleNum = parseInt(bNum.replace('B', ''));
    const comicsString = bundleData.series + ' #' + bundleData.issue + ' - ' + variantDetails + ratioStr;
    const coverTotal = skus.reduce(function(sum, s) { return sum + (s.coverPrice || 0); }, 0);

    stagedBundles.push({
      id: safeKey + '_' + bNum + '_' + Date.now(),
      name: bundleData.series + ' #' + bundleData.issue + (isPremium ? ' — Premium Bundle' : ' — Bundle ' + bundleNum),
      comicCount: comicCount,
      isPremium: isPremium,
      status: 'Pending',
      bundleData: { name: bundleData.series + ' #' + bundleData.issue, comics: [] },
      comicsString: comicsString,
      variantSummary: variantDetails + ratioStr,
      coverPriceTotal: coverTotal.toFixed(2),
      pricingMode: pricingMode,
      photos: [],
      draft: null
    });
  });

  renderStagedBar();

  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">📋 ' + bundleNums.length + ' bundles staged — click blue bar to send all</span>';
  }
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed - reads assignments from dropdowns")
else:
    print("Not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)