import os
import json
import shutil
import zipfile
import tempfile
import struct
import zlib

class AddonBuilder:
    def __init__(self, callback=None):
        self.callback = callback

    def _create_png(self, width, height, r, g, b, a=255):
        def make_chunk(chunk_type, data):
            chunk = chunk_type + data
            crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
            return struct.pack('>I', len(data)) + chunk + crc

        signature = b'\x89PNG\r\n\x1a\n'
        ihdr = make_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
        raw_data = b''
        for y in range(height):
            raw_data += b'\x00'
            for x in range(width):
                raw_data += struct.pack('BBBB', r, g, b, a)
        compressed = zlib.compress(raw_data)
        idat = make_chunk(b'IDAT', compressed)
        iend = make_chunk(b'IEND', b'')
        return signature + ihdr + idat + iend

    def build_custom_addon(self, output_path, hide_tag='§0§k', avatar_path=None, settings=None):
        if settings is None:
            settings = {}
        temp_dir = tempfile.mkdtemp()
        try:
            bp_dir = os.path.join(temp_dir, 'LocalName_BP')
            rp_dir = os.path.join(temp_dir, 'LocalName_RP')
            os.makedirs(os.path.join(bp_dir, 'entities'))
            os.makedirs(os.path.join(rp_dir, 'entity'))
            os.makedirs(os.path.join(rp_dir, 'render_controllers'))
            os.makedirs(os.path.join(rp_dir, 'texts'))
            os.makedirs(os.path.join(rp_dir, 'textures', 'entity'))

            bp_manifest = {
                "format_version": 2,
                "header": {
                    "name": "LocalName",
                    "description": "Hides player identity",
                    "uuid": "a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a",
                    "version": [1, 0, 0],
                    "min_engine_version": [1, 132, 1]
                },
                "modules": [{
                    "type": "data",
                    "uuid": "b8c9d4e3-2a5b-4f6e-8c7d-9e0f1a2b3c4d",
                    "version": [1, 0, 0]
                }]
            }
            with open(os.path.join(bp_dir, 'manifest.json'), 'w') as f:
                json.dump(bp_manifest, f, indent=2)
            with open(os.path.join(bp_dir, 'pack_icon.png'), 'wb') as f:
                f.write(self._create_png(256, 256, 0, 0, 0))

            player_entity = {
                "format_version": "1.132.1",
                "minecraft:entity": {
                    "description": {
                        "identifier": "minecraft:player",
                        "is_spawnable": False,
                        "is_summonable": False,
                        "is_experimental": False
                    },
                    "components": {
                        "minecraft:name_tag": {
                            "value": hide_tag if settings.get('enabled', True) else ""
                        }
                    }
                }
            }
            with open(os.path.join(bp_dir, 'entities', 'player.json'), 'w') as f:
                json.dump(player_entity, f, indent=2)

            rp_manifest = {
                "format_version": 2,
                "header": {
                    "name": "LocalName RP",
                    "description": "Resource pack for LocalName",
                    "uuid": "c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f",
                    "version": [1, 0, 0],
                    "min_engine_version": [1, 132, 1]
                },
                "modules": [{
                    "type": "resources",
                    "uuid": "d0e1f2a3-4b5c-6d7e-8f9a-0b1c2d3e4f5a",
                    "version": [1, 0, 0]
                }]
            }
            with open(os.path.join(rp_dir, 'manifest.json'), 'w') as f:
                json.dump(rp_manifest, f, indent=2)
            with open(os.path.join(rp_dir, 'pack_icon.png'), 'wb') as f:
                f.write(self._create_png(256, 256, 0, 0, 0))

            client_entity = {
                "format_version": "1.10.0",
                "minecraft:client_entity": {
                    "description": {
                        "identifier": "minecraft:player",
                        "materials": {
                            "default": "entity_alphatest",
                            "cape": "entity_alphatest",
                            "animated": "player_animated"
                        },
                        "textures": {
                            "default": "textures/entity/black",
                            "cape": "textures/entity/cape_invisible"
                        },
                        "geometry": {
                            "default": "geometry.humanoid.custom"
                        },
                        "render_controllers": ["controller.render.player"],
                        "enable_attachables": True
                    }
                }
            }
            with open(os.path.join(rp_dir, 'entity', 'player.entity.json'), 'w') as f:
                json.dump(client_entity, f, indent=2)

            render_ctrl = {
                "format_version": "1.10.0",
                "render_controllers": {
                    "controller.render.player": {
                        "geometry": "geometry.default",
                        "materials": [{"*": "material.default"}],
                        "textures": ["texture.default"]
                    }
                }
            }
            with open(os.path.join(rp_dir, 'render_controllers', 'player.render_controller.json'), 'w') as f:
                json.dump(render_ctrl, f, indent=2)

            with open(os.path.join(rp_dir, 'texts', 'en_US.lang'), 'w') as f:
                f.write("pack.name=LocalName RP\npack.description=Hidden identity\n")
            with open(os.path.join(rp_dir, 'texts', 'languages.json'), 'w') as f:
                json.dump(["en_US"], f)

            if avatar_path and os.path.exists(avatar_path) and settings.get('custom_avatar_enabled', False):
                shutil.copy2(avatar_path, os.path.join(rp_dir, 'textures', 'entity', 'black.png'))
            else:
                with open(os.path.join(rp_dir, 'textures', 'entity', 'black.png'), 'wb') as f:
                    f.write(self._create_png(64, 64, 0, 0, 0))

            if settings.get('hide_cape', True):
                with open(os.path.join(rp_dir, 'textures', 'entity', 'cape_invisible.png'), 'wb') as f:
                    f.write(self._create_png(64, 32, 0, 0, 0, 0))
            else:
                with open(os.path.join(rp_dir, 'textures', 'entity', 'cape_invisible.png'), 'wb') as f:
                    f.write(self._create_png(64, 32, 0, 0, 0))

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, temp_dir)
                        zf.write(filepath, arcname)

            if self.callback:
                self.callback('done', 1, 1, output_path)
            return output_path
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
