with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

collage_html = """
  <!-- COLLAGE BUILDER -->
  <div class="panel panel-collage" style="display:none">
    <div class="card">
      <div class="defaults-title" style="font-size:13px;font-weight:600;color:#212529;margin-bottom:0.5rem">🖼️ Bundle Collage Builder</div>
      <p style="font-size:13px;color:#6c757d;margin-bottom:1rem">Upload individual comic photos — app builds the collage automatically.</p>

      <div style="margin-bottom:1rem">
        <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">BUNDLE TITLE (for filename)</label>
        <input type="text" id="collage-title" placeholder="e.g. Corpse Knight #1 Complete Set" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:6px;font-size:13px" />
      </div>

      <div style="margin-bottom:1rem">
        <label style="font-size:11px;color:#6c757d;display:block;margin-bottom:4px">LOGO/WATERMARK (optional, PNG recommended)</label>
        <input type="file" id="collage-logo" accept="image/*" style="font-size:13px" onchange="loadLogo(event)" />
        <div id="logo-preview" style="margin-top:8px"></div>
      </div>

      <div class="drop-zone" id="collage-drop-zone"
        onclick="document.getElementById('collage-photos').click()"
        ondragover="event.preventDefault()"
        ondrop="handleCollageDrop(event)"
        style="margin-bottom:1rem">
        <div style="font-size:32px;margin-bottom:8px">📸</div>
        <strong>Drop comic photos here or tap to select</strong>
        <p style="color:#6c757d;font-size:13px">Select multiple photos at once — one per comic</p>
        <input type="file" id="collage-photos" accept="image/*" multiple style="display:none" onchange="handleCollagePhotos(event)" />
      </div>

      <div id="collage-photo-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:1rem"></div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem">
        <button class="btn btn-secondary" onclick="clearCollagePhotos()" style="font-size:13px">Clear Photos</button>
        <button class="btn btn-primary" onclick="buildCollage()" style="font-size:13px">Build Collage</button>
      </div>

      <div id="collage-output" style="display:none">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">HERO COLLAGE</div>
        <canvas id="collage-canvas" style="width:100%;border-radius:8px;border:1px solid #dee2e6"></canvas>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">
          <button class="btn btn-secondary" onclick="downloadCollage()" style="font-size:13px">Download Collage</button>
          <button class="btn btn-primary" onclick="sendCollageToTaskmaster()" style="font-size:13px">Send to Taskmaster</button>
        </div>
      </div>

      <div class="status" id="collage-status"></div>
    </div>
  </div>
"""

collage_js = """
let collagePhotos = [];
let collageLogoImg = null;

function loadLogo(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      collageLogoImg = img;
      document.getElementById('logo-preview').innerHTML =
        '<img src="' + e.target.result + '" style="height:40px;border-radius:4px"> Logo loaded';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function handleCollageDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'));
  addCollagePhotos(files);
}

function handleCollagePhotos(event) {
  const files = Array.from(event.target.files);
  addCollagePhotos(files);
  event.target.value = '';
}

function addCollagePhotos(files) {
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        collagePhotos.push({ file, img, src: e.target.result });
        renderPhotoGrid();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function renderPhotoGrid() {
  const grid = document.getElementById('collage-photo-grid');
  grid.innerHTML = collagePhotos.map((p, i) =>
    '<div style="position:relative">' +
    '<img src="' + p.src + '" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px">' +
    '<button onclick="removeCollagePhoto(' + i + ')" style="position:absolute;top:2px;right:2px;background:rgba(0,0,0,0.6);color:white;border:none;border-radius:50%;width:20px;height:20px;font-size:11px;cursor:pointer;line-height:1">x</button>' +
    '<div style="text-align:center;font-size:10px;color:#6c757d;margin-top:2px">' + (i+1) + '</div>' +
    '</div>'
  ).join('');
  showStatus('collage-status', collagePhotos.length + ' photos loaded', 'success');
}

function removeCollagePhoto(idx) {
  collagePhotos.splice(idx, 1);
  renderPhotoGrid();
}

function clearCollagePhotos() {
  collagePhotos = [];
  document.getElementById('collage-photo-grid').innerHTML = '';
  document.getElementById('collage-output').style.display = 'none';
  showStatus('collage-status', '', '');
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

async function buildCollage() {
  if (!collagePhotos.length) {
    showStatus('collage-status', 'Please add photos first', 'error');
    return;
  }
  showStatus('collage-status', 'Building collage...', 'loading');

  const { cols, rows } = getGridDimensions(collagePhotos.length);
  const cellSize = 600;
  const padding = 8;
  const canvas = document.getElementById('collage-canvas');
  canvas.width = (cols * cellSize) + ((cols + 1) * padding);
  canvas.height = (rows * cellSize) + ((rows + 1) * padding);

  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  collagePhotos.forEach((p, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = padding + col * (cellSize + padding);
    const y = padding + row * (cellSize + padding);
    const img = p.img;
    const scale = Math.min(cellSize / img.width, cellSize / img.height);
    const drawW = img.width * scale;
    const drawH = img.height * scale;
    const offsetX = x + (cellSize - drawW) / 2;
    const offsetY = y + (cellSize - drawH) / 2;
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(x, y, cellSize, cellSize);
    ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
  });

  if (collageLogoImg) {
    const logoH = Math.min(80, canvas.height * 0.06);
    const logoW = (collageLogoImg.width / collageLogoImg.height) * logoH;
    const margin = 16;
    ctx.globalAlpha = 0.8;
    ctx.drawImage(collageLogoImg, canvas.width - logoW - margin, canvas.height - logoH - margin, logoW, logoH);
    ctx.globalAlpha = 1.0;
  } else {
    const fontSize = Math.max(20, canvas.width * 0.02);
    ctx.font = 'bold ' + fontSize + 'px Arial';
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.textAlign = 'right';
    ctx.fillText('ARC2', canvas.width - 16, canvas.height - 16);
  }

  document.getElementById('collage-output').style.display = 'block';
  showStatus('collage-status', 'Collage ready! ' + collagePhotos.length + ' photos in ' + cols + 'x' + rows + ' grid', 'success');
}

function downloadCollage() {
  const canvas = document.getElementById('collage-canvas');
  const title = document.getElementById('collage-title').value || 'bundle-collage';
  const link = document.createElement('a');
  link.download = title.replace(/[^a-z0-9]/gi, '-').toLowerCase() + '-collage.jpg';
  link.href = canvas.toDataURL('image/jpeg', 0.92);
  link.click();
}

async function sendCollageToTaskmaster() {
  const canvas = document.getElementById('collage-canvas');
  const title = document.getElementById('collage-title').value || 'Bundle';
  const base64 = canvas.toDataURL('image/jpeg', 0.85).split(',')[1];
  showStatus('collage-status', 'Sending to Taskmaster...', 'loading');
  try {
    const res = await fetch('/.netlify/functions/agent2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'publish_draft',
        draft: { title, description: 'Bundle collage generated by ARC2 app' },
        collageImage: base64
      })
    });
    const data = await res.json();
    if (data.success) {
      showStatus('collage-status', 'Sent to Taskmaster! Check Discord for listing draft.', 'success');
    } else {
      showStatus('collage-status', 'Error: ' + (data.error || 'Unknown'), 'error');
    }
  } catch(e) {
    showStatus('collage-status', 'Error: ' + e.message, 'error');
  }
}
"""

# Add collage tab button
old_tabs = "onclick=\"switchTab('ebay')\">Sales</button>"
new_tabs = "onclick=\"switchTab('ebay')\">Sales</button>\n      <button class=\"tab\" onclick=\"switchTab('collage')\">Collage</button>"
if old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("Tab button added")
else:
    print("Tab button not found")

# Add collage to switchTab array
old_arr = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','sell','agents'];"
new_arr = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','sell','agents','collage'];"
if old_arr in content:
    content = content.replace(old_arr, new_arr, 1)
    print("Tab array updated")
else:
    print("Tab array not found")

# Insert collage panel before agents panel
agents_idx = content.find('panel-agents">')
if agents_idx > 0:
    div_start = content.rfind('\n  <div', 0, agents_idx)
    content = content[:div_start] + '\n' + collage_html + content[div_start:]
    print("Panel inserted before agents")
else:
    print("Agents panel not found")

# Add JS before barcode scanner comment
old_js = '</script>\n\n<!-- Barcode S'
if old_js in content:
    content = content.replace(old_js, collage_js + '\n</script>\n\n<!-- Barcode S', 1)
    print("JS added")
else:
    print("JS insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)

print("Done")