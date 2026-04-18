with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix the button to call openBarcodeScanner instead of file input
old = "onclick=\"document.getElementById('barcode-file-input').click()\""
new = "onclick=\"openBarcodeScanner()\""

if old in content:
    content = content.replace(old, new, 1)
    print("Button fixed")
else:
    print("Not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)