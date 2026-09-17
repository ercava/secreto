import os
import gzip
import struct
from PIL import Image

BASE_MAP_COLORS = [
    (0, 0, 0, 0),        # 0: None / Transparent
    (127, 178, 56, 255),  # 1: Pale Green (Grass)
    (247, 233, 163, 255), # 2: Sand
    (199, 199, 199, 255), # 3: Cobweb
    (255, 0, 0, 255),     # 4: Lava / Red
    (160, 160, 255, 255), # 5: Ice / Pale Blue
    (167, 167, 167, 255), # 6: Iron
    (0, 124, 0, 255),     # 7: Leaves / Foliage
    (255, 255, 255, 255), # 8: White / Snow
    (164, 168, 184, 255), # 9: Clay
    (151, 109, 77, 255),  # 10: Dirt
    (112, 112, 112, 255), # 11: Stone
    (64, 64, 255, 255),   # 12: Water
    (143, 119, 72, 255),  # 13: Oak Wood
    (255, 252, 245, 255), # 14: Quartz
    (216, 127, 51, 255),  # 15: Orange
    (178, 76, 216, 255),  # 16: Magenta
    (102, 153, 216, 255), # 17: Light Blue
    (229, 229, 51, 255),  # 18: Yellow
    (127, 204, 25, 255),  # 19: Lime
    (242, 127, 165, 255), # 20: Pink
    (76, 76, 76, 255),    # 21: Gray
    (153, 153, 153, 255), # 22: Light Gray
    (76, 127, 153, 255),  # 23: Cyan
    (127, 63, 178, 255),  # 24: Purple
    (51, 76, 178, 255),   # 25: Blue
    (102, 76, 51, 255),   # 26: Brown
    (102, 127, 51, 255),  # 27: Dark Green
    (153, 51, 51, 255),   # 28: Red
    (25, 25, 25, 255),    # 29: Black
    (250, 238, 77, 255),  # 30: Gold
    (92, 219, 213, 255),  # 31: Diamond
    (74, 128, 255, 255),  # 32: Lapis
    (0, 217, 58, 255),    # 33: Emerald
    (129, 86, 49, 255),   # 34: Podzol
    (112, 2, 0, 255),     # 35: Netherrack
    (209, 177, 161, 255), # 36: White Terracotta
    (159, 82, 36, 255),   # 37: Orange Terracotta
    (149, 87, 108, 255),  # 38: Magenta Terracotta
    (112, 108, 138, 255), # 39: Light Blue Terracotta
    (186, 133, 36, 255),  # 40: Yellow Terracotta
    (103, 117, 53, 255),  # 41: Lime Terracotta
    (160, 77, 78, 255),   # 42: Pink Terracotta
    (57, 41, 35, 255),    # 43: Gray Terracotta
    (135, 107, 98, 255),  # 44: Light Gray Terracotta
    (87, 92, 92, 255),    # 45: Cyan Terracotta
    (122, 73, 88, 255),   # 46: Purple Terracotta
    (76, 62, 92, 255),    # 47: Blue Terracotta
    (76, 50, 35, 255),    # 48: Brown Terracotta
    (76, 82, 42, 255),    # 49: Green Terracotta
    (142, 60, 46, 255),   # 50: Red Terracotta
    (37, 22, 16, 255),    # 51: Black Terracotta
    (189, 48, 49, 255),   # 52: Crimson Nylium
    (148, 26, 29, 255),   # 53: Crimson Stem
    (94, 25, 29, 255),    # 54: Crimson Hyphae
    (22, 126, 134, 255),  # 55: Warped Nylium
    (58, 142, 140, 255),  # 56: Warped Stem
    (86, 44, 62, 255),    # 57: Warped Hyphae
    (20, 180, 133, 255),  # 58: Warped Wart
    (100, 100, 100, 255), # 59: Deepslate
    (216, 175, 147, 255), # 60: Raw Iron
    (127, 167, 150, 255), # 61: Glow Lichen
]

SHADE_MULTIPLIERS = [180/255.0, 220/255.0, 255/255.0, 135/255.0]

def get_minecraft_color(code):
    base_id = code // 4
    shade_id = code % 4
    if base_id == 0 or base_id >= len(BASE_MAP_COLORS):
        return (0, 0, 0, 0)
    r, g, b, a = BASE_MAP_COLORS[base_id]
    mult = SHADE_MULTIPLIERS[shade_id]
    return (int(r * mult), int(g * mult), int(b * mult), a)

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

class NBTReader:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read_byte(self):
        val = self.data[self.offset]
        self.offset += 1
        return val

    def read_short(self):
        val = struct.unpack_from('>h', self.data, self.offset)[0]
        self.offset += 2
        return val

    def read_int(self):
        val = struct.unpack_from('>i', self.data, self.offset)[0]
        self.offset += 4
        return val

    def read_long(self):
        val = struct.unpack_from('>q', self.data, self.offset)[0]
        self.offset += 8
        return val

    def read_float(self):
        val = struct.unpack_from('>f', self.data, self.offset)[0]
        self.offset += 4
        return val

    def read_double(self):
        val = struct.unpack_from('>d', self.data, self.offset)[0]
        self.offset += 8
        return val

    def read_string(self):
        length = struct.unpack_from('>H', self.data, self.offset)[0]
        self.offset += 2
        s = self.data[self.offset:self.offset+length].decode('utf-8', errors='ignore')
        self.offset += length
        return s

    def read_payload(self, tag_type):
        if tag_type == TAG_BYTE: return self.read_byte()
        if tag_type == TAG_SHORT: return self.read_short()
        if tag_type == TAG_INT: return self.read_int()
        if tag_type == TAG_LONG: return self.read_long()
        if tag_type == TAG_FLOAT: return self.read_float()
        if tag_type == TAG_DOUBLE: return self.read_double()
        if tag_type == TAG_BYTE_ARRAY:
            length = self.read_int()
            val = self.data[self.offset:self.offset+length]
            self.offset += length
            return val
        if tag_type == TAG_STRING: return self.read_string()
        if tag_type == TAG_LIST:
            item_type = self.read_byte()
            length = self.read_int()
            return [self.read_payload(item_type) for _ in range(length)]
        if tag_type == TAG_COMPOUND:
            res = {}
            while True:
                child_type = self.read_byte()
                if child_type == TAG_END: break
                child_name = self.read_string()
                res[child_name] = self.read_payload(child_type)
            return res
        if tag_type == TAG_INT_ARRAY:
            length = self.read_int()
            val = struct.unpack_from(f'>{length}i', self.data, self.offset)
            self.offset += length * 4
            return list(val)
        if tag_type == TAG_LONG_ARRAY:
            length = self.read_int()
            val = struct.unpack_from(f'>{length}q', self.data, self.offset)
            self.offset += length * 8
            return list(val)
        return None

    def read_root(self):
        tag_type = self.read_byte()
        if tag_type == TAG_END: return None, None
        name = self.read_string()
        return name, self.read_payload(tag_type)

def main():
    maps_dir = r"c:\Users\Last Final Day\Documents\GitHub\tools\nabil-shi\mcsimp\world\data\minecraft\maps"
    out_dir = r"c:\Users\Last Final Day\Documents\GitHub\tools\nabil-shi\mc-world-web\maps"
    os.makedirs(out_dir, exist_ok=True)
    
    import json
    metadata = []
    
    for i in range(7):
        p = os.path.join(maps_dir, f"{i}.dat")
        if not os.path.exists(p):
            continue
        with open(p, "rb") as fp:
            decomp = gzip.decompress(fp.read())
        reader = NBTReader(decomp)
        root_name, tag_val = reader.read_root()
        data = tag_val.get("data", tag_val) if isinstance(tag_val, dict) else {}
        
        colors = data.get("colors", b"")
        x_center = data.get("xCenter", 0)
        z_center = data.get("zCenter", 0)
        scale = data.get("scale", 0)
        dimension = data.get("dimension", "minecraft:overworld")
        
        # Render 128x128 image
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        pixels = []
        for b in colors:
            pixels.append(get_minecraft_color(b))
        
        if len(pixels) == 128 * 128:
            img.putdata(pixels)
            # Resize 4x with nearest-neighbor for sharp pixel art preview
            img_large = img.resize((512, 512), Image.Resampling.NEAREST)
            out_img = os.path.join(out_dir, f"map_{i}.png")
            out_large = os.path.join(out_dir, f"map_{i}_large.png")
            img.save(out_img)
            img_large.save(out_large)
            print(f"Generated map {i}: center=({x_center}, {z_center}), scale={scale}")
            
            metadata.append({
                "id": i,
                "xCenter": x_center,
                "zCenter": z_center,
                "scale": scale,
                "dimension": dimension,
                "image": f"maps/map_{i}.png",
                "imageLarge": f"maps/map_{i}_large.png"
            })
            
    with open(os.path.join(out_dir, "maps_meta.json"), "w") as fp:
        json.dump(metadata, fp, indent=2)
    print("Done rendering maps!")

if __name__ == "__main__":
    main()
