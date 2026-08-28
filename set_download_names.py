import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Current HTML has: download (without value)
# We want to replace:
# href="data/..._A_train.csv" download -> href="data/..._A_train.csv" download="train.csv"
# href="data/..._A_holdout_features.csv" download -> href="data/..._A_holdout_features.csv" download="holdout.csv"
# href="data/..._B_train.csv" download -> href="data/..._B_train.csv" download="train.csv"
# href="data/..._B_holdout_features.csv" download -> href="data/..._B_holdout_features.csv" download="holdout.csv"
# href="data/..._whole_schema.json" download -> href="data/..._whole_schema.json" download="whole.json"

html = re.sub(r'href="([^"]+_A_train\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="train.csv"', html)
html = re.sub(r'href="([^"]+_A_holdout_features\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="holdout.csv"', html)
html = re.sub(r'href="([^"]+_B_train\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="train.csv"', html)
html = re.sub(r'href="([^"]+_B_holdout_features\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="holdout.csv"', html)
html = re.sub(r'href="([^"]+_whole_schema\.json)"\s*download(?:="[^"]*")?', r'href="\1" download="whole.json"', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# Also update the local original one to stay in sync
local_html = 'C:/Users/chan/Documents/semiconductor-ai-project/초기설정/AI_주제.html'
try:
    with open(local_html, 'r', encoding='utf-8') as f:
        local = f.read()
    
    local = re.sub(r'href="([^"]+_A_train\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="train.csv"', local)
    local = re.sub(r'href="([^"]+_A_holdout_features\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="holdout.csv"', local)
    local = re.sub(r'href="([^"]+_B_train\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="train.csv"', local)
    local = re.sub(r'href="([^"]+_B_holdout_features\.csv)"\s*download(?:="[^"]*")?', r'href="\1" download="holdout.csv"', local)
    local = re.sub(r'href="([^"]+_whole_schema\.json)"\s*download(?:="[^"]*")?', r'href="\1" download="whole.json"', local)

    with open(local_html, 'w', encoding='utf-8') as f:
        f.write(local)
except:
    pass

print("Download filenames updated successfully.")
