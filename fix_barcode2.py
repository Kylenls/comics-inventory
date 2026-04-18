with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Add ZXing library
content = content.replace(
    '</head>',
    '<script src="https://cdn.jsdelivr.net/npm/@zxing/browser@0.1.1/umd/index.min.js"></script>\n</head>',
    1
)

# Replace simple scanner with ZXing live scanner
start = content.find('async function openBarcodeScanner() {')
end = content.find('\nfunction closeBarcodeScanner() {')

new_func = """async function openBarcodeScanner() {
  const overlay = document.getElementById('barcode-overlay');
  overlay.style.display = 'flex';
  document.getElementById('barcode-status').textContent = 'Starting camera...';
  barcodeTriggered = false;

  try {
    if (typeof ZXingBrowser === 'undefined') {
      throw new Error('Barcode library not loaded');
    }
    
    const codeReader = new ZXingBrowser.BrowserMultiFormatReader();
    const videoEl = document.getElementById('barcode-video');
    
    document.getElementById('barcode-status').textContent = 'Point at barcode — scanning...';
    
    await codeReader.decodeFromConstraints(
      { video: { facingMode: { ideal: 'environment' } } },
      videoEl,
      (result, error, controls) => {
        if (result && !barcodeTriggered) {
          barcodeTriggered = true;
          controls.stop();
          const code = result.getText();
          document.getElementById('barcode-status').textContent = 'Found: ' + code;
          setTimeout(() => {
            closeBarcodeScanner();
            processBarcodeResult(code, null, null);
          }, 500);
        }
      }
    );
  } catch(e) {
    overlay.style.display = 'none';
    showStatus('add-status', 'Scanner error: ' + e.message + ' — try Scan Cover instead', 'error');
  }
}

"""

if start > 0 and end > 0:
    content = content[:start] + new_func + content[end:]
    print("ZXing scanner installed")
else:
    print(f"Not found - start:{start} end:{end}")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)