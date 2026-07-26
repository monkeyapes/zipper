import os
import json
import shutil
import zipfile
import threading

class AddonInjector:
    def __init__(self, callback=None):
        self.callback = callback
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def find_minecraft_worlds(self):
        possible_paths = [
            os.path.expandvars('%LOCALAPPDATA%\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'),
            os.path.expandvars('%USERPROFILE%\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'),
            os.path.expandvars('%HOMEDRIVE%%HOMEPATH%\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'),
            'C:\\Users\\' + os.getlogin() + '\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds'
        ]
        for path in possible_paths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                try:
                    worlds = []
                    for entry in os.listdir(expanded):
                        entry_path = os.path.join(expanded, entry)
                        if os.path.isdir(entry_path):
                            level_dat = os.path.join(entry_path, 'level.dat')
                            if os.path.exists(level_dat):
                                worlds.append(entry_path)
                    if worlds:
                        return expanded, worlds
                except Exception:
                    pass
        return None, []

    def get_world_name(self, world_path):
        try:
            levelname_path = os.path.join(world_path, 'levelname.txt')
            if os.path.exists(levelname_path):
                with open(levelname_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            manifests_path = os.path.join(world_path, 'world_behavior_packs.json')
            if os.path.exists(manifests_path):
                return os.path.basename(world_path)
            return os.path.basename(world_path)
        except Exception:
            return os.path.basename(world_path)

    def packs_installed(self, world_path):
        bp_json_path = os.path.join(world_path, 'world_behavior_packs.json')
        rp_json_path = os.path.join(world_path, 'world_resource_packs.json')
        bp_installed = False
        rp_installed = False
        try:
            if os.path.exists(bp_json_path):
                with open(bp_json_path, 'r') as f:
                    data = json.load(f)
                    for entry in data:
                        if entry.get('pack_id') == 'a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a':
                            bp_installed = True
                            break
        except Exception:
            pass
        try:
            if os.path.exists(rp_json_path):
                with open(rp_json_path, 'r') as f:
                    data = json.load(f)
                    for entry in data:
                        if entry.get('pack_id') == 'c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f':
                            rp_installed = True
                            break
        except Exception:
            pass
        return bp_installed and rp_installed

    def inject_into_world(self, world_path, behavior_pack_path, resource_pack_path):
        try:
            bp_json_path = os.path.join(world_path, 'world_behavior_packs.json')
            rp_json_path = os.path.join(world_path, 'world_resource_packs.json')

            bp_entry = {
                "pack_id": "a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a",
                "version": [1, 0, 0]
            }
            rp_entry = {
                "pack_id": "c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f",
                "version": [1, 0, 0]
            }

            if not os.path.exists(bp_json_path):
                with open(bp_json_path, 'w') as f:
                    json.dump([bp_entry], f, indent=2)
            else:
                with open(bp_json_path, 'r') as f:
                    data = json.load(f)
                exists = any(e.get('pack_id') == 'a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a' for e in data)
                if not exists:
                    data.append(bp_entry)
                    with open(bp_json_path, 'w') as f:
                        json.dump(data, f, indent=2)

            if not os.path.exists(rp_json_path):
                with open(rp_json_path, 'w') as f:
                    json.dump([rp_entry], f, indent=2)
            else:
                with open(rp_json_path, 'r') as f:
                    data = json.load(f)
                exists = any(e.get('pack_id') == 'c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f' for e in data)
                if not exists:
                    data.append(rp_entry)
                    with open(rp_json_path, 'w') as f:
                        json.dump(data, f, indent=2)

            com_mojang = os.path.dirname(os.path.dirname(world_path))
            bp_dest = os.path.join(com_mojang, 'behavior_packs', 'LocalName_BP')
            rp_dest = os.path.join(com_mojang, 'resource_packs', 'LocalName_RP')

            if os.path.exists(behavior_pack_path) and not os.path.exists(bp_dest):
                shutil.copytree(behavior_pack_path, bp_dest)
            if os.path.exists(resource_pack_path) and not os.path.exists(rp_dest):
                shutil.copytree(resource_pack_path, rp_dest)

            return True
        except Exception:
            return False

    def remove_from_world(self, world_path):
        try:
            bp_json_path = os.path.join(world_path, 'world_behavior_packs.json')
            rp_json_path = os.path.join(world_path, 'world_resource_packs.json')

            bp_id = 'a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a'
            rp_id = 'c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f'

            if os.path.exists(bp_json_path):
                with open(bp_json_path, 'r') as f:
                    data = json.load(f)
                data = [e for e in data if e.get('pack_id') != bp_id]
                with open(bp_json_path, 'w') as f:
                    json.dump(data, f, indent=2)

            if os.path.exists(rp_json_path):
                with open(rp_json_path, 'r') as f:
                    data = json.load(f)
                data = [e for e in data if e.get('pack_id') != rp_id]
                with open(rp_json_path, 'w') as f:
                    json.dump(data, f, indent=2)

            return True
        except Exception:
            return False

    def inject_all(self, worlds, behavior_pack_path, resource_pack_path):
        self._cancel = False
        total = len(worlds)
        for i, world_path in enumerate(worlds):
            if self._cancel:
                if self.callback:
                    self.callback('cancelled', i, total, self.get_world_name(world_path))
                return False
            if self.callback:
                self.callback('progress', i + 1, total, self.get_world_name(world_path))
            self.inject_into_world(world_path, behavior_pack_path, resource_pack_path)
        if self.callback:
            self.callback('done', total, total, '')
        return True

    def remove_all(self, worlds):
        self._cancel = False
        total = len(worlds)
        for i, world_path in enumerate(worlds):
            if self._cancel:
                return False
            if self.callback:
                self.callback('progress', i + 1, total, self.get_world_name(world_path))
            self.remove_from_world(world_path)
        if self.callback:
            self.callback('done', total, total, '')
        return True
