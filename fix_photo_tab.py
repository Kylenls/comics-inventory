import re

with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Step 1: Update tabs array - remove bundles and listings, add photos
old_tabs = "'add','invoice','foc','import','inventory','pc','bundles','update','ebay','listings','agents'"
new_tabs = "'add','invoice','foc','import','inventory','pc','update','ebay','photos','agents'"
if old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("Step 1: Tabs array updated")
else:
    print("Step 1 FAILED - tabs not found")

# Step 2: Update tab buttons - remove bundles and listings, add photos
old_btns = """      <button class="tab" onclick="switchTab('bundles')">Bundles</button>
      <button class="tab" onclick="switchTab('update')">Update</button>
      <button class="tab" onclick="switchTab('ebay')">eBay</button>
      <button class="tab" onclick="switchTab('listings')">eBay Listings</button>
      <button class="tab" onclick="switchTab('agents')">Agents</button>"""
new_btns = """      <button class="tab" onclick="switchTab('update')">Update</button>
      <button class="tab" onclick="switchTab('ebay')">eBay</button>
      <button class="tab" onclick="switchTab('photos')">📸 Photos</button>
      <button class="tab" onclick="switchTab('agents')">Agents</button>"""
if old_btns in content:
    content = content.replace(old_btns, new_btns, 1)
    print("Step 2: Tab buttons updated")
else:
    print("Step 2 FAILED - checking buttons")
    idx = content.find("switchTab('bundles')")
    print("  bundles button at:", idx)

# Step 3: Remove bundles panel
bundles_start = content.find('  <div class="panel" id="panel-bundles">')
listings_start = content.find('  <div class="panel" id="panel-listings">')
update_start = content.find('  <div class="panel" id="panel-update">')
agents_start = content.find('  <div class="panel" id="panel-agents">')

if bundles_start > 0 and update_start > 0:
    content = content[:bundles_start] + content[update_start:]
    print("Step 3: Bundles panel removed")
else:
    print("Step 3 FAILED - bundles:", bundles_start, "update:", update_start)

# Step 4: Remove listings panel (re-find after removing bundles)
listings_start = content.find('  <div class="panel" id="panel-listings">')
agents_start = content.find('  <div class="panel" id="panel-agents">')

if listings_start > 0 and agents_start > 0:
    content = content[:listings_start] + content[agents_start:]
    print("Step 4: Listings panel removed")
else:
    print("Step 4 FAILED - listings:", listings_start, "agents:", agents_start)

# Step 5: Add photos panel before agents panel
agents_start = content.find('  <div class="panel" id="panel-agents">')

photos_panel = '''  <div class="panel" id="panel-photos">
    <div class="card">
      <div class="defaults-title" style="font-size:13px;font-weight:600;margin-bottom:4px">📸 Photo Studio</div>
      <p style="font-size:12px;color:#6c757d;margin-bottom:12px">Upload lightbox photos, AI clean them, build a collage, then download everything.</p>

      <!-- Upload -->
      <div class="defaults-title" style="font-size:11px;margin-bottom:8px">UPLOAD PHOTOS (<span id="photo-count">0</span> uploaded)</div>
      <div id="photo-drop-zone"
        ondrop="photoHandleDrop(event)" ondragover="event.preventDefault()"
        onclick="document.getElementById('photo-file-input').click()"
        style="border:2px dashed #dee2e6;border-radius:8px;padding:30px;text-align:center;cursor:pointer;margin-bottom:8px">
        <div style="font-size:24px;margin-bottom:8px">📷</div>
        <div style="font-size:13px;color:#6c757d">Drop photos here or click to upload</div>
        <div style="font-size:11px;color:#adb5bd;margin-top:4px">Supports JPG, PNG — multiple files OK</div>
      </div>
      <input type="file" id="photo-file-input" multiple accept="image/*" style="display:none" onchange="photoAddFiles(Array.from(this.files))" />

      <!-- Photo Grid -->
      <div id="photo-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px"></div>

      <!-- Actions -->
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
        <button class="btn btn-secondary" onclick="photoCleanAll()" id="photo-clean-btn" style="font-size:13px">🤖 AI Clean All</button>
        <button class="btn btn-secondary" onclick="photoBuildCollage()" id="photo-collage-btn" style="font-size:13px">🖼️ Build Collage</button>
        <button class="btn btn-secondary" onclick="photoClearAll()" style="font-size:13px;color:#dc3545">🗑️ Clear All</button>
      </div>

      <div class="status" id="photo-status"></div>
    </div>

    <!-- Collage Preview -->
    <div class="card" id="photo-collage-card" style="display:none;margin-top:12px">
      <div class="defaults-title" style="font-size:11px;margin-bottom:8px">COLLAGE PREVIEW</div>
      <canvas id="photo-canvas" style="width:100%;border-radius:8px;margin-bottom:12px"></canvas>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-primary" onclick="photoDownloadCollage()" style="font-size:13px">⬇️ Download Collage</button>
        <button class="btn btn-secondary" onclick="photoDownloadAll()" style="font-size:13px">⬇️ Download All Photos</button>
      </div>
    </div>
  </div>

'''

if agents_start > 0:
    content = content[:agents_start] + photos_panel + content[agents_start:]
    print("Step 5: Photos panel added")
else:
    print("Step 5 FAILED - agents panel not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)