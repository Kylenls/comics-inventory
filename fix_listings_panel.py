with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the full listings panel and replace it
old_start = '  <div class="panel" id="panel-listings">'
old_end = '  <div class="panel" \n'

panel_start = content.find(old_start)
panel_end = content.find('  <div class="panel" ', panel_start + 100)

if panel_start < 0:
    print("Panel start not found")
else:
    old_panel = content[panel_start:panel_end]
    
    new_panel = '''  <div class="panel" id="panel-listings">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;height:calc(100vh - 120px)">

      <!-- LEFT: PLAN & BUILD -->
      <div style="overflow-y:auto;display:flex;flex-direction:column;gap:12px">

        <!-- Invoice Loader -->
        <div class="card">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">INVOICE LOOKUP</div>
          <div style="display:flex;gap:8px">
            <input type="text" id="lgen-invoice" placeholder="Invoice number e.g. 827969" style="flex:1;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <button class="btn btn-primary" onclick="lgenLoadInvoice()" style="white-space:nowrap">Load</button>
          </div>
          <div class="status" id="lgen-load-status" style="margin-top:8px"></div>
        </div>

        <!-- Bundle List -->
        <div class="card" id="lgen-bundles-card" style="display:none">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">BUNDLES <span id="lgen-bundle-count"></span></div>
          <div id="lgen-bundle-list"></div>
        </div>

        <!-- Queue -->
        <div class="card">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">QUEUE (<span id="lgen-queue-count">0</span> listings)</div>
          <div id="lgen-queue-list">
            <p style="font-size:13px;color:#6c757d">No listings queued yet.</p>
          </div>
        </div>

        <!-- Manual Add -->
        <div class="card">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">ADD MANUALLY</div>
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:6px;margin-bottom:6px">
            <input type="text" id="lgen-manual-title" placeholder="Series title" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="lgen-manual-issue" placeholder="Issue #" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
            <input type="text" id="lgen-manual-publisher" placeholder="Publisher" style="padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
          </div>
          <button class="btn btn-secondary" onclick="lgenAddManual()" style="width:100%;font-size:13px">+ Add to Queue</button>
        </div>

      </div>

      <!-- RIGHT: FINALIZE -->
      <div style="overflow-y:auto;display:flex;flex-direction:column;gap:12px">

        <!-- Active Bundle Banner -->
        <div class="card" id="lgen-active-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div>
              <div style="font-size:13px;font-weight:700" id="lgen-active-name">No active listing</div>
              <div style="font-size:11px;color:#6c757d" id="lgen-active-detail">Select a bundle from the queue to begin</div>
            </div>
            <span id="lgen-active-badge" style="font-size:11px;padding:3px 10px;border-radius:10px;background:#f0f0f0;color:#6c757d">Pending</span>
          </div>
        </div>

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
        <div class="card">
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
        <div class="card" id="listing-collage-card" style="display:none">
          <div class="defaults-title" style="font-size:11px;margin-bottom:8px">COLLAGE PREVIEW</div>
          <canvas id="listing-canvas" style="width:100%;border-radius:8px"></canvas>
          <button class="btn btn-secondary" onclick="downloadCollage()" style="width:100%;margin-top:8px;font-size:12px">Download Collage</button>
        </div>

        <!-- Draft -->
        <div class="card">
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

    content = content[:panel_start] + new_panel + content[panel_end:]
    print("Panel replaced, length change:", len(new_panel) - len(old_panel))

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)