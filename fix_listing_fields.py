with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """        <div id="listing-single-picker" style="display:none">
          <div class="field">
            <label>Search Comic</label>
            <input type="text" id="listing-single-search" placeholder="SKU or series..." oninput="searchSingleListing()" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <div id="listing-single-results"></div>
        </div>
      </div>"""

new = """        <div id="listing-single-picker" style="display:none">
          <div class="field">
            <label>Search Comic</label>
            <input type="text" id="listing-single-search" placeholder="SKU or series..." oninput="searchSingleListing()" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <div id="listing-single-results"></div>
        </div>

        <div id="listing-manual-entry" style="margin-top:12px">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">COMIC DETAILS FOR LISTING</div>
          <div id="listing-comics-list" style="margin-bottom:8px"></div>
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:6px;align-items:end">
            <input type="text" id="listing-entry-title" placeholder="Series title" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="listing-entry-issue" placeholder="Issue #" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="listing-entry-publisher" placeholder="Publisher" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <button class="btn btn-secondary" onclick="addListingComic()" style="font-size:13px;white-space:nowrap">+ Add</button>
          </div>
        </div>
      </div>"""

if old in content:
    content = content.replace(old, new, 1)
    print("Manual entry fields added")
else:
    print("Not found")

# Add JS for manual comic entry
manual_js = """
// ── MANUAL COMIC ENTRY ───────────────────────────────
let manualListingComics = [];

function addListingComic() {
  const title = document.getElementById('listing-entry-title').value.trim();
  const issue = document.getElementById('listing-entry-issue').value.trim();
  const publisher = document.getElementById('listing-entry-publisher').value.trim();
  if (!title) { showStatus('listing-status', 'Please enter a comic title', 'error'); return; }
  manualListingComics.push({ title, issue, publisher });
  renderListingComicsList();
  document.getElementById('listing-entry-title').value = '';
  document.getElementById('listing-entry-issue').value = '';
  document.getElementById('listing-entry-publisher').value = '';
  document.getElementById('listing-entry-title').focus();
}

function removeListingComic(idx) {
  manualListingComics.splice(idx, 1);
  renderListingComicsList();
}

function renderListingComicsList() {
  const list = document.getElementById('listing-comics-list');
  if (!manualListingComics.length) {
    list.innerHTML = '<p style="font-size:13px;color:#6c757d;margin-bottom:8px">No comics added yet</p>';
    return;
  }
  list.innerHTML = manualListingComics.map((c, i) =>
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid #f0f0f0">' +
    '<span style="font-size:13px">' + c.title + (c.issue ? ' #' + c.issue : '') + (c.publisher ? ' (' + c.publisher + ')' : '') + '</span>' +
    '<button onclick="removeListingComic(' + i + ')" style="background:none;border:none;color:#dc3545;font-size:13px;cursor:pointer">x</button>' +
    '</div>'
  ).join('');
}

function getListingComicsString() {
  // Priority: manual entry > bundle > single
  if (manualListingComics.length) {
    return manualListingComics.map(c =>
      c.title + (c.issue ? ' #' + c.issue : '') + (c.publisher ? ' (' + c.publisher + ')' : '')
    ).join(', ');
  }
  if (listingBundle && listingBundle.comics && listingBundle.comics.length) {
    return listingBundle.comics.map(c =>
      c.series + ' #' + c.issue + (c.variant ? ' CVR ' + c.variant : '')
    ).join(', ');
  }
  if (listingSingleComic) {
    return listingSingleComic.fields['Series'] + ' #' + listingSingleComic.fields['Issue'];
  }
  return '';
}
"""

old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + manual_js + '\n</script>\n\n<!-- Barcode', 1)
    print("Manual entry JS added")
else:
    old_js2 = '\n</script>\n<script src='
    if old_js2 in content:
        content = content.replace(old_js2, '\n' + manual_js + '\n</script>\n<script src=', 1)
        print("Manual entry JS added (alt)")
    else:
        print("JS insertion point not found")

# Fix generateListing to use getListingComicsString
old_gen = """  const comicTitles = listingBundle
    ? (listingBundle.comics || []).map(c => c.series + ' #' + c.issue + (c.variant ? ' CVR ' + c.variant : '')).join(', ')
    : listingSingleComic
    ? listingSingleComic.fields['Series'] + ' #' + listingSingleComic.fields['Issue']
    : 'Comic Bundle';"""

new_gen = """  const comicTitles = getListingComicsString();
  if (!comicTitles) {
    showStatus('listing-status', 'Please add comics using the fields above first', 'error');
    return;
  }"""

if old_gen in content:
    content = content.replace(old_gen, new_gen, 1)
    print("generateListing updated to use helper")
else:
    print("generateListing not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)