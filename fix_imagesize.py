with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """async function handleCoverPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const base64 = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  await processImageBase64(base64, file.type || 'image/jpeg', 'cover');
  event.target.value = '';
}"""

new = """async function handleCoverPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Compress image to under 4MB before sending
  const base64 = await compressImage(file, 1600, 0.85);
  await processImageBase64(base64, 'image/jpeg', 'cover');
  event.target.value = '';
}

async function compressImage(file, maxWidth, quality) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        if (width > maxWidth) {
          height = Math.round(height * maxWidth / width);
          width = maxWidth;
        }
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        resolve(dataUrl.split(',')[1]);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("Image compression added")
else:
    print("Function not found - checking...")
    idx = content.find('async function handleCoverPhoto')
    print(content[idx:idx+200])

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)