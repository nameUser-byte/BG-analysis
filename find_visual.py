import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(07 / VISUAL LANGUAGE.*?</section>)', html, re.DOTALL)
if m:
    print(m.group(1)[:500])
else:
    print("Not found")
