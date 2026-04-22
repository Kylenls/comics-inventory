with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

photo_js = """
// ── PHOTO STUDIO ─────────────────────────────────────
let studioPhotos = [];

function photoHandleDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'));
  photoAddFiles(files);
}

function photoAddFiles(files) {
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const src = e.target.result;
      const img = new Image();
      img.onload = () => {
        const base64 = src.split(',')[1];
        studioPhotos.push({ file, img, src, base64, cleaned: false });
        photoRenderGrid();
      };
      img.src = src;
    };
    reader.readAsDataURL(file);
  });
}

function photoRenderGrid() {
  const grid = document.getElementById('photo-grid');
  const count = document.getElementById('photo-count');
  if (!grid) return;
  if (count) count.textContent = studioPhotos.length;
  grid.innerHTML = studioPhotos.map((p, idx) =>
    '<div style="position:relative">' +
    '<img src="' + p.src + '" style="width:100%;border-radius:6px;aspect-ratio:3/4;object-fit:cover;border:2px solid ' + (p.cleaned ? '#198754' : '#dee2e6') + '">' +
    (p.cleaned ? '<div style="position:absolute;top:4px;left:4px;background:#198754;color:white;font-size:10px;padding:2px 6px;border-radius:10px">✓ Clean</div>' : '') +
    '<button onclick="photoRemove(' + idx + ')" style="position:absolute;top:4px;right:4px;background:rgba(0,0,0,0.5);color:white;border:none;border-radius:50%;width:20px;height:20px;cursor:pointer;font-size:12px;line-height:20px;text-align:center">×</button>' +
    '</div>'
  ).join('');
}

function photoRemove(idx) {
  studioPhotos.splice(idx, 1);
  photoRenderGrid();
}

function photoClearAll() {
  studioPhotos = [];
  photoRenderGrid();
  const card = document.getElementById('photo-collage-card');
  if (card) card.style.display = 'none';
  showStatus('photo-status', '', '');
}

async function photoCleanAll() {
  if (!studioPhotos.length) {
    showStatus('photo-status', 'Please upload photos first', 'error');
    return;
  }
  const btn = document.getElementById('photo-clean-btn');
  if (btn) btn.disabled = true;
  let cleaned = 0;
  let failed = 0;

  for (let i = 0; i < studioPhotos.length; i++) {
    showStatus('photo-status', 'AI cleaning photo ' + (i+1) + ' of ' + studioPhotos.length + '...', 'loading');
    try {
      const photo = studioPhotos[i];

      // Resize to under 5MB
      const resizeCanvas = document.createElement('canvas');
      const maxDim = 1600;
      let rw = photo.img.naturalWidth || photo.img.width;
      let rh = photo.img.naturalHeight || photo.img.height;
      const scale = Math.min(1, maxDim / Math.max(rw, rh));
      resizeCanvas.width = Math.floor(rw * scale);
      resizeCanvas.height = Math.floor(rh * scale);
      const rctx = resizeCanvas.getContext('2d');
      rctx.drawImage(photo.img, 0, 0, resizeCanvas.width, resizeCanvas.height);
      const base64 = resizeCanvas.toDataURL('image/jpeg', 0.80).split(',')[1];

      const res = await fetch('/.netlify/functions/cleanphoto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageBase64: base64, mediaType: 'image/jpeg' })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Clean failed');

      const adj = data.adjustments;
      const srcW = resizeCanvas.width;
      const srcH = resizeCanvas.height;
      const cropX = Math.floor(adj.cropLeft * srcW);
      const cropY = Math.floor(adj.cropTop * srcH);
      const cropW = Math.floor((adj.cropRight - adj.cropLeft) * srcW);
      const cropH = Math.floor((adj.cropBottom - adj.cropTop) * srcH);

      const outCanvas = document.createElement('canvas');
      outCanvas.width = cropW;
      outCanvas.height = cropH;
      const outCtx = outCanvas.getContext('2d');

      if (adj.rotation !== 0) {
        outCtx.translate(cropW/2, cropH/2);
        outCtx.rotate(adj.rotation * Math.PI / 180);
        outCtx.translate(-cropW/2, -cropH/2);
      }
      outCtx.drawImage(resizeCanvas, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH);

      if (adj.brightnessAdjust !== 0 || adj.contrastAdjust !== 0) {
        const brightness = 1 + (adj.brightnessAdjust / 100);
        const contrast = 1 + (adj.contrastAdjust / 100);
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = cropW;
        tempCanvas.height = cropH;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.filter = 'brightness(' + brightness + ') contrast(' + contrast + ')';
        tempCtx.drawImage(outCanvas, 0, 0);
        outCtx.clearRect(0, 0, cropW, cropH);
        outCtx.filter = 'none';
        outCtx.drawImage(tempCanvas, 0, 0);
      }

      const cleanedSrc = outCanvas.toDataURL('image/jpeg', 0.92);
      const cleanedImg = new Image();
      await new Promise(resolve => { cleanedImg.onload = resolve; cleanedImg.src = cleanedSrc; });
      studioPhotos[i].src = cleanedSrc;
      studioPhotos[i].img = cleanedImg;
      studioPhotos[i].base64 = cleanedSrc.split(',')[1];
      studioPhotos[i].cleaned = true;
      cleaned++;
      photoRenderGrid();

    } catch(e) {
      console.error('Clean photo error:', e);
      failed++;
    }
    await new Promise(r => setTimeout(r, 1000));
  }

  if (btn) btn.disabled = false;
  showStatus('photo-status', cleaned + ' photos cleaned' + (failed > 0 ? ', ' + failed + ' failed' : ''), cleaned > 0 ? 'success' : 'error');
}

async function photoBuildCollage() {
  if (!studioPhotos.length) {
    showStatus('photo-status', 'Please upload photos first', 'error');
    return;
  }

  showStatus('photo-status', 'Building collage...', 'loading');

  const count = studioPhotos.length;
  const cols = count <= 2 ? count : count <= 4 ? 2 : count <= 6 ? 3 : count <= 9 ? 3 : 4;
  const rows = Math.ceil(count / cols);
  const cellW = 600;
  const cellH = 800;
  const padding = 8;
  const canvasW = cols * cellW + (cols + 1) * padding;
  const canvasH = rows * cellH + (rows + 1) * padding;

  const canvas = document.getElementById('photo-canvas');
  canvas.width = canvasW;
  canvas.height = canvasH;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#1a1a1a';
  ctx.fillRect(0, 0, canvasW, canvasH);

  for (let i = 0; i < count; i++) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = padding + col * (cellW + padding);
    const y = padding + row * (cellH + padding);
    const img = studioPhotos[i].img;
    const scale = Math.min(cellW / img.width, cellH / img.height);
    const drawW = img.width * scale;
    const drawH = img.height * scale;
    const drawX = x + (cellW - drawW) / 2;
    const drawY = y + (cellH - drawH) / 2;
    ctx.drawImage(img, drawX, drawY, drawW, drawH);
  }

  // Add logo watermark if saved
  if (savedLogoImg) {
    const logoH = Math.min(80, canvasH * 0.05);
    const logoW = (savedLogoImg.width / savedLogoImg.height) * logoH;
    ctx.globalAlpha = 0.85;
    ctx.drawImage(savedLogoImg, canvasW - logoW - 16, canvasH - logoH - 16, logoW, logoH);
    ctx.globalAlpha = 1.0;
  } else {
    ctx.font = 'bold 24px Arial';
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.textAlign = 'right';
    ctx.fillText('ARC2', canvasW - 16, canvasH - 16);
  }

  document.getElementById('photo-collage-card').style.display = 'block';
  showStatus('photo-status', 'Collage ready - ' + count + ' photos in ' + cols + 'x' + rows + ' grid', 'success');
}

function photoDownloadCollage() {
  const canvas = document.getElementById('photo-canvas');
  const link = document.createElement('a');
  link.download = 'arc2-collage-' + Date.now() + '.jpg';
  link.href = canvas.toDataURL('image/jpeg', 0.95);
  link.click();
}

function photoDownloadAll() {
  // Download collage first
  photoDownloadCollage();
  // Then download each cleaned photo
  studioPhotos.forEach((photo, idx) => {
    setTimeout(() => {
      const link = document.createElement('a');
      link.download = 'arc2-photo-' + (idx + 1) + (photo.cleaned ? '-clean' : '') + '.jpg';
      link.href = photo.src;
      link.click();
    }, (idx + 1) * 500);
  });
}
"""

old_js = '\n</script>\n\n<!-- Barcode'
if old_js in content:
    content = content.replace(old_js, '\n' + photo_js + '\n</script>\n\n<!-- Barcode', 1)
    print("Photo JS added")
else:
    print("Insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)