import glob
import json
import os
from PIL import Image, ImageStat, ImageFilter

# Load existing metadata
with open('assets/gartic_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# strip JS wrapper
json_str = content.replace('const garticArchiveData =', '').strip()
if json_str.endswith(';'):
    json_str = json_str[:-1].strip()

data = json.loads(json_str)

anime_titles = [
    "Anime Portrait with Stylized Hair",
    "Chibi Character Expression",
    "Vibrant Anime Figure & Gaze",
    "Whimsical Persona Gesture",
    "Manga Hero Concept Sketch",
    "Playful Cartoon Mascot",
    "Anime Dreamer in Motion",
    "Ecstatic Anime Face Reaction",
    "Curious Anime Companion",
    "Stylized Character Silhouette"
]

sketch_titles = [
    "Expressive Face Lineart",
    "Minimalist Comic Figure",
    "Hand-Drawn Character Doodle",
    "Quick Cartoon Gag Sketch",
    "Pencil Style Gesture Study",
    "Animated Facial Reaction",
    "Funny Caricature Illustration",
    "Playful Lineart Gag",
    "Speed Doodle Portrait",
    "Classic Comic Strip Character"
]

monster_titles = [
    "Shadow Beast Creature",
    "Dark Fantasy Monster",
    "Wild Night Horror Beast",
    "Creepy Smiling Cryptid",
    "Mythic Shadow Silhouette",
    "Abyssal Monster Sketch",
    "Chaos Goblin Character",
    "Eerie Gaze in the Shadows"
]

vivid_titles = [
    "Neon Purple Glow Figure",
    "Electric Dreamscape Motion",
    "Cyan & Magenta Palette Play",
    "Cosmic Cartoon Adventure",
    "Vivid Pop-Art Animation",
    "Midnight Blue Fantasy Sketch",
    "Psychedelic Motion Doodle",
    "Technicolor Creature Loop"
]

def analyze_and_title(idx, item, thumb_path):
    im = Image.open(thumb_path).convert('RGB')
    stat = ImageStat.Stat(im)
    r, g, b = stat.mean
    w, h = im.size
    total = w * h
    
    edges = sum(ImageStat.Stat(im.filter(ImageFilter.FIND_EDGES)).mean)
    
    colors = im.getcolors(maxcolors=150000) or []
    colors.sort(reverse=True)
    
    dark_px = sum(cnt for cnt, (cr,cg,cb) in colors if max(cr,cg,cb) < 65)
    white_px = sum(cnt for cnt, (cr,cg,cb) in colors if min(cr,cg,cb) > 230)
    blue_px = sum(cnt for cnt, (cr,cg,cb) in colors if cb > 140 and cr < 120 and cg < 150)
    purple_px = sum(cnt for cnt, (cr,cg,cb) in colors if cb > 130 and cr > 110 and cg < 110)
    pink_px = sum(cnt for cnt, (cr,cg,cb) in colors if cr > 180 and cg < 120 and cb > 120)
    green_px = sum(cnt for cnt, (cr,cg,cb) in colors if cg > 130 and cr < 120 and cb < 120)
    yellow_px = sum(cnt for cnt, (cr,cg,cb) in colors if cr > 170 and cg > 140 and cb < 80)
    red_px = sum(cnt for cnt, (cr,cg,cb) in colors if cr > 170 and cg < 80 and cb < 80)
    
    dark_ratio = dark_px / total
    white_ratio = white_px / total
    blue_ratio = blue_px / total
    purple_ratio = purple_px / total
    pink_ratio = pink_px / total
    
    tags = set(item.get('tags', ['drawing', 'gartic', 'album']))
    
    if dark_ratio > 0.35:
        base_title = monster_titles[idx % len(monster_titles)]
        tags.update(['monster', 'dark', 'eyes', 'creature', 'shadow', 'night'])
    elif white_ratio > 0.55:
        if pink_ratio > 0.08 or r > 210:
            base_title = anime_titles[idx % len(anime_titles)]
            tags.update(['anime', 'girl', 'hair', 'face', 'pink', 'smile', 'character'])
        else:
            base_title = sketch_titles[idx % len(sketch_titles)]
            tags.update(['sketch', 'face', 'character', 'lineart', 'portrait', 'funny'])
    elif purple_ratio > 0.12 or (b > 180 and r > 130):
        if edges > 75:
            base_title = anime_titles[idx % len(anime_titles)]
            tags.update(['anime', 'character', 'hair', 'purple', 'eyes', 'vibrant'])
        else:
            base_title = vivid_titles[idx % len(vivid_titles)]
            tags.update(['purple', 'violet', 'color', 'abstract', 'glow'])
    elif blue_ratio > 0.35 or b > 180:
        base_title = vivid_titles[idx % len(vivid_titles)]
        tags.update(['blue', 'water', 'cyan', 'cool', 'night'])
    else:
        base_title = sketch_titles[idx % len(sketch_titles)]
        tags.update(['drawing', 'character', 'funny', 'meme', 'animation'])
        
    return base_title, sorted(list(tags))

updated_data = []
for i, item in enumerate(data):
    thumb = item.get('thumbPath')
    if not os.path.exists(thumb):
        thumb = os.path.join('assets/gartic_thumbs', os.path.splitext(item['filename'])[0] + '.jpg')
    
    title, tags = analyze_and_title(i, item, thumb)
    item['title'] = title
    item['tags'] = tags
    updated_data.append(item)

output_js = "const garticArchiveData = " + json.dumps(updated_data, indent=2) + ";\n"
with open('assets/gartic_data.js', 'w', encoding='utf-8') as f:
    f.write(output_js)

print(f"Successfully processed and updated {len(updated_data)} items with visual analysis titles!")
