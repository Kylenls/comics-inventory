with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

old = 'id="panel-collage">\n\n    </div>\n\n  <div class="panel" id="panel-sell">'
new = 'id="panel-collage">\n    <div class="card"><p style="color:#6c757d;font-size:13px;padding:1rem">Collage builder coming soon.</p></div>\n  </div>\n\n  <div class="panel" id="panel-sell">'

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed")
else:
    print("Not found")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)