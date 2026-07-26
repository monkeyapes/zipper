import subprocess
import os
import json
import tempfile
import shutil

def find_adb():
    possible = [
        'adb',
        os.path.expandvars('%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe'),
        os.path.expandvars('%ANDROID_HOME%\\platform-tools\\adb.exe'),
        'C:\\android\\sdk\\platform-tools\\adb.exe',
        os.path.expandvars('%LOCALAPPDATA%\\Android\\Sdk\\platform-tools\\adb.exe'),
        os.path.expandvars('%USERPROFILE%\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe'),
    ]
    for p in possible:
        expanded = os.path.expandvars(p)
        if os.path.exists(expanded):
            return expanded
    result = subprocess.run(['where', 'adb'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode == 0:
        return result.stdout.strip().split('\n')[0]
    return None

def get_devices(adb_path):
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True, timeout=5,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        lines = result.stdout.strip().split('\n')
        devices = []
        for line in lines[1:]:
            if line.strip() and 'device' in line and 'offline' not in line:
                devices.append(line.split('\t')[0])
        return devices
    except Exception:
        return []

def push_addon_files(adb_path, device_id, addon_dir):
    remote_bp = '/storage/emulated/0/games/com.mojang/behavior_packs/LocalName_BP'
    remote_rp = '/storage/emulated/0/games/com.mojang/resource_packs/LocalName_RP'

    bp_src = os.path.join(addon_dir, 'LocalName_BP')
    rp_src = os.path.join(addon_dir, 'LocalName_RP')

    if not os.path.exists(bp_src) or not os.path.exists(rp_src):
        return False, "Addon source directories not found"

    target = f'-s {device_id}' if device_id else ''
    cmds = [
        f'mkdir -p {remote_bp}/entities',
        f'mkdir -p {remote_rp}/entity',
        f'mkdir -p {remote_rp}/render_controllers',
        f'mkdir -p {remote_rp}/texts',
        f'mkdir -p {remote_rp}/textures/entity',
    ]
    for cmd in cmds:
        subprocess.run(f'adb {target} shell "{cmd}"', shell=True, capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)

    files_to_push = []
    for root, dirs, files in os.walk(bp_src):
        for f in files:
            local = os.path.join(root, f)
            rel = os.path.relpath(local, bp_src)
            remote = f'{remote_bp}/{rel}'
            files_to_push.append((local, remote))
    for root, dirs, files in os.walk(rp_src):
        for f in files:
            local = os.path.join(root, f)
            rel = os.path.relpath(local, rp_src)
            remote = f'{remote_rp}/{rel}'
            files_to_push.append((local, remote))

    for local, remote in files_to_push:
        subprocess.run(f'adb {target} push "{local}" "{remote}"', shell=True,
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    return True, f"Pushed {len(files_to_push)} files"

def send_live_update(adb_path, device_id, hide_tag='\u00a70\u00a7k'):
    target = f'-s {device_id}' if device_id else ''
    escaped_tag = hide_tag.replace('§', '\\\\(escaped)')
    cmd = f'adb {target} shell am broadcast -a com.localname.action.LIVE_UPDATE --es hide_tag "{hide_tag}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    return result.returncode == 0, result.stdout + result.stderr

def live_update(device_id=None, hide_tag='\u00a70\u00a7k', addon_base_dir=None):
    adb_path = find_adb()
    if not adb_path:
        return False, "ADB not found. Install Android SDK platform-tools."

    if not device_id:
        devices = get_devices(adb_path)
        if not devices:
            return False, "No Android devices connected via ADB."
        device_id = devices[0]

    if not addon_base_dir:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        addon_base_dir = os.path.abspath(os.path.join(script_dir, '..', 'addon'))

    ok, msg = push_addon_files(adb_path, device_id, addon_base_dir)
    if not ok:
        return False, msg

    ok, msg = send_live_update(adb_path, device_id, hide_tag)
    if ok:
        return True, f"Live update pushed to {device_id}"
    else:
        return False, f"Push OK but broadcast failed: {msg}"
