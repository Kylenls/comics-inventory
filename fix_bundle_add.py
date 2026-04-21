with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix single search - use exact string from output
old_single = """'<button onclick="selectSingleListing(\\'' + JSON.stringify(r).replace(/"/g, "'") + '\\\')" class="btn btn-primary" style="font-size:11px;padding:4px 8px">Select</button>'"""
new_single = """'<button onclick="selectSingleListingByIdx(' + idx + ')" class="btn btn-primary" style="font-size:11px;padding:4px 8px">Select</button>'"""

if old_single in content:
    # Also change the map signature
    content = content.replace(
        "results.innerHTML = data.records.map(r =>\n    '<div style=\"display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0\">' +\n    '<span style=\"font-size:13px\">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +\n    " + old_single,
        "window._singleSearchResults = data.records;\n  results.innerHTML = data.records.map((r, idx) =>\n    '<div style=\"display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0f0\">' +\n    '<span style=\"font-size:13px\">' + (r.fields['Series'] || '') + ' #' + (r.fields['Issue'] || '') + ' ' + (r.fields['Variant'] || '') + '</span>' +\n    " + new_single,
        1
    )
    print("Single search fixed")
else:
    print("Not found - need exact content")
    idx = content.find('selectSingleListing(')
    print(repr(content[idx-200:idx+50]))

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)