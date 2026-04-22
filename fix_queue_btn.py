with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

idx = content.find('agent2BuildDraftByKey')
# Find the button start
btn_start = content.rfind("'<button onclick=", 0, idx)
btn_end = content.find("</button>' +", idx) + len("</button>' +")
old_btn = content[btn_start:btn_end]
print("Found button:")
print(repr(old_btn))

new_btn = """'<button onclick="lgenQueueFromBundle(\\'' + safeKey + '\\')" style="width:100%;margin-top:4px;padding:8px;background:#198754;border:none;color:white;border-radius:8px;font-size:12px;font-weight:600;font-family:inherit;cursor:pointer">📋 Add to Listing Queue</button>' +
        """ + old_btn

content = content.replace(old_btn, new_btn, 1)
print("Button added")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)