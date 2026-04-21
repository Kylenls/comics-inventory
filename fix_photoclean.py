with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

clean_js = """
async function cleanListingPhoto(idx) {
  const photo = listingPhotos[idx];
  if (!photo) return;
  
  showStatus('listing-status', 'AI cleaning photo ' + (idx+1) + ' of ' + listingPhotos.length + '...', 'loading');
  
  try {
    // Convert image to base64
    const canvas = document.createElement('canvas');
    canvas.width = photo.img.width;
    canvas.height = photo.img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(photo.img, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg', 0.92).split(',')[1];
    
    // Send to cleanphoto function
    const res = await fetch('/.netlify/functions/cleanphoto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageBase64: base64, mediaType: 'image/jpeg' })
    });
    const data = await res.json();
    
    if (!data.success) throw new Error(data.error || 'Clean failed');
    
    const adj = data.adjustments;
    
    // Apply adjustments to canvas
    const srcW = photo.img.width;
    const srcH = photo.img.height;
    const cropX = Math.floor(adj.cropLeft * srcW);
    const cropY = Math.floor(adj.cropTop * srcH);
    const cropW = Math.floor((adj.cropRight - adj.cropLeft) * srcW);
    const cropH = Math.floor((adj.cropBottom - adj.cropTop) * srcH);
    
    const outCanvas = document.createElement('canvas');
    outCanvas.width = cropW;
    outCanvas.height = cropH;
    const outCtx = outCanvas.getContext('2d');
    
    // Apply rotation if needed
    if (adj.rotation !== 0) {
      outCtx.translate(cropW/2, cropH/2);
      outCtx.rotate(adj.rotation * Math.PI / 180);
      outCtx.translate(-cropW/2, -cropH/2);
    }
    
    // Draw cropped image
    outCtx.drawImage(photo.img, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH);
    
    // Apply brightness/contrast via CSS filter
    if (adj.brightnessAdjust !== 0 || adj.contrastAdjust !== 0) {
      const brightness = 1 + (adj.brightnessAdjust / 100);
      const contrast = 1 + (adj.contrastAdjust / 100);
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = cropW;
      tempCanvas.height = cropH;
      const tempCtx = tempCanvas.getContext('2d');
      tempCtx.filter = 'brightness(' + brightness + ') contrast(' + contrast + ')';
      tempCtx.drawImage(outCanvas, 0, 0);
      outCanvas.width = cropW;
      outCanvas.height = cropH;
      outCtx.drawImage(tempCanvas, 0, 0);
    }
    
    // Store cleaned version
    const cleanedSrc = outCanvas.toDataURL('image/jpeg', 0.92);
    const cleanedImg = new Image();
    cleanedImg.onload = () => {
      listingPhotos[idx].cleaned = cleanedSrc;
      listingPhotos[idx].img = cleanedImg;
      renderListingPhotoGrid();
    };
    cleanedImg.src = cleanedSrc;
    
    return true;
  } catch(e) {
    console.error('Clean photo error:', e);
    return false;
  }
}

async function cleanAllListingPhotos() {
  if (!listingPhotos.length) {
    showStatus('listing-status', 'Please add photos first', 'error');
    return;
  }
  showStatus('listing-status', 'Starting AI photo cleaning...', 'loading');
  
  let cleaned = 0;
  for (let i = 0; i < listingPhotos.length; i++) {
    const ok = await cleanListingPhoto(i);
    if (ok) cleaned++;
    // Small delay between API calls
    await new Promise(r => setTimeout(r, 500));
  }
  
  showStatus('listing-status', cleaned + ' of ' + listingPhotos.length + ' photos cleaned by AI', 'success');
}
"""

# Insert before closing script tag
old = '\n</script>\n<script src='
if old in content:
    content = content.replace(old, '\n' + clean_js + '\n</script>\n<script src=', 1)
    print("Clean JS added")
else:
    old2 = '\n</script>\n\n<!-- Barcode'
    if old2 in content:
        content = content.replace(old2, '\n' + clean_js + '\n</script>\n\n<!-- Barcode', 1)
        print("Clean JS added (alt)")
    else:
        print("JS insertion point not found")

# Add Clean All button to listing generator photo section
old_btn = '        <button class="btn btn-secondary" onclick="buildListingCollage()" id="listing-collage-btn">Build Collage</button>'
new_btn = '        <button class="btn btn-secondary" onclick="cleanAllListingPhotos()" id="listing-clean-btn">AI Clean Photos</button>\n        <button class="btn btn-secondary" onclick="buildListingCollage()" id="listing-collage-btn">Build Collage</button>'
if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("Clean button added")
else:
    print("Button insertion point not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)