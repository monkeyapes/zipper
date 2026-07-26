import json
import os

class SettingsManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'settings.json')
        self.config_path = config_path
        self.defaults = {
            'enabled': True,
            'hide_tag_format': '§0§k',
            'avatar_path': '',
            'auto_inject': False,
            'custom_avatar_enabled': False,
            'mc_worlds_path': '',
            'last_zip_path': '',
            'last_extract_path': '',
            'obfuscate_name': True,
            'black_avatar': True,
            'hide_cape': True
        }
        self.settings = dict(self.defaults)
        self.load()

    def load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    for k in self.defaults:
                        if k in loaded:
                            self.settings[k] = loaded[k]
        except Exception:
            self.settings = dict(self.defaults)

    def save(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception:
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def reset(self):
        self.settings = dict(self.defaults)
        self.save()
