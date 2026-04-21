with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Add logo upload section to listings panel
old = """      <div style="margin-top:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">PHOTOS (<span id="listing-photo-count">0</span> uploaded)</div>"""

new = """      <div style="margin-bottom:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">WATERMARK LOGO</div>
        <div style="display:flex;align-items:center;gap:10px">
          <div id="logo-preview-listing" style="font-size:13px;color:#6c757d">No logo uploaded</div>
          <button class="btn btn-secondary" onclick="document.getElementById('logo-upload-input').click()" style="font-size:12px">Upload Logo</button>
          <button class="btn btn-secondary" onclick="clearSavedLogo()" style="font-size:12px;color:#dc3545">Clear</button>
        </div>
        <input type="file" id="logo-upload-input" accept="image/png,image/jpeg" style="display:none" onchange="saveLogo(event)" />
      </div>

      <div style="margin-top:1rem">
        <div class="defaults-title" style="font-size:11px;margin-bottom:8px">PHOTOS (<span id="listing-photo-count">0</span> uploaded)</div>"""

if old in content:
    content = content.replace(old, new, 1)
    print("Logo upload section added")
else:
    print("Insertion point not found")

# Add logo JS
logo_js = """
// ── LOGO / WATERMARK ─────────────────────────────────
let savedLogoImg = null;

function initLogo() {
  const saved = localStorage.getItem('arc2_logo_base64');
  if (saved) {
    const img = new Image();
    img.onload = () => {
      savedLogoImg = img;
      document.getElementById('logo-preview-listing').innerHTML =
        '<img src="' + saved + '" style="height:32px;border-radius:4px;margin-right:6px"> Logo loaded';
    };
    img.src = saved;
  }
}

function saveLogo(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const src = e.target.result;
    localStorage.setItem('arc2_logo_base64', src);
    const img = new Image();
    img.onload = () => {
      savedLogoImg = img;
      document.getElementById('logo-preview-listing').innerHTML =
        '<img src="' + src + '" style="height:32px;border-radius:4px;margin-right:6px"> Logo saved';
    };
    img.src = src;
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function clearSavedLogo() {
  localStorage.removeItem('arc2_logo_base64');
  savedLogoImg = null;
  document.getElementById('logo-preview-listing').innerHTML = 'No logo uploaded';
}
"""

# Add JS before closing script tag
old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + logo_js + '\n</script>\n\n<!-- Barcode', 1)
    print("Logo JS added")
else:
    old_js2 = '\n</script>\n<script src='
    if old_js2 in content:
        content = content.replace(old_js2, '\n' + logo_js + '\n</script>\n<script src=', 1)
        print("Logo JS added (alt)")
    else:
        print("JS insertion point not found")

# Update buildListingCollage to use saved logo
old_collage = """  const fontSize = Math.max(20, canvas.width * 0.02);
  ctx.font = 'bold ' + fontSize + 'px Arial';
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.textAlign = 'right';
  ctx.fillText('ARC2', canvas.width - 16, canvas.height - 16);"""

new_collage = """  if (savedLogoImg) {
    const logoH = Math.min(80, canvas.height * 0.06);
    const logoW = (savedLogoImg.width / savedLogoImg.height) * logoH;
    const margin = 16;
    ctx.globalAlpha = 0.85;
    ctx.drawImage(savedLogoImg, canvas.width - logoW - margin, canvas.height - logoH - margin, logoW, logoH);
    ctx.globalAlpha = 1.0;
  } else {
    const fontSize = Math.max(20, canvas.width * 0.02);
    ctx.font = 'bold ' + fontSize + 'px Arial';
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.textAlign = 'right';
    ctx.fillText('ARC2', canvas.width - 16, canvas.height - 16);
  }"""

if old_collage in content:
    content = content.replace(old_collage, new_collage, 1)
    print("Collage logo updated")
else:
    print("Collage watermark not found")

# Init logo on page load - add to existing window.onload or add new one
old_init = "if (tab === 'inventory') { l"
if old_init in content:
    # Add initLogo call to switchTab
    content = content.replace(
        "function switchTab(tab) {",
        "function switchTab(tab) {\n  if (typeof initLogo === 'function' && !savedLogoImg) initLogo();",
        1
    )
    print("Logo init added to switchTab")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)