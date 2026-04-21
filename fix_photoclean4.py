with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Store base64 when photo is first added
old = """function addListingPhotos(files) {
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        listingPhotos.push({ file, img, src: e.target.result, cleaned: null });
        renderListingPhotoGrid();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}"""

new = """function addListingPhotos(files) {
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const src = e.target.result;
      const img = new Image();
      img.onload = () => {
        // Store base64 directly when loaded
        const base64 = src.split(',')[1];
        listingPhotos.push({ file, img, src, base64, cleaned: null });
        renderListingPhotoGrid();
      };
      img.src = src;
    };
    reader.readAsDataURL(file);
  });
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("Step 1 done - store base64 on load")
else:
    print("Step 1 NOT found")

# Use stored base64 instead of re-drawing canvas
old2 = """    // Convert image to base64 - ensure image is loaded
    await new Promise((resolve, reject) => {
      if (photo.img.complete && photo.img.naturalWidth > 0) {
        resolve();
      } else {
        photo.img.onload = resolve;
        photo.img.onerror = reject;
      }
    });
    
    if (!photo.img.naturalWidth || !photo.img.naturalHeight) {
      throw new Error('Image dimensions are 0 - image not loaded properly');
    }
    
    const canvas = document.createElement('canvas');
    canvas.width = photo.img.naturalWidth;
    canvas.height = photo.img.naturalHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(photo.img, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg', 0.92).split(',')[1];"""

new2 = """    // Use stored base64 directly - no canvas needed
    const base64 = photo.base64;
    if (!base64) {
      throw new Error('No base64 data for photo ' + idx);
    }"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Step 2 done - use stored base64")
else:
    print("Step 2 NOT found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)