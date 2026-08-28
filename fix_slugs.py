import re

html_path = 'C:/Users/chan/Documents/temp_project/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the map inside the javascript
old_map = "'08_dram_cell':'dram','09_nand_vth':'3d_nand'"
new_map = "'08_dram':'dram','09_nand':'3d_nand'"

html = html.replace(old_map, new_map)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Slugs fixed.")
