import json
import os
import sys
import shutil
import tempfile
import struct
import zlib
import zipfile
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR.endswith('app'):
    PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
else:
    PROJECT_DIR = BASE_DIR

HIDE_TAG = '\u00a70\u00a7k'
BP_UUID = 'a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a'
RP_UUID = 'c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f'

def create_png(width, height, r, g, b, a=255):
    def mc(ct, data):
        chunk = ct + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = mc(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            raw += struct.pack('BBBB', r, g, b, a)
    idat = mc(b'IDAT', zlib.compress(raw))
    iend = mc(b'IEND', b'')
    return sig + ihdr + idat + iend

def ensure_packs():
    bp_dir = os.path.join(PROJECT_DIR, 'addon', 'LocalName_BP')
    rp_dir = os.path.join(PROJECT_DIR, 'addon', 'LocalName_RP')
    if not os.path.exists(bp_dir) or not os.path.exists(rp_dir):
        rebuild_packs()
    return bp_dir, rp_dir

def rebuild_packs():
    bp_dir = os.path.join(PROJECT_DIR, 'addon', 'LocalName_BP')
    rp_dir = os.path.join(PROJECT_DIR, 'addon', 'LocalName_RP')
    os.makedirs(os.path.join(bp_dir, 'entities'), exist_ok=True)
    os.makedirs(os.path.join(rp_dir, 'entity'), exist_ok=True)
    os.makedirs(os.path.join(rp_dir, 'render_controllers'), exist_ok=True)
    os.makedirs(os.path.join(rp_dir, 'texts'), exist_ok=True)
    os.makedirs(os.path.join(rp_dir, 'textures', 'entity'), exist_ok=True)

    bp_manifest = {"format_version": 2, "header": {"name": "LocalName", "description": "Identity hider", "uuid": BP_UUID, "version": [1, 0, 0], "min_engine_version": [1, 132, 1]}, "modules": [{"type": "data", "uuid": "b8c9d4e3-2a5b-4f6e-8c7d-9e0f1a2b3c4d", "version": [1, 0, 0]}]}
    with open(os.path.join(bp_dir, 'manifest.json'), 'w') as f:
        json.dump(bp_manifest, f, indent=2)
    with open(os.path.join(bp_dir, 'pack_icon.png'), 'wb') as f:
        f.write(create_png(256, 256, 0, 0, 0))
    player_entity = {"format_version": "1.132.1", "minecraft:entity": {"description": {"identifier": "minecraft:player", "is_spawnable": False, "is_summonable": False, "is_experimental": False}, "components": {"minecraft:name_tag": {"value": HIDE_TAG}}}}
    with open(os.path.join(bp_dir, 'entities', 'player.json'), 'w') as f:
        json.dump(player_entity, f, indent=2)

    rp_manifest = {"format_version": 2, "header": {"name": "LocalName RP", "description": "Resource pack", "uuid": RP_UUID, "version": [1, 0, 0], "min_engine_version": [1, 132, 1]}, "modules": [{"type": "resources", "uuid": "d0e1f2a3-4b5c-6d7e-8f9a-0b1c2d3e4f5a", "version": [1, 0, 0]}]}
    with open(os.path.join(rp_dir, 'manifest.json'), 'w') as f:
        json.dump(rp_manifest, f, indent=2)
    with open(os.path.join(rp_dir, 'pack_icon.png'), 'wb') as f:
        f.write(create_png(256, 256, 0, 0, 0))
    client_entity = {"format_version": "1.10.0", "minecraft:client_entity": {"description": {"identifier": "minecraft:player", "materials": {"default": "entity_alphatest", "cape": "entity_alphatest", "animated": "player_animated"}, "textures": {"default": "textures/entity/black", "cape": "textures/entity/cape_invisible"}, "geometry": {"default": "geometry.humanoid.custom"}, "render_controllers": ["controller.render.player"], "enable_attachables": True}}}
    with open(os.path.join(rp_dir, 'entity', 'player.entity.json'), 'w') as f:
        json.dump(client_entity, f, indent=2)
    render_ctrl = {"format_version": "1.10.0", "render_controllers": {"controller.render.player": {"geometry": "geometry.default", "materials": [{"*": "material.default"}], "textures": ["texture.default"]}}}
    with open(os.path.join(rp_dir, 'render_controllers', 'player.render_controller.json'), 'w') as f:
        json.dump(render_ctrl, f, indent=2)
    with open(os.path.join(rp_dir, 'texts', 'en_US.lang'), 'w') as f:
        f.write("pack.name=LocalName RP\npack.description=Identity hider\n")
    with open(os.path.join(rp_dir, 'texts', 'languages.json'), 'w') as f:
        json.dump(["en_US"], f)
    with open(os.path.join(rp_dir, 'textures', 'entity', 'black.png'), 'wb') as f:
        f.write(create_png(64, 64, 0, 0, 0))
    with open(os.path.join(rp_dir, 'textures', 'entity', 'cape_invisible.png'), 'wb') as f:
        f.write(create_png(64, 32, 0, 0, 0, 0))

def find_minecraft_worlds():
    possible = [
        os.path.expandvars('%LOCALAPPDATA%\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'),
        os.path.expandvars('%USERPROFILE%\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'),
    ]
    for path in possible:
        expanded = os.path.expandvars(path)
        if os.path.exists(expanded):
            worlds = []
            try:
                for entry in os.listdir(expanded):
                    ep = os.path.join(expanded, entry)
                    if os.path.isdir(ep) and os.path.exists(os.path.join(ep, 'level.dat')):
                        worlds.append(ep)
            except Exception:
                pass
            if worlds:
                return worlds
    return []

def packs_installed(world_path):
    for fname in ['world_behavior_packs.json', 'world_resource_packs.json']:
        fp = os.path.join(world_path, fname)
        if not os.path.exists(fp):
            return False
    try:
        with open(os.path.join(world_path, 'world_behavior_packs.json')) as f:
            if not any(e.get('pack_id') == BP_UUID for e in json.load(f)):
                return False
        with open(os.path.join(world_path, 'world_resource_packs.json')) as f:
            if not any(e.get('pack_id') == RP_UUID for e in json.load(f)):
                return False
        return True
    except Exception:
        return False

def inject_world(world_path):
    bp_entry = {"pack_id": BP_UUID, "version": [1, 0, 0]}
    rp_entry = {"pack_id": RP_UUID, "version": [1, 0, 0]}
    try:
        bp_json = os.path.join(world_path, 'world_behavior_packs.json')
        if not os.path.exists(bp_json):
            with open(bp_json, 'w') as f:
                json.dump([bp_entry], f, indent=2)
        else:
            with open(bp_json, 'r') as f:
                data = json.load(f)
            if not any(e.get('pack_id') == BP_UUID for e in data):
                data.append(bp_entry)
                with open(bp_json, 'w') as f:
                    json.dump(data, f, indent=2)
        rp_json = os.path.join(world_path, 'world_resource_packs.json')
        if not os.path.exists(rp_json):
            with open(rp_json, 'w') as f:
                json.dump([rp_entry], f, indent=2)
        else:
            with open(rp_json, 'r') as f:
                data = json.load(f)
            if not any(e.get('pack_id') == RP_UUID for e in data):
                data.append(rp_entry)
                with open(rp_json, 'w') as f:
                    json.dump(data, f, indent=2)
        com_mojang = os.path.dirname(os.path.dirname(world_path))
        bp_dest = os.path.join(com_mojang, 'behavior_packs', 'LocalName_BP')
        rp_dest = os.path.join(com_mojang, 'resource_packs', 'LocalName_RP')
        bp_src, rp_src = ensure_packs()
        if os.path.exists(bp_src) and not os.path.exists(bp_dest):
            shutil.copytree(bp_src, bp_dest)
        if os.path.exists(rp_src) and not os.path.exists(rp_dest):
            shutil.copytree(rp_src, rp_dest)
        return True
    except Exception:
        return False

def run_check():
    worlds = find_minecraft_worlds()
    if not worlds:
        return
    for w in worlds:
        if not packs_installed(w):
            inject_world(w)

def run_loop(interval_hours=24):
    while True:
        try:
            run_check()
        except Exception:
            pass
        time.sleep(interval_hours * 3600)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_check()
    else:
        run_loop()
