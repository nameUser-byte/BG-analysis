import re

with open('초기설정/AI_주제.html', 'r', encoding='utf-8') as f:
    html = f.read()

imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
print("Images:", imgs)

bg_urls = re.findall(r'url\([\'"]?([^\)]+?)[\'"]?\)', html)
print("CSS Background URLs:", bg_urls)
