import os
import glob
import struct
import zlib
from PIL import Image

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

class FastNBT:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read_byte(self):
        v = self.data[self.offset]
        self.offset += 1
        return v

    def read_short(self):
        v = struct.unpack_from('>h', self.data, self.offset)[0]
        self.offset += 2
        return v

    def read_int(self):
        v = struct.unpack_from('>i', self.data, self.offset)[0]
        self.offset += 4
        return v

    def read_long(self):
        v = struct.unpack_from('>q', self.data, self.offset)[0]
        self.offset += 8
        return v

    def read_float(self):
        v = struct.unpack_from('>f', self.data, self.offset)[0]
        self.offset += 4
        return v

    def read_double(self):
        v = struct.unpack_from('>d', self.data, self.offset)[0]
        self.offset += 8
        return v

    def read_string(self):
        l = struct.unpack_from('>H', self.data, self.offset)[0]
        self.offset += 2
        s = self.data[self.offset:self.offset+l].decode('utf-8', errors='ignore')
        self.offset += l
        return s

    def skip_payload(self, tag_type):
        if tag_type == TAG_BYTE: self.offset += 1
        elif tag_type == TAG_SHORT: self.offset += 2
        elif tag_type == TAG_INT: self.offset += 4
        elif tag_type == TAG_LONG: self.offset += 8
        elif tag_type == TAG_FLOAT: self.offset += 4
        elif tag_type == TAG_DOUBLE: self.offset += 8
        elif tag_type == TAG_BYTE_ARRAY:
            l = self.read_int()
            self.offset += l
        elif tag_type == TAG_STRING:
            l = struct.unpack_from('>H', self.data, self.offset)[0]
            self.offset += 2 + l
        elif tag_type == TAG_LIST:
            it = self.read_byte()
            l = self.read_int()
            for _ in range(l):
                self.skip_payload(it)
        elif tag_type == TAG_COMPOUND:
            while True:
                ct = self.read_byte()
                if ct == TAG_END: break
                l = struct.unpack_from('>H', self.data, self.offset)[0]
                self.offset += 2 + l
                self.skip_payload(ct)
        elif tag_type == TAG_INT_ARRAY:
            l = self.read_int()
            self.offset += l * 4
        elif tag_type == TAG_LONG_ARRAY:
            l = self.read_int()
            self.offset += l * 8

    def read_payload(self, tag_type):
        if tag_type == TAG_BYTE: return self.read_byte()
        if tag_type == TAG_SHORT: return self.read_short()
        if tag_type == TAG_INT: return self.read_int()
        if tag_type == TAG_LONG: return self.read_long()
        if tag_type == TAG_FLOAT: return self.read_float()
        if tag_type == TAG_DOUBLE: return self.read_double()
        if tag_type == TAG_BYTE_ARRAY:
            l = self.read_int()
            v = self.data[self.offset:self.offset+l]
            self.offset += l
            return v
        if tag_type == TAG_STRING: return self.read_string()
        if tag_type == TAG_LIST:
            it = self.read_byte()
            l = self.read_int()
            return [self.read_payload(it) for _ in range(l)]
        if tag_type == TAG_COMPOUND:
            res = {}
            while True:
                ct = self.read_byte()
                if ct == TAG_END: break
                cn = self.read_string()
                res[cn] = self.read_payload(ct)
            return res
        if tag_type == TAG_INT_ARRAY:
            l = self.read_int()
            v = struct.unpack_from(f'>{l}i', self.data, self.offset)
            self.offset += l*4
            return list(v)
        if tag_type == TAG_LONG_ARRAY:
            l = self.read_int()
            v = struct.unpack_from(f'>{l}q', self.data, self.offset)
            self.offset += l*8
            return list(v)
        return None

    def read_root(self):
        t = self.read_byte()
        if t == TAG_END: return None, None
        return self.read_string(), self.read_payload(t)

def unpack_heightmap(longs, bits_per_val=9):
    values = []
    mask = (1 << bits_per_val) - 1
    vals_per_long = 64 // bits_per_val
    for l in longs:
        u = l if l >= 0 else l + (1 << 64)
        for i in range(vals_per_long):
            if len(values) < 256:
                val = (u >> (i * bits_per_val)) & mask
                values.append(val - 64)
    return values

def get_terrain_color(surface_h, floor_h):
    # If surface > floor, surface is water
    water_depth = surface_h - floor_h
    if water_depth > 0:
        # Water
        if water_depth >= 8:
            return (28, 54, 120, 255) # Deep water
        elif water_depth >= 3:
            return (42, 85, 175, 255) # Ocean
        else:
            return (65, 125, 210, 255) # Shallow water / coast
            
    # Land elevation coloring
    h = surface_h
    if h <= 62:
        return (218, 198, 140, 255) # Beach / sand
    elif h <= 75:
        return (95, 155, 60, 255)   # Plains / lush lowlands
    elif h <= 95:
        return (70, 130, 48, 255)   # Dense forest / hills
    elif h <= 125:
        return (105, 115, 95, 255)  # Rocky foothills
    elif h <= 160:
        return (130, 130, 130, 255) # High mountain stone
    else:
        return (235, 240, 245, 255) # Snow peaks

def render_all_regions():
    region_dir = r"c:\Users\Last Final Day\Documents\GitHub\tools\nabil-shi\mcsimp\world\dimensions\minecraft\overworld\region"
    out_dir = r"c:\Users\Last Final Day\Documents\GitHub\tools\nabil-shi\mc-world-web"
    os.makedirs(out_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(region_dir, "r.*.*.mca"))
    print(f"Found {len(files)} region files.")
    
    # Calculate bounds
    rx_list, rz_list = [], []
    for f in files:
        b = os.path.basename(f).split('.')
        rx_list.append(int(b[1]))
        rz_list.append(int(b[2]))
        
    min_rx, max_rx = min(rx_list), max(rx_list)
    min_rz, max_rz = min(rz_list), max(rz_list)
    
    num_rx = max_rx - min_rx + 1
    num_rz = max_rz - min_rz + 1
    
    # Each region is 512x512 blocks.
    # We will render at 1 pixel per 2x2 blocks (scale 0.5) -> 256x256 pixels per region file.
    # Resulting image: (num_rx * 256) x (num_rz * 256)
    reg_w, reg_h = 256, 256
    total_w = num_rx * reg_w
    total_h = num_rz * reg_h
    
    print(f"Canvas size: {total_w} x {total_h} pixels ({num_rx} x {num_rz} regions)")
    world_img = Image.new("RGBA", (total_w, total_h), (8, 14, 26, 255))
    
    processed = 0
    for idx, f in enumerate(files):
        b = os.path.basename(f).split('.')
        rx, rz = int(b[1]), int(b[2])
        
        # Region image (256x256)
        # We will subsample 1 pixel per 2x2 blocks (each chunk 16x16 -> 8x8 pixels)
        reg_img = Image.new("RGBA", (reg_w, reg_h), (0, 0, 0, 0))
        reg_pixels = reg_img.load()
        
        file_size = os.path.getsize(f)
        if file_size < 8192:
            processed += 1
            continue
        with open(f, "rb") as fp:
            header = fp.read(4096)
            if len(header) < 4096:
                processed += 1
                continue
            for cz in range(32):
                for cx in range(32):
                    entry_idx = (cz * 32 + cx) * 4
                    loc = struct.unpack_from(">I", header, entry_idx)[0]
                    if loc == 0:
                        continue
                    offset = (loc >> 8) * 4096
                    if offset >= file_size or offset < 4096:
                        continue
                    fp.seek(offset)
                    len_bytes = fp.read(4)
                    if len(len_bytes) < 4:
                        continue
                    length = struct.unpack(">I", len_bytes)[0]
                    if length <= 1 or offset + 4 + length > file_size:
                        continue
                    scheme = ord(fp.read(1))
                    raw_chunk = fp.read(length - 1)
                    try:
                        decomp = zlib.decompress(raw_chunk)
                        reader = FastNBT(decomp)
                        _, cval = reader.read_root()
                        hm = cval.get("Heightmaps", {})
                        if "WORLD_SURFACE" in hm and "OCEAN_FLOOR" in hm:
                            ws = unpack_heightmap(hm["WORLD_SURFACE"])
                            of = unpack_heightmap(hm["OCEAN_FLOOR"])
                            
                            # Subsample 16x16 chunk into 8x8 pixels
                            for py in range(8):
                                for px in range(8):
                                    # Take sample block at (px*2, py*2)
                                    # in 16x16 chunk array: index is py*2 * 16 + px*2
                                    b_idx = (py * 2) * 16 + (px * 2)
                                    col = get_terrain_color(ws[b_idx], of[b_idx])
                                    reg_pixels[cx * 8 + px, cz * 8 + py] = col
                    except Exception:
                        pass
                        
        # Paste region into world canvas
        dest_x = (rx - min_rx) * reg_w
        dest_y = (rz - min_rz) * reg_h
        world_img.paste(reg_img, (dest_x, dest_y), reg_img)
        
        processed += 1
        if processed % 20 == 0 or processed == len(files):
            print(f"Processed {processed}/{len(files)} regions...")
            
    out_map_path = os.path.join(out_dir, "world_terrain_map.png")
    world_img.save(out_map_path, "PNG")
    print(f"Saved complete world map to: {out_map_path}")
    
    # Save coordinate calibration metadata
    import json
    meta = {
        "minX": min_rx * 512,
        "maxX": (max_rx + 1) * 512,
        "minZ": min_rz * 512,
        "maxZ": (max_rz + 1) * 512,
        "width": total_w,
        "height": total_h,
        "image": "world_terrain_map.png"
    }
    with open(os.path.join(out_dir, "world_terrain_meta.json"), "w") as fp:
        json.dump(meta, fp, indent=2)
    print("Metadata written:", meta)

if __name__ == "__main__":
    render_all_regions()
