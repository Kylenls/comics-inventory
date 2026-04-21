content = open('/Users/kylenelson/arc2-comics/index.html').read()

# Remove the broken Sold tab button - consolidate into Sales
old = "      <button class=\"tab\" onclick=\"switchTab('ebay')\">Sales</button>\n      <button class=\"tab\" onclick=\"switchTab('sell')\">Sold</button>\n      <button class=\"tab\" onclick=\"switchTab('agents')\">Agents</button>"
new = "      <button class=\"tab\" onclick=\"switchTab('ebay')\">Sales</button>\n      <button class=\"tab\" onclick=\"switchTab('agents')\">Agents</button>"
if old in content:
    content = content.replace(old, new, 1)
    print("Tab button fixed")
else:
    print("Tab button not found")

# Fix tabs array
old2 = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','sell','agents'];"
new2 = "const tabs = ['add','invoice','foc','import','inventory','pc','bundles','update','ebay','agents'];"
if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Tabs array fixed")
else:
    print("Tabs array not found")

open('/Users/kylenelson/arc2-comics/index.html', 'w').write(content)
print("Done")