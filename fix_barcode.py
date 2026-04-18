with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the openBarcodeScanner function and replace everything up to closeBarcodeScanner
start = content.find('async function openBarcodeScanner() {')
end = content.find('\nfunction closeBarcodeScanner() {')

if start > 0 and end > 0:
    new_func = """async function openBarcodeScanner() {
  document.getElementById('barcode-file-input').click();
}

"""
    content = content[:start] + new_func + content[end:]
    print("Replaced openBarcodeScanner")
else:
    print(f"Not found - start:{start} end:{end}")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)