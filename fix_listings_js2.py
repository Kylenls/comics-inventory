with open('/Users/kylenelson/arc2-comics/index.html', 'r') as f:
    content = f.read()

# Fix the button - use data attribute instead of passing safeKey in onclick
old_btn = """'<button onclick="lgenStageBundle(\\'' + safeKey + '\\')" data-key="' + g.key + '" data-series="' + g.series + '" data-issue="' + g.issue + '" data-cover="' + coverTotal.toFixed(2) + '" data-count="' + g.skus.length + '" data-variants="' + variants.join(',') + '" data-premium="' + hasRatio + '" class="btn btn-primary" style="font-size:12px;white-space:nowrap">+ Queue</button>' +"""

new_btn = """'<button onclick="lgenStageBundle(this)" data-key="' + g.key + '" data-series="' + g.series + '" data-issue="' + g.issue + '" data-cover="' + coverTotal.toFixed(2) + '" data-count="' + g.skus.length + '" data-variants="' + variants.join(',') + '" data-premium="' + hasRatio + '" class="btn btn-primary" style="font-size:12px;white-space:nowrap">+ Queue</button>' +"""

idx = content.find("lgenStageBundle(''")
if idx > 0:
    # Find the full button string
    btn_start = content.rfind("'<button onclick=", 0, idx)
    btn_end = content.find("+ Queue</button>' +", idx) + len("+ Queue</button>' +")
    old_exact = content[btn_start:btn_end]
    new_exact = """'<button onclick="lgenStageBundle(this)" data-key="' + g.key + '" data-series="' + g.series + '" data-issue="' + g.issue + '" data-cover="' + coverTotal.toFixed(2) + '" data-count="' + g.skus.length + '" data-variants="' + variants.join(',') + '" data-premium="' + hasRatio + '" class="btn btn-primary" style="font-size:12px;white-space:nowrap">+ Queue</button>' +"""
    content = content.replace(old_exact, new_exact, 1)
    print("Button fixed")
else:
    print("Button not found")

# Fix the function signature
old_fn = """function lgenStageBundle(safeKey) {
  const btn = document.querySelector('[onclick="lgenStageBundle(\\'' + safeKey + '\\')"]');
  if (!btn) return;"""

new_fn = """function lgenStageBundle(btn) {
  if (!btn) return;"""

if old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    print("Function signature fixed")
else:
    idx2 = content.find('function lgenStageBundle')
    end2 = content.find('\n  const series', idx2)
    old_exact2 = content[idx2:end2]
    new_fn2 = "function lgenStageBundle(btn) {\n  if (!btn) return;"
    content = content.replace(old_exact2, new_fn2, 1)
    print("Function signature fixed (alt)")

with open('/Users/kylenelson/arc2-comics/index.html', 'w') as f:
    f.write(content)