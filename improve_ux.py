import re

html_path = '초기설정/AI_주제.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Restore personal titles
if '개인 정리본' not in html:
    html = re.sub(r'(<title>.*?)(</title>)', r'\1 · 개인 정리본\2', html)
    html = re.sub(r'(<div class="nav-brand">.*?)(</div>)', r'\1<span style="margin-left:6px; color:var(--text-faint);">· 개인 정리본</span>\2', html)

# 2. Restore the hero note
note_html = '<p class="hero-note" style="margin-top:20px; font-size:13px; color:var(--text-dim); background:var(--surface); padding:12px; border-radius:8px; border:1px solid var(--border);"><strong>안내</strong> · 이 페이지는 공식 교육과정이 아닌, 지원 준비생 대상 특강의 원본 내용을 바탕으로 본인이 학습 및 복습 용도로 데이터를 연동해 둔 개인 정리본입니다.</p>'

if '학습 및 복습 용도로' not in html:
    html = re.sub(r'(<div class="hero-meta">.*?</div>)', r'\1\n    ' + note_html, html, count=1, flags=re.DOTALL)

# 3. Add target="_blank" to external links
def external_link_fixer(match):
    href = match.group(1)
    tag = match.group(0)
    if href.startswith('http') and 'target=' not in tag:
        return tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
    return tag

html = re.sub(r'<a[^>]+href="([^"#]+)"[^>]*>', external_link_fixer, html)

# 4. Fix relative .html links (like preclass_setup.html)
base_url = 'https://waterfirst.github.io/semiconductor-ai-hackathon-bootcamp/'
def html_link_fixer(match):
    href = match.group(1)
    if not href.startswith('http') and href.endswith('.html'):
        new_href = base_url + href
        return match.group(0).replace(f'href="{href}"', f'href="{new_href}"')
    return match.group(0)

html = re.sub(r'<a[^>]+href="([^"#]+\.html)"[^>]*>', html_link_fixer, html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("UX improvements applied.")
