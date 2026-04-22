import re

with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Simple replacements first
replacements = [
    ('listingQueue = [...stagedBundles]', 'window._listingQueue = [...stagedBundles]'),
    ('listingQueue.push', 'window._listingQueue.push'),
    ('listingQueue.length', 'window._listingQueue.length'),
    ('listingQueue.map', 'window._listingQueue.map'),
    ('listingQueue.filter', 'window._listingQueue.filter'),
    ('listingQueue[0]', 'window._listingQueue[0]'),
    ('listingQueue[idx]', 'window._listingQueue[idx]'),
    ('listingQueue[activeQueueIdx]', 'window._listingQueue[window._activeQueueIdx]'),
    ('listingQueue = []', 'window._listingQueue = []'),
    ('activeQueueIdx = -1', 'window._activeQueueIdx = -1'),
    ('activeQueueIdx = idx', 'window._activeQueueIdx = idx'),
    ('activeQueueIdx >= 0', 'window._activeQueueIdx >= 0'),
    ('listingQueue[window._activeQueueIdx]', 'window._listingQueue[window._activeQueueIdx]'),
]

for old, new in replacements:
    count = content.count(old)
    if count:
        content = content.replace(old, new)
        print(f'Replaced {count}x: {old[:40]}')

# Replace remaining bare listingQueue and activeQueueIdx
content = re.sub(r'\blistingQueue\b', 'window._listingQueue', content)
content = re.sub(r'\bactiveQueueIdx\b', 'window._activeQueueIdx', content)

print('Total window._listingQueue refs:', content.count('window._listingQueue'))
print('Total window._activeQueueIdx refs:', content.count('window._activeQueueIdx'))

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)