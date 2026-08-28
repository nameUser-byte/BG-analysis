import re

html_path = 'temp.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# We need to inject the prefix logic into renderTopic
# Original:
# function renderTopic(key){const t=topicData[key],base=`datasets/student/${t.slug}`;detail.innerHTML=`...
# We will replace `const t=topicData[key],base=`datasets/student/${t.slug}`;`
# with:
# `const t=topicData[key]; const prefixMap={'01_photo':'photo','02_overlay':'overlay','03_dry_etch':'dry_etch','04_har_etch':'har_etch','05_cmp':'cmp','06_deposition_apc':'depoistion','07_fdc':'fdc','08_dram_cell':'dram','09_nand_vth':'3d_nand','10_virtual_lot':'virtual'}; const p=prefixMap[t.slug];`

html = html.replace(
    'const t=topicData[key],base=`datasets/student/${t.slug}`;',
    "const t=topicData[key]; const prefixMap={'01_photo':'photo','02_overlay':'overlay','03_dry_etch':'dry_etch','04_har_etch':'har_etch','05_cmp':'cmp','06_deposition_apc':'depoistion','07_fdc':'fdc','08_dram_cell':'dram','09_nand_vth':'3d_nand','10_virtual_lot':'virtual'}; const p=prefixMap[t.slug];"
)

# Now we replace the download-grid HTML
# Original: <div class="download-grid"><a class="download-link" href="${base}/A/train.csv" download>...</a>...</div>
# We can just use a regex to replace the entire <div class="download-grid">...</div>
# inside the detail.innerHTML assignment.

new_grid = '''<div class="download-grid"><a class="download-link" href="data/${p}_A_train.csv" download>A 학습용 데이터<small>CSV · 모델 학습 및 자체 검증용</small></a><a class="download-link" href="data/${p}_A_holdout_features.csv" download>A 검증용 입력<small>CSV · 정답(label) 없음</small></a><a class="download-link" href="data/${p}_B_train.csv" download>B 학습용 데이터<small>CSV · 모델 학습 및 자체 검증용</small></a><a class="download-link" href="data/${p}_B_holdout_features.csv" download>B 검증용 입력<small>CSV · 정답(label) 없음</small></a><a class="download-link" href="data/${p}_whole_schema.json" download>전체 데이터 사전<small>JSON · feature/target 설명</small></a></div>'''

html = re.sub(r'<div class="download-grid">.*?</div>', new_grid, html)

with open('초기설정/AI_주제.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML completely replaced and customized successfully.")
