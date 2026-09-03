import csv
import json
import os
import re

lep_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(lep_dir, 'lep - Sheet1.csv')

def get_initials(name):
    parts = re.split(r'\s+', name.strip())
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()

memorandum_data = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue
        name = row[0].strip()
        cat = row[1].strip().lower()
        msg = row[2].strip()
        if not name or not cat:
            continue
        
        name_lower = name.lower()
        media = None
        media_type = 'image'

        cat_dir = os.path.join(lep_dir, cat)
        if os.path.exists(cat_dir):
            for fname in os.listdir(cat_dir):
                f_base, f_ext = os.path.splitext(fname)
                if (f_base.lower() == name_lower or 
                    (name_lower == 'safana' and f_base.lower() == 'saffana') or 
                    (name_lower == 'raqiqa' and f_base.lower() == 'raqi')):
                    if f_ext.lower() in ['.jpg', '.jpeg', '.png']:
                        media = f'{cat}/{fname}'
                        media_type = 'image'
                        break
                    elif f_ext.lower() in ['.mp4', '.webm', '.mov']:
                        media = f'{cat}/{fname}'
                        media_type = 'video'
                        break

        memorandum_data.append({
            'name': name,
            'initials': get_initials(name),
            'message': msg,
            'category': cat,
            'media': media,
            'mediaType': media_type
        })

arc_dir = os.path.join(lep_dir, 'arc')
arc_files = [f for f in sorted(os.listdir(arc_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
arc_data = []
for idx, f in enumerate(arc_files):
    arc_data.append({
        'id': idx + 1,
        'file': f'arc/{f}'
    })

data_content = f'''// Auto-generated data file for Lepo (19th Birthday)
const memorandumData = {json.dumps(memorandum_data, indent=2, ensure_ascii=False)};
const arcData = {json.dumps(arc_data, indent=2, ensure_ascii=False)};
'''

with open(os.path.join(lep_dir, 'data.js'), 'w', encoding='utf-8') as f:
    f.write(data_content)

print(f'Done! Memo: {len(memorandum_data)}, Arc: {len(arc_data)}')
