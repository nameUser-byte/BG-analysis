import re

html_path = '초기설정/AI_주제.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace dl-main text
html = html.replace('<span class="dl-main">A train</span>', '<span class="dl-main">A 학습용 데이터</span>')
html = html.replace('<span class="dl-main">A holdout</span>', '<span class="dl-main">A 검증용 입력</span>')
html = html.replace('<span class="dl-main">B train</span>', '<span class="dl-main">B 학습용 데이터</span>')
html = html.replace('<span class="dl-main">B holdout</span>', '<span class="dl-main">B 검증용 입력</span>')

# Replace small text for train
html = re.sub(r'<small>datasets/student/[^/]+/A/train\.csv</small>', '<small>CSV · 학습 및 Validation</small>', html)
html = re.sub(r'<small>datasets/student/[^/]+/B/train\.csv</small>', '<small>CSV · 학습 및 Validation</small>', html)

# Replace small text for holdout
html = re.sub(r'<small>datasets/student/[^/]+/A/holdout_features\.csv</small>', '<small>CSV · Label 없음</small>', html)
html = re.sub(r'<small>datasets/student/[^/]+/B/holdout_features\.csv</small>', '<small>CSV · Label 없음</small>', html)


def add_schema(match):
    prefix = match.group(1)
    original = match.group(0)
    
    new_link = f'''
            <a href="data/{prefix}_whole_schema.json" class="dl-link" download>
              <span class="dl-main">전체 데이터 사전</span>
              <small>JSON · feature/target 설명</small>
            </a>
          </div>'''
    
    return original.replace('          </div>', new_link)

pattern = re.compile(r'(<a href="data/([a-z0-9_]+)_B_holdout_features\.csv".*?</a>\s*</div>)', re.DOTALL)
new_html = pattern.sub(add_schema, html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Updated HTML successfully.")
