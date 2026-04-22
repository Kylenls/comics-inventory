with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = """function sendAllStagedToListings() {
  if (!stagedBundles.length) return;
  listingQueue = [...stagedBundles];
  activeQueueIdx = -1;
  renderListingQueue();
  switchTab('listings');
  if (listingQueue.length > 0) activateQueueItem(0);
}"""

new = """function sendAllStagedToListings() {
  if (!stagedBundles.length) return;
  listingQueue = [...stagedBundles];
  activeQueueIdx = -1;
  switchTab('listings');
  if (typeof renderListingQueue === 'function') renderListingQueue();
  if (listingQueue.length > 0 && typeof activateQueueItem === 'function') activateQueueItem(0);
}"""

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed")
else:
    print("Not found")
    idx = content.find('function sendAllStagedToListings')
    print(content[idx:idx+200])

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)