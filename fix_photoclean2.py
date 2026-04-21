with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """async function cleanAllListingPhotos() {
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
}"""

new = """async function cleanAllListingPhotos() {
  if (!listingPhotos.length) {
    showStatus('listing-status', 'Please add photos first', 'error');
    return;
  }
  
  const btn = document.getElementById('listing-clean-btn');
  if (btn) btn.disabled = true;
  
  let cleaned = 0;
  let failed = 0;
  
  for (let i = 0; i < listingPhotos.length; i++) {
    showStatus('listing-status', 'AI cleaning photo ' + (i+1) + ' of ' + listingPhotos.length + '...', 'loading');
    try {
      const ok = await cleanListingPhoto(i);
      if (ok) cleaned++;
      else failed++;
    } catch(e) {
      console.error('Photo ' + (i+1) + ' failed:', e);
      failed++;
    }
    // Longer delay between API calls to avoid rate limiting
    await new Promise(r => setTimeout(r, 1500));
  }
  
  if (btn) btn.disabled = false;
  showStatus('listing-status', cleaned + ' of ' + listingPhotos.length + ' photos cleaned' + (failed > 0 ? ', ' + failed + ' failed' : ''), cleaned > 0 ? 'success' : 'error');
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed cleanAllListingPhotos")
else:
    print("Not found - checking current function")
    idx = content.find('async function cleanAllListingPhotos')
    print(content[idx:idx+200])

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)