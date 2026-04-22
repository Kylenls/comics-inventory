with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Replace the entire agent2BuildDraftByKey + agent2BuildDraft functions
old_fns = """function agent2BuildDraftByKey(safeKey) {
  const d = (window._bundleData || {})[safeKey];
  if (!d) { console.error('No bundle data for', safeKey); return; }
  const ratios = ['10','25','50','100'].filter(r => {
    const el = document.getElementById('ratio-' + safeKey + '-' + r);
    return el && el.checked;
  }).map(r => '1:' + r);
  const modeEl = document.querySelector('input[name="mode-' + safeKey + '"]:checked');
  const pricingMode = modeEl ? modeEl.value : 'standard';
  return agent2BuildDraft(d.bundleKey, d.series, d.issue, d.publisher, d.coverStr, d.costBasis, ratios.join(','), pricingMode);
}"""

new_fns = """// ── BUNDLE STAGING ───────────────────────────────────
let stagedBundles = [];

function renderStagedBar() {
  let bar = document.getElementById('staged-listings-bar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'staged-listings-bar';
    bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#0066cc;color:white;padding:12px 16px;z-index:1000;display:flex;justify-content:space-between;align-items:center';
    document.body.appendChild(bar);
  }
  if (!stagedBundles.length) {
    bar.style.display = 'none';
    return;
  }
  bar.style.display = 'flex';
  bar.innerHTML = '<div><strong>' + stagedBundles.length + '</strong> bundle(s) staged — ' +
    stagedBundles.map(b => b.isPremium ? '⭐ Premium' : 'Standard').join(', ') +
    '</div>' +
    '<button onclick="sendAllStagedToListings()" style="background:white;color:#0066cc;border:none;padding:8px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:13px">Send All to eBay Listing Generator →</button>';
}

function sendAllStagedToListings() {
  if (!stagedBundles.length) return;
  listingQueue = [...stagedBundles];
  activeQueueIdx = -1;
  renderListingQueue();
  switchTab('listings');
  if (listingQueue.length > 0) activateQueueItem(0);
}

function agent2BuildDraftByKey(safeKey) {
  const d = (window._bundleData || {})[safeKey];
  if (!d) { alert('Bundle data not found - please reload the invoice'); return; }
  
  const ratios = ['10','25','50','100'].filter(r => {
    const el = document.getElementById('ratio-' + safeKey + '-' + r);
    return el && el.checked;
  }).map(r => '1:' + r);
  
  const modeEl = document.querySelector('input[name="mode-' + safeKey + '"]:checked');
  const pricingMode = modeEl ? modeEl.value : 'standard';
  const isPremium = ratios.length > 0;
  const standardCount = stagedBundles.filter(b => !b.isPremium).length;
  const variantDetails = d.richCoverDesc || d.coverStr;
  const ratioStr = ratios.length ? ' (Ratio variants: ' + ratios.join(', ') + ')' : '';
  const comicsString = d.series + ' #' + d.issue + ' - ' + variantDetails + ratioStr;
  const comicCount = Object.keys((window.bundlePlan && window.bundlePlan[d.bundleKey] && window.bundlePlan[d.bundleKey].variants) || {}).length + ratios.length;

  const stagedItem = {
    id: safeKey + '_' + Date.now(),
    name: d.series + ' #' + d.issue + (isPremium ? ' — Premium' : ' — Standard ' + (standardCount + 1)),
    comicCount: comicCount || 5,
    isPremium,
    status: 'Pending',
    bundleData: { name: d.series + ' #' + d.issue, comics: [] },
    comicsString,
    variantSummary: variantDetails + ratioStr,
    coverPriceTotal: d.costBasis ? (d.costBasis * 2).toFixed(2) : null,
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
    statusEl.innerHTML = '<span style="color:#198754;font-size:12px">✓ Staged (' + stagedBundles.length + ' total) — click the blue bar to send all</span>';
  }
}"""

if 'function agent2BuildDraftByKey' in content:
    # Find and replace the function
    start = content.find('function agent2BuildDraftByKey')
    # Find the next top-level function after it
    next_fn = content.find('\nasync function agent2BuildDraft', start)
    if next_fn > 0:
        # Find the end of agent2BuildDraft
        end_of_draft = content.find('\n// ── CASH POSITION', next_fn)
        if end_of_draft > 0:
            content = content[:start] + new_fns + '\n\n' + content[end_of_draft:]
            print("Functions replaced successfully")
        else:
            print("Could not find end of agent2BuildDraft")
    else:
        print("Could not find agent2BuildDraft")
else:
    print("agent2BuildDraftByKey not found")

# Also fix listingQueue and activeQueueIdx to be simple lets if not already
if 'let listingQueue = []' not in content:
    content = content.replace('window.listingQueue = window.listingQueue || [];', 'let listingQueue = [];', 1)
    print("Fixed listingQueue declaration")

if 'let activeQueueIdx = -1' not in content:
    content = content.replace('window.activeQueueIdx = window.activeQueueIdx !== undefined ? window.activeQueueIdx : -1;', 'let activeQueueIdx = -1;', 1)
    content = content.replace('const getListingQueue = () => window.listingQueue;\nconst getActiveIdx = () => window.activeQueueIdx;', '', 1)
    print("Fixed activeQueueIdx declaration")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)