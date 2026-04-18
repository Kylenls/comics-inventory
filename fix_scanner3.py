with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix PIN
content = content.replace("const CORRECT_PIN = '104545'", "const CORRECT_PIN = '42069'")
print("PIN updated" if "42069" in content else "PIN not found")

# Fix barcode scanner - ZXing might not work on Safari
# Use simpler approach: open camera, capture frame, send to Claude every 2 seconds
old_start = content.find('async function openBarcodeScanner() {')
old_end = content.find('\nfunction closeBarcodeScanner() {')

new_func = """async function openBarcodeScanner() {
  const overlay = document.getElementById('barcode-overlay');
  overlay.style.display = 'flex';
  document.getElementById('barcode-status').textContent = 'Starting camera...';
  barcodeTriggered = false;

  try {
    barcodeStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } }
    });
    const video = document.getElementById('barcode-video');
    video.srcObject = barcodeStream;
    await video.play();
    document.getElementById('barcode-status').textContent = 'Hold barcode steady — scanning...';

    // Try native BarcodeDetector first (Chrome/Android)
    if ('BarcodeDetector' in window) {
      barcodeDetector = new BarcodeDetector({ formats: ['upc_a','upc_e','ean_13','ean_8','code_128'] });
      startNativeDetection(video);
      return;
    }

    // Fallback: capture frames and send to Claude every 2.5 seconds
    let attempts = 0;
    barcodeInterval = setInterval(async () => {
      if (barcodeTriggered || attempts >= 10) {
        if (attempts >= 10) {
          document.getElementById('barcode-status').textContent = 'Having trouble — try Scan Cover instead';
          clearInterval(barcodeInterval);
        }
        return;
      }
      attempts++;
      document.getElementById('barcode-status').textContent = 'Scanning... attempt ' + attempts + '/10';
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      canvas.toBlob(async (blob) => {
        const reader = new FileReader();
        reader.onload = async () => {
          const base64 = reader.result.split(',')[1];
          try {
            const res = await fetch('/.netlify/functions/decodebarcode', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ imageBase64: base64 })
            });
            const data = await res.json();
            if (data.barcode && !barcodeTriggered) {
              barcodeTriggered = true;
              clearInterval(barcodeInterval);
              document.getElementById('barcode-status').textContent = 'Found: ' + data.barcode;
              setTimeout(() => {
                closeBarcodeScanner();
                processBarcodeResult(data.barcode, data.variant, data.printRun);
              }, 500);
            }
          } catch(e) {}
        };
        reader.readAsDataURL(blob);
      }, 'image/jpeg', 0.8);
    }, 2500);

  } catch(e) {
    overlay.style.display = 'none';
    showStatus('add-status', 'Camera error: ' + e.message, 'error');
  }
}

"""

if old_start > 0 and old_end > 0:
    content = content[:old_start] + new_func + content[old_end:]
    print("Scanner replaced")
else:
    print(f"Not found: start={old_start} end={old_end}")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)