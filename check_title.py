import re

with open('초기설정/AI_주제.html', 'r', encoding='utf-8') as f:
    html = f.read()

t = re.search(r'<title>.*?</title>', html)
if t: print(t.group(0))
n = re.search(r'<div class="nav-brand">.*?</div>', html)
if n: print(n.group(0))
