import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Restore the exact names requested by user
# We want to replace:
# href="data/..._A_train.csv" download -> href="data/..._A_train.csv" download="train.csv"
# href="data/..._A_holdout_features.csv" download -> href="data/..._A_holdout_features.csv" download="holdout.csv"
# href="data/..._B_train.csv" download -> href="data/..._B_train.csv" download="train.csv"
# href="data/..._B_holdout_features.csv" download -> href="data/..._B_holdout_features.csv" download="holdout.csv"
# href="data/..._whole_schema.json" download -> href="data/..._whole_schema.json" download="whole.json"

html = re.sub(r'href="([^"]+_A_train\.csv)"\s*download', r'href="\1" download="train.csv"', html)
html = re.sub(r'href="([^"]+_A_holdout_features\.csv)"\s*download', r'href="\1" download="holdout.csv"', html)
html = re.sub(r'href="([^"]+_B_train\.csv)"\s*download', r'href="\1" download="train.csv"', html)
html = re.sub(r'href="([^"]+_B_holdout_features\.csv)"\s*download', r'href="\1" download="holdout.csv"', html)
html = re.sub(r'href="([^"]+_whole_schema\.json)"\s*download', r'href="\1" download="whole.json"', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Download filenames explicitly set again.")
