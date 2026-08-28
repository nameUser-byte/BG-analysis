import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'<section id="step6".*?</section>', html, re.DOTALL)
if m: print(m.group(0)[:500])
m = re.search(r'<section id="step7".*?</section>', html, re.DOTALL)
if m: print(m.group(0)[:500])
