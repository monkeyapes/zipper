import os
import zipfile
import json
import shutil
import tempfile

class JarFixer:
    def __init__(self, callback=None):
        self.callback = callback
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def analyze_apk(self, apk_path):
        try:
            with zipfile.ZipFile(apk_path, 'r') as zf:
                info = zf.infolist()
                android_manifest = None
                dex_files = []
                lib_files = []
                asset_files = []
                for entry in info:
                    if entry.filename == 'AndroidManifest.xml':
                        android_manifest = entry
                    elif entry.filename.endswith('.dex'):
                        dex_files.append(entry.filename)
                    elif entry.filename.startswith('lib/'):
                        lib_files.append(entry.filename)
                    elif entry.filename.startswith('assets/'):
                        asset_files.append(entry.filename)
                return {
                    'total_entries': len(info),
                    'has_manifest': android_manifest is not None,
                    'dex_count': len(dex_files),
                    'lib_count': len(lib_files),
                    'asset_count': len(asset_files),
                    'is_valid_apk': android_manifest is not None and len(dex_files) > 0
                }
        except Exception as e:
            return {'error': str(e)}

    def inject_into_apk(self, apk_path, output_path, addon_path):
        self._cancel = False
        temp_dir = tempfile.mkdtemp()
        try:
            if self.callback:
                self.callback('progress', 0, 5, 'Extracting APK...')

            with zipfile.ZipFile(apk_path, 'r') as zf:
                zf.extractall(temp_dir)

            if self._cancel:
                return False

            if self.callback:
                self.callback('progress', 1, 5, 'Reading AndroidManifest...')

            manifest_path = os.path.join(temp_dir, 'AndroidManifest.xml')
            assets_addon_dir = os.path.join(temp_dir, 'assets', 'addons', 'LocalName')
            os.makedirs(assets_addon_dir, exist_ok=True)

            if self._cancel:
                return False

            if self.callback:
                self.callback('progress', 2, 5, 'Copying addon files...')

            if os.path.isdir(addon_path):
                for item in os.listdir(addon_path):
                    src = os.path.join(addon_path, item)
                    dst = os.path.join(assets_addon_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            elif os.path.isfile(addon_path):
                with zipfile.ZipFile(addon_path, 'r') as azf:
                    azf.extractall(assets_addon_dir)

            if self._cancel:
                return False

            if self.callback:
                self.callback('progress', 3, 5, 'Rebuilding APK...')

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, temp_dir)
                        zf.write(filepath, arcname)

            if self.callback:
                self.callback('done', 5, 5, output_path)
            return True

        except Exception as e:
            if self.callback:
                self.callback('error', 0, 0, str(e))
            return False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
