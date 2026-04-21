with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """    // Convert image to base64
    const canvas = document.createElement('canvas');
    canvas.width = photo.img.width;
    canvas.height = photo.img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(photo.img, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg', 0.92).split(',')[1];"""

new = """    // Convert image to base64 - ensure image is loaded
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

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed image loading check")
else:
    print("Not found")
    idx = content.find('Convert image to base64')
    print(content[idx:idx+300])

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)