with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

bundle_to_listings_js = """
// ── BUNDLE TO LISTING GENERATOR ─────────────────────
function agent2BuildDraftByKey(safeKey) {
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

  // Switch to listings tab
  switchTab('listings');

  // Show confirmation in bundle planner
  const statusEl = document.getElementById('draft-status-' + safeKey);
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ Sent to eBay Listing Generator</span>';
  }
}
"""

# Insert JS before closing script tag
old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + bundle_to_listings_js + '\n</script>\n\n<!-- Barcode', 1)
    print("Bundle to listings JS added")
else:
    old_js2 = '\n</script>\n<script src='
    if old_js2 in content:
        content = content.replace(old_js2, '\n' + bundle_to_listings_js + '\n</script>\n<script src=', 1)
        print("Bundle to listings JS added (alt)")
    else:
        print("JS insertion point not found")

# Also fix generateListing to pass comicCount and coverPriceTotal from bundle
old_gen = """  const comicTitles = getListingComicsString();
  if (!comicTitles) {
    showStatus('listing-status', 'Please add comics using the fields above first', 'error');
    return;
  }"""

new_gen = """  const comicTitles = listingBundle ? (listingBundle.comicsString || getListingComicsString()) : getListingComicsString();
  if (!comicTitles) {
    showStatus('listing-status', 'Please add comics using the fields above first', 'error');
    return;
  }
  const listingComicCount = listingBundle ? (listingBundle.comicCount || listingPhotos.length || 1) : (manualListingComics.length || listingPhotos.length || 1);
  const listingCoverTotal = listingBundle ? listingBundle.coverPriceTotal : null;"""

if old_gen in content:
    content = content.replace(old_gen, new_gen, 1)
    print("generateListing updated with count and cover total")
else:
    print("generateListing not found")

# Fix the fetch call to pass count and coverPriceTotal
old_fetch = """      body: JSON.stringify({
        action: 'generate_listing',
        comics: comicTitles,
        count: listingPhotos.length,
        mode: listingMode
      })"""

new_fetch = """      body: JSON.stringify({
        action: 'generate_listing',
        comics: comicTitles,
        count: listingComicCount,
        mode: listingMode,
        coverPriceTotal: listingCoverTotal
      })"""

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch, 1)
    print("Fetch updated with count and cover total")
else:
    print("Fetch not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)