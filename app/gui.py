import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from settings_manager import SettingsManager
from zip_utils import ZipExtractor
from injector import AddonInjector
from addon_builder import AddonBuilder
from jar_fixer import JarFixer
from persistence import is_installed, install, uninstall, run_once_now as persistence_run_now

class LocalNameApp:
    def __init__(self):
        self.settings = SettingsManager()
        self.zip_extractor = ZipExtractor(callback=self.zip_callback)
        self.injector = AddonInjector(callback=self.inject_callback)
        self.builder = AddonBuilder(callback=self.build_callback)
        self.jar_fixer = JarFixer(callback=self.jar_callback)
        self.addon_base_dir = None
        self.worlds = []
        self.build_window()
        self.refresh_worlds()

    def build_window(self):
        self.root = tk.Tk()
        self.root.title("LocalName - Identity Hider for Minecraft Bedrock")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        style = ttk.Style()
        style.theme_use('vista' if 'vista' in style.theme_names() else 'clam')

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.enabled_var = tk.BooleanVar(value=self.settings.get('enabled', True))
        self.enabled_switch = ttk.Checkbutton(
            status_frame, text="Protection Active",
            variable=self.enabled_var,
            command=self.on_toggle_enabled
        )
        self.enabled_switch.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(header_frame, text="LocalName", font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="v1.0", font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.build_zip_tab()
        self.build_jar_tab()
        self.build_injector_tab()
        self.build_settings_tab()
        self.build_persistence_tab()

        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, variable=self.progress_var, mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.pack(fill=tk.X)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_zip_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="ZIP Extractor")

        ttk.Label(tab, text="ZIP Extractor", font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        file_frame = ttk.Frame(tab)
        file_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(file_frame, text="ZIP File:").pack(side=tk.LEFT)
        self.zip_path_var = tk.StringVar(value=self.settings.get('last_zip_path', ''))
        ttk.Entry(file_frame, textvariable=self.zip_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_zip).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Load", command=self.load_zip).pack(side=tk.LEFT, padx=(5, 0))

        dest_frame = ttk.Frame(tab)
        dest_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dest_frame, text="Extract To:").pack(side=tk.LEFT)
        self.zip_dest_var = tk.StringVar(value=self.settings.get('last_extract_path', ''))
        ttk.Entry(dest_frame, textvariable=self.zip_dest_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(dest_frame, text="Browse", command=self.browse_zip_dest).pack(side=tk.LEFT)
        ttk.Button(dest_frame, text="Extract", command=self.extract_zip).pack(side=tk.LEFT, padx=(5, 0))

        self.zip_contents = scrolledtext.ScrolledText(tab, height=12, font=('Consolas', 9))
        self.zip_contents.pack(fill=tk.BOTH, expand=True, pady=5)

    def build_jar_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="JAR/APK Fixer")

        ttk.Label(tab, text="JAR/APK Fixer", font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        file_frame = ttk.Frame(tab)
        file_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(file_frame, text="APK/JAR File:").pack(side=tk.LEFT)
        self.apk_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.apk_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_apk).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Analyze", command=self.analyze_apk).pack(side=tk.LEFT, padx=(5, 0))

        self.apk_info = scrolledtext.ScrolledText(tab, height=8, font=('Consolas', 9))
        self.apk_info.pack(fill=tk.X, pady=5)

        inject_frame = ttk.Frame(tab)
        inject_frame.pack(fill=tk.X, pady=5)

        ttk.Label(inject_frame, text="Inject Addon Into APK:").pack(anchor=tk.W)
        btn_frame = ttk.Frame(inject_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Browse Addon (.mcaddon)", command=self.browse_addon_for_apk).pack(side=tk.LEFT)
        self.apk_addon_path_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.apk_addon_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(btn_frame, text="Inject", command=self.inject_apk).pack(side=tk.LEFT)

        ttk.Separator(tab, orient='horizontal').pack(fill=tk.X, pady=10)
        build_frame = ttk.LabelFrame(tab, text="Zipper APK Builder", padding=10)
        build_frame.pack(fill=tk.X, pady=5)
        ttk.Label(build_frame, text="Build the Zipper Android APK (requires Android SDK):",
                  font=('Arial', 9)).pack(anchor=tk.W)
        btn_row = ttk.Frame(build_frame)
        btn_row.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row, text="Open Project Folder", command=self.open_android_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Build APK (via Gradle)", command=self.build_apk).pack(side=tk.LEFT, padx=2)
        self.apk_build_status = ttk.Label(build_frame, text="", font=('Arial', 8))
        self.apk_build_status.pack(anchor=tk.W)

    def build_injector_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="World Injector")

        ttk.Label(tab, text="Addon Injector - Injects LocalName into all Bedrock worlds",
                  font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(control_frame, text="Refresh Worlds", command=self.refresh_worlds).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Inject All", command=self.inject_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Remove All", command=self.remove_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Rebuild Addon", command=self.rebuild_addon).pack(side=tk.LEFT, padx=5)

        self.world_count_label = ttk.Label(control_frame, text="0 worlds found")
        self.world_count_label.pack(side=tk.RIGHT)

        columns = ('name', 'path', 'status')
        self.world_tree = ttk.Treeview(tab, columns=columns, show='headings', height=12)
        self.world_tree.heading('name', text='World Name')
        self.world_tree.heading('path', text='Path')
        self.world_tree.heading('status', text='LocalName')
        self.world_tree.column('name', width=200)
        self.world_tree.column('path', width=350)
        self.world_tree.column('status', width=100)

        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.world_tree.yview)
        self.world_tree.configure(yscrollcommand=scrollbar.set)

        self.world_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def build_settings_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Settings")

        ttk.Label(tab, text="Settings", font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        notebook_inner = ttk.Notebook(tab)
        notebook_inner.pack(fill=tk.BOTH, expand=True, pady=10)

        general_frame = ttk.Frame(notebook_inner, padding=10)
        notebook_inner.add(general_frame, text="General")

        self.chk_obfuscate = tk.BooleanVar(value=self.settings.get('obfuscate_name', True))
        ttk.Checkbutton(general_frame, text="Obfuscate player name",
                        variable=self.chk_obfuscate).pack(anchor=tk.W, pady=2)

        self.chk_black_avatar = tk.BooleanVar(value=self.settings.get('black_avatar', True))
        ttk.Checkbutton(general_frame, text="Replace avatar with pure black",
                        variable=self.chk_black_avatar).pack(anchor=tk.W, pady=2)

        self.chk_hide_cape = tk.BooleanVar(value=self.settings.get('hide_cape', True))
        ttk.Checkbutton(general_frame, text="Hide player cape",
                        variable=self.chk_hide_cape).pack(anchor=tk.W, pady=2)

        self.chk_auto = tk.BooleanVar(value=self.settings.get('auto_inject', False))
        ttk.Checkbutton(general_frame, text="Auto-inject into new worlds",
                        variable=self.chk_auto).pack(anchor=tk.W, pady=2)

        tag_frame = ttk.Frame(notebook_inner, padding=10)
        notebook_inner.add(tag_frame, text="Hide Tag")

        ttk.Label(tag_frame, text="Customize the hide tag format:").pack(anchor=tk.W)
        ttk.Label(tag_frame, text="Use Minecraft formatting codes: §0=black, §k=obfuscated, §8=dark gray",
                  font=('Arial', 8)).pack(anchor=tk.W)

        self.tag_var = tk.StringVar(value=self.settings.get('hide_tag_format', '§0§k'))
        tag_entry = ttk.Entry(tag_frame, textvariable=self.tag_var, font=('Consolas', 11), width=30)
        tag_entry.pack(anchor=tk.W, pady=5)

        preview_label = ttk.Label(tag_frame, text="Preview:")
        preview_label.pack(anchor=tk.W)
        self.tag_preview = tk.Text(tag_frame, height=3, width=40, font=('Consolas', 14))
        self.tag_preview.pack(anchor=tk.W, pady=5)
        self.update_tag_preview()

        def on_tag_change(*args):
            self.update_tag_preview()
        self.tag_var.trace_add('write', on_tag_change)

        ttk.Label(tag_frame, text="Common formats:\n§0§k - Black obfuscated (recommended)\n§8§k - Dark gray obfuscated\n§f§k - White obfuscated\n§7 - Light gray (no obfuscation)\n\nYou can also add text: §0§k[Hidden]",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=5)

        avatar_frame = ttk.Frame(notebook_inner, padding=10)
        notebook_inner.add(avatar_frame, text="Avatar")

        self.chk_custom_avatar = tk.BooleanVar(value=self.settings.get('custom_avatar_enabled', False))
        ttk.Checkbutton(avatar_frame, text="Use custom avatar texture",
                        variable=self.chk_custom_avatar).pack(anchor=tk.W, pady=2)

        ttk.Label(avatar_frame, text="Import a 64x64 PNG texture for the player avatar:").pack(anchor=tk.W, pady=5)

        avatar_file_frame = ttk.Frame(avatar_frame)
        avatar_file_frame.pack(fill=tk.X)

        self.avatar_path_var = tk.StringVar(value=self.settings.get('avatar_path', ''))
        ttk.Entry(avatar_file_frame, textvariable=self.avatar_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(avatar_file_frame, text="Browse", command=self.browse_avatar).pack(side=tk.LEFT, padx=5)

        ttk.Button(avatar_frame, text="Apply Texture", command=self.apply_avatar).pack(anchor=tk.W, pady=5)
        ttk.Label(avatar_frame, text="Tip: Extract a skin from a resource pack or\nuse a skin editor to create a 64x64 PNG.",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W)

        ttk.Frame(tab, height=20).pack()
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Rebuild & Apply", command=self.rebuild_and_apply).pack(side=tk.RIGHT)

    def update_tag_preview(self):
        self.tag_preview.delete('1.0', tk.END)
        self.tag_preview.insert('1.0', self.tag_var.get())

    def on_toggle_enabled(self):
        enabled = self.enabled_var.get()
        self.settings.set('enabled', enabled)
        status = "Active" if enabled else "Disabled"
        self.status_label.config(text=f"Protection {status}")
        if enabled:
            self.rebuild_addon()

    def browse_zip(self):
        path = filedialog.askopenfilename(
            title="Select ZIP file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if path:
            self.zip_path_var.set(path)
            self.settings.set('last_zip_path', path)
            self.load_zip()

    def browse_zip_dest(self):
        path = filedialog.askdirectory(title="Select extraction destination")
        if path:
            self.zip_dest_var.set(path)
            self.settings.set('last_extract_path', path)

    def load_zip(self):
        path = self.zip_path_var.get()
        if not path or not os.path.exists(path):
            self.zip_contents.delete('1.0', tk.END)
            self.zip_contents.insert('1.0', "File not found.")
            return
        self.zip_contents.delete('1.0', tk.END)
        contents = self.zip_extractor.get_contents(path)
        if isinstance(contents, str):
            self.zip_contents.insert('1.0', f"Error: {contents}")
            return
        total = len(contents)
        total_size = sum(s for _, s, _ in contents)
        self.zip_contents.insert('1.0', f"Total: {total} files, {total_size:,} bytes\n{'-'*50}\n")
        for name, size, csize in contents:
            self.zip_contents.insert(tk.END, f"{name:<60} {size:>8,} bytes\n")

    def extract_zip(self):
        zip_path = self.zip_path_var.get()
        dest_path = self.zip_dest_var.get()
        if not zip_path or not os.path.exists(zip_path):
            messagebox.showerror("Error", "Select a valid ZIP file")
            return
        if not dest_path:
            messagebox.showerror("Error", "Select a destination folder")
            return
        os.makedirs(dest_path, exist_ok=True)
        self.set_progress(0, "Extracting...")
        threading.Thread(target=self._extract_worker, args=(zip_path, dest_path), daemon=True).start()

    def _extract_worker(self, zip_path, dest_path):
        self.zip_extractor.extract(zip_path, dest_path)

    def zip_callback(self, status, current, total, message):
        if status == 'progress':
            pct = (current / total) * 100 if total > 0 else 0
            self.set_progress(pct, f"Extracting: {message}")
        elif status == 'done':
            self.set_progress(100, f"Extraction complete - {total} files")
        elif status == 'error':
            self.set_progress(0, f"Error: {message}")
        elif status == 'cancelled':
            self.set_progress(0, "Cancelled")

    def browse_apk(self):
        path = filedialog.askopenfilename(
            title="Select APK or JAR file",
            filetypes=[("APK files", "*.apk"), ("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if path:
            self.apk_path_var.set(path)

    def analyze_apk(self):
        path = self.apk_path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Select a valid APK/JAR file")
            return
        self.apk_info.delete('1.0', tk.END)
        self.apk_info.insert('1.0', "Analyzing...")
        threading.Thread(target=self._analyze_worker, args=(path,), daemon=True).start()

    def _analyze_worker(self, path):
        info = self.jar_fixer.analyze_apk(path)
        self.apk_info.delete('1.0', tk.END)
        if 'error' in info:
            self.apk_info.insert('1.0', f"Error: {info['error']}")
            return
        result = f"APK Analysis: {os.path.basename(path)}\n"
        result += f"{'='*50}\n"
        result += f"Total entries:     {info['total_entries']}\n"
        result += f"AndroidManifest:   {'Yes' if info['has_manifest'] else 'No'}\n"
        result += f"DEX files:         {info['dex_count']}\n"
        result += f"Library files:     {info['lib_count']}\n"
        result += f"Asset files:       {info['asset_count']}\n"
        result += f"Valid APK:         {'Yes' if info['is_valid_apk'] else 'No - may not be a valid APK'}\n"
        self.apk_info.insert('1.0', result)

    def browse_addon_for_apk(self):
        path = filedialog.askopenfilename(
            title="Select LocalName .mcaddon",
            filetypes=[("MCADDON files", "*.mcaddon"), ("All files", "*.*")]
        )
        if path:
            self.apk_addon_path_var.set(path)

    def inject_apk(self):
        apk_path = self.apk_path_var.get()
        addon_path = self.apk_addon_path_var.get()
        if not apk_path or not os.path.exists(apk_path):
            messagebox.showerror("Error", "Select a valid APK file")
            return
        if not addon_path or not os.path.exists(addon_path):
            messagebox.showerror("Error", "Select a valid .mcaddon file")
            return
        output_path = apk_path.replace('.apk', '_patched.apk')
        self.set_progress(0, "Injecting addon into APK...")
        threading.Thread(target=self._inject_apk_worker, args=(apk_path, output_path, addon_path), daemon=True).start()

    def _inject_apk_worker(self, apk_path, output_path, addon_path):
        self.jar_fixer.inject_into_apk(apk_path, output_path, addon_path)

    def jar_callback(self, status, current, total, message):
        if status == 'progress':
            pct = (current / total) * 100 if total > 0 else 0
            self.set_progress(pct, f"APK: {message}")
        elif status == 'done':
            self.set_progress(100, f"APK patched: {message}")
            messagebox.showinfo("Success", f"Patched APK saved to:\n{message}")
        elif status == 'error':
            self.set_progress(0, f"APK Error: {message}")

    def refresh_worlds(self):
        worlds_dir, self.worlds = self.injector.find_minecraft_worlds()
        for item in self.world_tree.get_children():
            self.world_tree.delete(item)
        if not self.worlds:
            self.world_count_label.config(text="0 worlds found")
            self.status_label.config(text="No Minecraft Bedrock worlds found.")
            return
        for world_path in self.worlds:
            name = self.injector.get_world_name(world_path)
            installed = self.injector.packs_installed(world_path)
            status_text = "Protected" if installed else "Unprotected"
            self.world_tree.insert('', tk.END, values=(name, world_path, status_text))
        self.world_count_label.config(text=f"{len(self.worlds)} worlds found")
        self.status_label.config(text=f"Found {len(self.worlds)} worlds")

    def inject_all(self):
        if not self.worlds:
            messagebox.showinfo("No Worlds", "No Minecraft worlds found.")
            return
        addon_paths = self.get_addon_paths()
        if not addon_paths:
            self.build_addon_files()
            addon_paths = self.get_addon_paths()
        if not addon_paths:
            messagebox.showerror("Error", "Could not build addon files.")
            return
        self.set_progress(0, "Injecting addon into all worlds...")
        def worker():
            self.injector.inject_all(self.worlds, addon_paths[0], addon_paths[1])
        threading.Thread(target=worker, daemon=True).start()

    def remove_all(self):
        if not self.worlds:
            return
        self.set_progress(0, "Removing addon from all worlds...")
        def worker():
            self.injector.remove_all(self.worlds)
        threading.Thread(target=worker, daemon=True).start()

    def rebuild_addon(self):
        self.build_addon_files()
        self.refresh_worlds()

    def get_addon_paths(self):
        base_dir = self.get_addon_base_dir()
        if not base_dir:
            return None
        bp_path = os.path.join(base_dir, 'addon', 'LocalName_BP')
        rp_path = os.path.join(base_dir, 'addon', 'LocalName_RP')
        if os.path.exists(bp_path) and os.path.exists(rp_path):
            return (bp_path, rp_path)
        return None

    def get_addon_base_dir(self):
        if self.addon_base_dir and os.path.exists(self.addon_base_dir):
            return self.addon_base_dir
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for d in [os.path.join(script_dir, '..'), os.path.join(script_dir, '..', 'addon')]:
            if os.path.exists(d):
                self.addon_base_dir = os.path.abspath(os.path.join(d))
                return self.addon_base_dir
        return None

    def build_addon_files(self):
        base_dir = self.get_addon_base_dir()
        if not base_dir:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.abspath(os.path.join(script_dir, '..'))
            self.addon_base_dir = base_dir

        output_path = os.path.join(base_dir, 'build', 'LocalName.mcaddon')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        avatar_path = self.avatar_path_var.get() if self.chk_custom_avatar.get() else None

        builder_settings = {
            'enabled': self.enabled_var.get(),
            'custom_avatar_enabled': self.chk_custom_avatar.get(),
            'hide_cape': self.chk_hide_cape.get()
        }

        hide_tag = self.tag_var.get()

        self.builder.build_custom_addon(output_path, hide_tag, avatar_path, builder_settings)
        return output_path

    def rebuild_and_apply(self):
        self.save_settings()
        output = self.build_addon_files()
        if output and self.worlds:
            self.set_progress(0, "Rebuilt addon. Re-injecting...")
            addon_paths = self.get_addon_paths()
            if addon_paths:
                threading.Thread(target=lambda: self.injector.inject_all(
                    self.worlds, addon_paths[0], addon_paths[1]), daemon=True).start()

    def inject_callback(self, status, current, total, message):
        if status == 'progress':
            pct = (current / total) * 100 if total > 0 else 0
            self.set_progress(pct, f"[{current}/{total}] {message}")
            self.refresh_worlds()
        elif status == 'done':
            self.set_progress(100, f"Done - {total} worlds updated")
            self.refresh_worlds()
            messagebox.showinfo("Complete", f"LocalName injected into {total} worlds!")
        elif status == 'cancelled':
            self.set_progress(0, "Cancelled")
        elif status == 'error':
            self.set_progress(0, f"Error: {message}")

    def build_callback(self, status, current, total, message):
        if status == 'done':
            self.set_progress(100, f"Addon built: {message}")
        else:
            self.set_progress(0, f"Building addon...")

    def browse_avatar(self):
        path = filedialog.askopenfilename(
            title="Select avatar texture (64x64 PNG)",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if path:
            self.avatar_path_var.set(path)

    def apply_avatar(self):
        path = self.avatar_path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Select a valid PNG file")
            return
        self.settings.set('avatar_path', path)
        self.settings.set('custom_avatar_enabled', True)
        self.chk_custom_avatar.set(True)
        messagebox.showinfo("Success", "Avatar texture set. Click 'Rebuild & Apply' to use it.")

    def save_settings(self):
        self.settings.set('enabled', self.enabled_var.get())
        self.settings.set('obfuscate_name', self.chk_obfuscate.get())
        self.settings.set('black_avatar', self.chk_black_avatar.get())
        self.settings.set('hide_cape', self.chk_hide_cape.get())
        self.settings.set('auto_inject', self.chk_auto.get())
        self.settings.set('hide_tag_format', self.tag_var.get())
        self.settings.set('avatar_path', self.avatar_path_var.get())
        self.settings.set('custom_avatar_enabled', self.chk_custom_avatar.get())
        messagebox.showinfo("Saved", "Settings saved successfully.")

    def reset_settings(self):
        self.settings.reset()
        self.enabled_var.set(self.settings.get('enabled', True))
        self.chk_obfuscate.set(self.settings.get('obfuscate_name', True))
        self.chk_black_avatar.set(self.settings.get('black_avatar', True))
        self.chk_hide_cape.set(self.settings.get('hide_cape', True))
        self.chk_auto.set(self.settings.get('auto_inject', False))
        self.tag_var.set(self.settings.get('hide_tag_format', '§0§k'))
        self.avatar_path_var.set(self.settings.get('avatar_path', ''))
        self.chk_custom_avatar.set(self.settings.get('custom_avatar_enabled', False))
        self.update_tag_preview()
        messagebox.showinfo("Reset", "Settings reset to defaults.")

    def build_persistence_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Persistence")

        ttk.Label(tab, text="Stealth Persistence", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(tab, text="Installs a hidden clone + daily scheduled task that re-injects\nthe addon into worlds if removed. Survives app uninstall.",
                  font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=5)

        status_frame = ttk.LabelFrame(tab, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=10)

        self.persist_status_var = tk.StringVar(value="Checking...")
        ttk.Label(status_frame, textvariable=self.persist_status_var,
                  font=('Arial', 10)).pack(anchor=tk.W)

        self.persist_detail_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.persist_detail_var,
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W)

        control_frame = ttk.LabelFrame(tab, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=10)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.persist_install_btn = ttk.Button(btn_frame, text="Install Persistence",
                                              command=self.install_persistence)
        self.persist_install_btn.pack(side=tk.LEFT, padx=5)

        self.persist_uninstall_btn = ttk.Button(btn_frame, text="Remove Persistence",
                                                command=self.uninstall_persistence)
        self.persist_uninstall_btn.pack(side=tk.LEFT, padx=5)

        self.persist_run_btn = ttk.Button(btn_frame, text="Run Check Now",
                                          command=self.run_persistence_check)
        self.persist_run_btn.pack(side=tk.LEFT, padx=5)

        info_frame = ttk.LabelFrame(tab, text="How it works", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        info_text = (
            "1. A hidden copy of the watchdog is placed in:\n"
            "   %APPDATA%\\LocalName\\\n\n"
            "2. A Windows Scheduled Task runs daily at midnight,\n"
            "   checking every Bedrock world for the addon.\n\n"
            "3. If a world is missing the addon, it's re-injected\n"
            "   automatically -- including the behavior pack JSON\n"
            "   and resource pack files.\n\n"
            "4. The directory is marked HIDDEN. The scheduled task\n"
            "   persists even if the main app is uninstalled.\n\n"
            "5. To fully remove: use 'Remove Persistence' above."
        )
        ttk.Label(info_frame, text=info_text, font=('Arial', 9),
                  justify=tk.LEFT).pack(anchor=tk.W)

        self.refresh_persistence_status()

    def refresh_persistence_status(self):
        try:
            installed = is_installed()
            if installed:
                self.persist_status_var.set("Active - Hidden clone + daily task installed")
                loc = os.path.expandvars('%APPDATA%\\LocalName')
                self.persist_detail_var.set(f"Location: {loc}  |  Task: LocalNameWatchdog")
                self.persist_install_btn.config(text="Reinstall Persistence")
            else:
                self.persist_status_var.set("Not installed")
                self.persist_detail_var.set("No hidden clone or scheduled task found")
                self.persist_install_btn.config(text="Install Persistence")
        except Exception:
            self.persist_status_var.set("Unknown (run from source?)")
            self.persist_detail_var.set("Build EXE first with build.ps1")

    def install_persistence(self):
        self.set_progress(0, "Installing persistence...")
        def worker():
            success, msg = install()
            if success:
                self.set_progress(100, "Persistence installed")
                self.refresh_persistence_status()
                messagebox.showinfo("Persistence", f"Hidden clone installed.\nDaily scheduled task created.\n{msg}")
            else:
                self.set_progress(0, f"Failed: {msg}")
                messagebox.showerror("Error", f"Install failed:\n{msg}")
        threading.Thread(target=worker, daemon=True).start()

    def uninstall_persistence(self):
        if not messagebox.askyesno("Confirm", "Remove persistence? The hidden clone and scheduled task will be deleted."):
            return
        self.set_progress(0, "Removing persistence...")
        def worker():
            success, msg = uninstall()
            self.set_progress(100 if success else 0, msg)
            self.refresh_persistence_status()
        threading.Thread(target=worker, daemon=True).start()

    def run_persistence_check(self):
        self.set_progress(0, "Running watchdog check...")
        def worker():
            success, msg = persistence_run_now()
            self.set_progress(100 if success else 0, msg)
        threading.Thread(target=worker, daemon=True).start()

    def open_android_project(self):
        android_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'android')
        if os.path.exists(android_dir):
            os.startfile(android_dir)
            self.apk_build_status.config(text=f"Opened: {android_dir}")
        else:
            messagebox.showerror("Error", "Android project not found")

    def build_apk(self):
        android_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'android')
        gradlew = os.path.join(android_dir, 'gradlew.bat')
        if not os.path.exists(gradlew):
            messagebox.showinfo("Gradle not found",
                "Gradle wrapper not found. Install Android SDK and open android/ in Android Studio to build.")
            return
        self.apk_build_status.config(text="Building APK (this may take a while)...")
        self.set_progress(0, "Building Zipper APK...")
        def worker():
            try:
                import subprocess
                result = subprocess.run(
                    [gradlew, 'assembleRelease'],
                    cwd=android_dir,
                    capture_output=True, text=True, timeout=600
                )
                apk_path = os.path.join(android_dir, 'app', 'build', 'outputs', 'apk', 'release', 'app-release.apk')
                build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build')
                os.makedirs(build_dir, exist_ok=True)
                dest = os.path.join(build_dir, 'Zipper.apk')
                if os.path.exists(apk_path):
                    import shutil
                    shutil.copy2(apk_path, dest)
                    self.set_progress(100, f"APK built: {dest}")
                    self.apk_build_status.config(text=f"APK: {dest}")
                else:
                    self.set_progress(0, "APK build failed")
                    self.apk_build_status.config(text=result.stdout[-500:] if result.stdout else "Build failed")
            except subprocess.TimeoutExpired:
                self.set_progress(0, "Build timed out")
                self.apk_build_status.config(text="Build timed out (10 min)")
            except Exception as e:
                self.set_progress(0, f"Error: {e}")
                self.apk_build_status.config(text=f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def set_progress(self, pct, text):
        self.progress_var.set(pct)
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def on_close(self):
        self.save_settings()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
