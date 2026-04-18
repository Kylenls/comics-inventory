with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Find the handleFOCFile function and update it to also send to focupload
old = "async function handleFOCFile(event) {\n  const file = event.target.files[0];\n  const distributor = document.querySelector('input[name=\"foc-distributor\"]:checked')?.value || 'lunar';\n  if (!file) return;\n  showStatus('foc-status', 'Reading FOC catalog...', 'loading');"

new = """async function handleFOCFile(event) {
  const file = event.target.files[0];
  const distributor = document.querySelector('input[name="foc-distributor"]:checked')?.value || 'lunar';
  if (!file) return;
  showStatus('foc-status', 'Reading FOC catalog...', 'loading');

  // Send to Oracle's inbox via Airtable
  const reader2 = new FileReader();
  reader2.onload = async (e2) => {
    try {
      await fetch('/.netlify/functions/focupload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: file.name,
          content: e2.target.result,
          distributor: distributor
        })
      });
      console.log('FOC file queued for Oracle');
    } catch(err) {
      console.warn('Could not queue for Oracle:', err.message);
    }
  };
  reader2.readAsText(file);"""

if old in content:
    content = content.replace(old, new, 1)
    print("FOC handler updated")
else:
    print("Not found - checking...")
    idx = content.find('async function handleFOCFile')
    print(content[idx:idx+300])

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)