import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the explicit filenames from the download attribute so the browser uses the original file names from href
html = html.replace('download="train.csv"', 'download')
html = html.replace('download="holdout.csv"', 'download')
html = html.replace('download="whole.json"', 'download')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Removed custom download filenames.")
