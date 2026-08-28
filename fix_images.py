import re

html_path = '초기설정/AI_주제.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace assets/ and artifacts/ with absolute URLs from the target site
base_url = 'https://waterfirst.github.io/semiconductor-ai-hackathon-bootcamp/'

# We will use a function to add a comment before the image and fix the src
def replacer(match):
    original_src = match.group(1)
    new_src = base_url + original_src
    
    # Adding a helpful HTML comment above the image explaining its source
    comment = f"\n<!-- [이미지 설명] 이 이미지는 원본 교육 사이트({base_url})에서 동적으로 불러오는 자료입니다. 로컬에 파일이 없어도 깨지지 않도록 절대 경로로 수정되었습니다. -->\n"
    
    # Replace the src part in the original img tag
    fixed_img = match.group(0).replace(f'src="{original_src}"', f'src="{new_src}"')
    
    return comment + fixed_img

# Match <img ... src="assets/..." or <img ... src="artifacts/..."
html = re.sub(r'<img[^>]+src=["\'](assets/[^"\']+|artifacts/[^"\']+)["\']', replacer, html)

# Also check for og:image meta tags just in case
def meta_replacer(match):
    original_src = match.group(1)
    new_src = base_url + original_src
    return match.group(0).replace(f'content="{original_src}"', f'content="{new_src}"')

html = re.sub(r'<meta[^>]+property="og:image"[^>]+content=["\'](assets/[^"\']+)["\']', meta_replacer, html)


with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Images fixed and comments added successfully.")
