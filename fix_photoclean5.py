with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """    // Use stored base64 directly - no canvas needed
    const base64 = photo.base64;
    if (!base64) {
      throw new Error('No base64 data for photo ' + idx);
    }"""

new = """    // Resize image to under 5MB before sending to Claude
    const resizeCanvas = document.createElement('canvas');
    const maxDim = 1600;
    let rw = photo.img.naturalWidth || photo.img.width;
    let rh = photo.img.naturalHeight || photo.img.height;
    
    if (!rw || !rh) {
      // Try getting from stored src
      rw = 1200; rh = 1600; // safe default
    }
    
    const scale = Math.min(1, maxDim / Math.max(rw, rh));
    resizeCanvas.width = Math.floor(rw * scale);
    resizeCanvas.height = Math.floor(rh * scale);
    const rctx = resizeCanvas.getContext('2d');
    rctx.drawImage(photo.img, 0, 0, resizeCanvas.width, resizeCanvas.height);
    const base64 = resizeCanvas.toDataURL('image/jpeg', 0.80).split(',')[1];
    console.log('Photo', idx, 'resized to', base64.length, 'chars');"""

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed - added resize before API call")
else:
    print("Not found")
    idx = content.find('Use stored base64')
    print(content[idx:idx+200] if idx > 0 else 'Not found at all')

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)