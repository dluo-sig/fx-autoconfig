#!/usr/bin/env python3
"""
fx-autoconfig GUI Installer
A cross-platform installer for Firefox userChrome.js manager
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import shutil
import json
import platform
import subprocess
import threading
from pathlib import Path
import webbrowser

VERSION = "1.0.0"
CONFIG_FILE = "installer_config.json"

class FxAutoconfigInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title(f"fx-autoconfig Installer v{VERSION}")
        self.root.geometry("750x750")
        
        # Load configuration
        self.config = self.load_config()
        # Variables
        self.firefox_path = tk.StringVar(value=self.config.get('firefox_path', ''))
        self.profile_path = tk.StringVar(value=self.config.get('profile_path', ''))
        self.custom_js_path = tk.StringVar(value=self.config.get('custom_js_path', ''))
        self.custom_css_path = tk.StringVar(value=self.config.get('custom_css_path', ''))
        self.use_symlinks = tk.BooleanVar(value=self.config.get('use_symlinks', False))
        
        self.setup_ui()
        self.center_window()
        
        # Validate repository root early
        self.validate_repository()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Installation")
        
        # Help tab
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="Help & Instructions")
        
        self.setup_main_tab(main_frame)
        self.setup_help_tab(help_frame)
        
    def setup_main_tab(self, parent):
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, text="fx-autoconfig Installer", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Simplify Firefox userChrome.js setup",
                                  font=('Arial', 10, 'italic'))
        subtitle_label.pack()
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Firefox installation path
        firefox_frame = ttk.LabelFrame(parent, text="Firefox Installation Directory", padding=10)
        firefox_frame.pack(fill=tk.X, padx=10, pady=5)
        
        firefox_entry_frame = ttk.Frame(firefox_frame)
        firefox_entry_frame.pack(fill=tk.X)
        
        self.firefox_entry = ttk.Entry(firefox_entry_frame, textvariable=self.firefox_path,
                                      font=('Arial', 10))
        self.firefox_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(firefox_entry_frame, text="Browse", 
                  command=self.browse_firefox_path).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(firefox_entry_frame, text="Auto-detect", 
                  command=self.detect_firefox_path).pack(side=tk.RIGHT)
        
        # Profile path
        profile_frame = ttk.LabelFrame(parent, text="Firefox Profile Directory", padding=10)
        profile_frame.pack(fill=tk.X, padx=10, pady=5)
        
        profile_entry_frame = ttk.Frame(profile_frame)
        profile_entry_frame.pack(fill=tk.X)
        
        self.profile_entry = ttk.Entry(profile_entry_frame, textvariable=self.profile_path,
                                      font=('Arial', 10))
        self.profile_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(profile_entry_frame, text="Browse", 
                  command=self.browse_profile_path).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(profile_entry_frame, text="Detect Profiles", 
                  command=self.detect_profiles).pack(side=tk.RIGHT)
          # Custom JS files path
        custom_js_frame = ttk.LabelFrame(parent, text="Custom Scripts Directory (Optional)", padding=10)
        custom_js_frame.pack(fill=tk.X, padx=10, pady=5)
        
        custom_js_entry_frame = ttk.Frame(custom_js_frame)
        custom_js_entry_frame.pack(fill=tk.X)
        
        self.custom_js_entry = ttk.Entry(custom_js_entry_frame, textvariable=self.custom_js_path,
                                        font=('Arial', 10))
        self.custom_js_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(custom_js_entry_frame, text="Browse", 
                  command=self.browse_custom_js_path).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(custom_js_entry_frame, text="Clear", 
                  command=self.clear_custom_js_path).pack(side=tk.RIGHT)
        
        # Info label for custom JS files
        info_js_label = ttk.Label(custom_js_frame, text="Scripts (.uc.js/.uc.mjs/.sys.mjs) will be copied/linked to chrome/JS/",
                                 font=('Arial', 9), foreground='gray')
        info_js_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Custom CSS files path
        custom_css_frame = ttk.LabelFrame(parent, text="Custom Styles Directory (Optional)", padding=10)
        custom_css_frame.pack(fill=tk.X, padx=10, pady=5)
        
        custom_css_entry_frame = ttk.Frame(custom_css_frame)
        custom_css_entry_frame.pack(fill=tk.X)
        
        self.custom_css_entry = ttk.Entry(custom_css_entry_frame, textvariable=self.custom_css_path,
                                         font=('Arial', 10))
        self.custom_css_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(custom_css_entry_frame, text="Browse", 
                  command=self.browse_custom_css_path).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(custom_css_entry_frame, text="Clear",                  command=self.clear_custom_css_path).pack(side=tk.RIGHT)
        
        # Info label for custom CSS files
        info_css_label = ttk.Label(custom_css_frame, text="Styles (.uc.css) will be copied/linked to chrome/CSS/, other files to chrome/resources/",
                                  font=('Arial', 9), foreground='gray')
        info_css_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Custom files options (applies to both JS and CSS)
        options_frame = ttk.LabelFrame(parent, text="Custom Files Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.symlink_check = ttk.Checkbutton(options_frame, text="Create symlinks instead of copying files (preserves live editing, applies to both scripts and styles)",
                                           variable=self.use_symlinks, command=self.save_config)
        self.symlink_check.pack(anchor=tk.W)
        
        # Action buttons
        action_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill=tk.X)
        
        self.install_btn = ttk.Button(button_frame, text="Install fx-autoconfig", 
                                     command=self.install_autoconfig)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.uninstall_btn = ttk.Button(button_frame, text="Uninstall fx-autoconfig", 
                                       command=self.uninstall_autoconfig)
        self.uninstall_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        button_frame2 = ttk.Frame(action_frame)
        button_frame2.pack(fill=tk.X, pady=(5, 0))
        
        self.clear_cache_btn = ttk.Button(button_frame2, text="Clear Startup Cache", 
                                         command=self.clear_startup_cache)
        self.clear_cache_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        self.open_profile_btn = ttk.Button(button_frame2, text="Open Profile Folder", 
                                          command=self.open_profile_folder)
        self.open_profile_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
          # Status
        status_frame = ttk.LabelFrame(parent, text="Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, 
                                                    font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("Ready. Please select Firefox installation and profile directories.")
    
    def setup_help_tab(self, parent):
        help_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=('Arial', 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load help content from README.md
        help_content = self.load_readme_content()
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def load_readme_content(self):
        """Load content from ui/README.md file"""
        try:
            # Get the directory where this script is located (ui folder)
            script_dir = Path(__file__).parent.absolute()
            readme_path = script_dir / "README.md"
            
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert basic markdown to plain text for better readability
                content = self.simple_markdown_to_text(content)
                
                # Add installer-specific note at the beginning
                installer_note = """fx-autoconfig GUI Installer Help

This help content is loaded from the installer's README.md file.
For complete documentation, visit: https://github.com/MrOtherGuy/fx-autoconfig

================================================================================

"""
                return installer_note + content
            else:
                return self.get_simple_help()
        except Exception as e:
            self.log_message(f"Could not load README.md: {e}", error=True)
            return self.get_simple_help()
    
    def get_simple_help(self):
        """Simple help when README cannot be loaded"""
        return """fx-autoconfig GUI Installer Help

Could not load the installer README.md file.

For complete installation instructions and documentation, please visit:
https://github.com/MrOtherGuy/fx-autoconfig

The installer provides an easy way to set up fx-autoconfig for Firefox userChrome.js scripting."""
        
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def load_config(self):
        try:
            config_path = Path(__file__).parent / CONFIG_FILE
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.log_message(f"Could not load config: {e}")
        return {}
        
    def save_config(self):
        try:
            config = {
                'firefox_path': self.firefox_path.get(),
                'profile_path': self.profile_path.get(),
                'custom_js_path': self.custom_js_path.get(),
                'custom_css_path': self.custom_css_path.get(),
                'use_symlinks': self.use_symlinks.get()
            }
            config_path = Path(__file__).parent / CONFIG_FILE
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log_message(f"Could not save config: {e}")
            
    def log_message(self, message, error=False):
        timestamp = ""  # Keep it simple for now
        prefix = "❌ " if error else "✅ "
        full_message = f"{prefix}{message}\n"
        
        self.status_text.insert(tk.END, full_message)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_firefox_path(self):
        path = filedialog.askdirectory(title="Select Firefox Installation Directory")
        if path:
            self.firefox_path.set(path)
            self.save_config()
            if self.is_valid_firefox_path(path):
                self.log_message(f"Firefox installation found: {path}")
            else:
                self.log_message(f"Warning: firefox executable not found in {path}", error=True)
                
    def browse_profile_path(self):
        path = filedialog.askdirectory(title="Select Firefox Profile Directory")
        if path:
            self.profile_path.set(path)
            self.save_config()
            if self.is_valid_profile_path(path):
                self.log_message(f"Firefox profile found: {path}")
            else:
                self.log_message(f"Warning: prefs.js not found in {path}", error=True)
                
    def browse_custom_js_path(self):
        path = filedialog.askdirectory(title="Select Custom Scripts Directory")
        if path:
            self.custom_js_path.set(path)
            self.save_config()
            self.log_message(f"Custom scripts directory selected: {path}")
            
    def clear_custom_js_path(self):
        self.custom_js_path.set("")
        self.save_config()
        self.log_message("Custom scripts directory cleared")
        
    def browse_custom_css_path(self):
        path = filedialog.askdirectory(title="Select Custom Styles Directory")
        if path:
            self.custom_css_path.set(path)
            self.save_config()
            self.log_message(f"Custom styles directory selected: {path}")
            
    def clear_custom_css_path(self):
        self.custom_css_path.set("")
        self.save_config()
        self.log_message("Custom styles directory cleared")
        
    def detect_firefox_path(self):
        paths = self.get_firefox_paths()
        
        for path in paths:
            if self.is_valid_firefox_path(path):
                self.firefox_path.set(path)
                self.save_config()
                self.log_message(f"Firefox installation detected: {path}")
                return                
        self.log_message("Could not auto-detect Firefox installation", error=True)
        
    def get_firefox_paths(self):
        system = platform.system()
        paths = []
        
        if system == "Windows":
            # Check common installation directories
            search_dirs = [
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                os.environ.get('LOCALAPPDATA', ''),
            ]
            
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    try:
                        for item in os.listdir(search_dir):
                            if "firefox" in item.lower():
                                full_path = os.path.join(search_dir, item)
                                if os.path.isdir(full_path):
                                    paths.append(full_path)
                    except (PermissionError, OSError):
                        continue
                        
        elif system == "Darwin":  # macOS
            # Check Applications directory
            apps_dir = "/Applications"
            if os.path.exists(apps_dir):
                try:
                    for item in os.listdir(apps_dir):
                        if "firefox" in item.lower() and item.endswith(".app"):
                            app_path = os.path.join(apps_dir, item, "Contents", "MacOS")
                            if os.path.exists(app_path):
                                paths.append(app_path)
                except (PermissionError, OSError):
                    pass
                    
        elif system == "Linux":
            # Check common Linux installation directories
            search_dirs = [
                "/usr/lib",
                "/usr/lib64", 
                "/opt",
                "/snap",
                "/usr/bin",
            ]
            
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    try:
                        for item in os.listdir(search_dir):
                            if "firefox" in item.lower():
                                full_path = os.path.join(search_dir, item)
                                if os.path.isdir(full_path):
                                    # For snap, check if it's the current version
                                    if "snap" in search_dir and "firefox" in item:
                                        current_path = os.path.join(full_path, "current")
                                        if os.path.exists(current_path):
                                            paths.append(current_path)
                                        else:
                                            paths.append(full_path)
                                    else:
                                        paths.append(full_path)
                    except (PermissionError, OSError):
                        continue
            
        # Remove duplicates and return only valid Firefox paths
        unique_paths = []
        for path in paths:
            if path not in unique_paths and self.is_valid_firefox_path(path):
                unique_paths.append(path)
                
        return unique_paths
        
    def is_valid_firefox_path(self, path):
        executable = "firefox.exe" if platform.system() == "Windows" else "firefox"
        return os.path.exists(os.path.join(path, executable))
        
    def detect_profiles(self):
        profiles = self.get_profile_paths()
        
        if not profiles:
            self.log_message("No Firefox profiles found", error=True)
            return
            
        if len(profiles) == 1:
            self.profile_path.set(profiles[0])
            self.save_config()
            self.log_message(f"Profile selected: {os.path.basename(profiles[0])}")
            return
            
        # Multiple profiles - show selection dialog
        self.show_profile_selector(profiles)
        
    def get_profile_paths(self):
        system = platform.system()
        
        if system == "Windows":
            profiles_dir = os.path.join(os.environ.get('APPDATA', ''), 
                                       "Mozilla", "Firefox", "Profiles")
        elif system == "Darwin":  # macOS
            profiles_dir = os.path.expanduser(
                "~/Library/Application Support/Firefox/Profiles")
        elif system == "Linux":
            profiles_dir = os.path.expanduser("~/.mozilla/firefox")
        else:
            return []
            
        profiles = []
        if os.path.exists(profiles_dir):
            for item in os.listdir(profiles_dir):
                profile_path = os.path.join(profiles_dir, item)
                if os.path.isdir(profile_path) and self.is_valid_profile_path(profile_path):
                    profiles.append(profile_path)
                    
        return profiles
        
    def is_valid_profile_path(self, path):
        return os.path.exists(os.path.join(path, "prefs.js"))
        
    def show_profile_selector(self, profiles):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Firefox Profile")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a Firefox profile:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=('Arial', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for profile in profiles:
            display_name = f"{os.path.basename(profile)} ({profile})"
            listbox.insert(tk.END, display_name)
            
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_profile = profiles[selection[0]]
                self.profile_path.set(selected_profile)
                self.save_config()
                self.log_message(f"Profile selected: {os.path.basename(selected_profile)}")
                dialog.destroy()
                
        def on_cancel():
            dialog.destroy()
            
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
    def validate_paths(self):
        if not self.firefox_path.get():
            self.log_message("Please select Firefox installation directory", error=True)
            return False
        
        if not self.profile_path.get():
            self.log_message("Please select Firefox profile directory", error=True)
            return False
        
        if not self.is_valid_firefox_path(self.firefox_path.get()):
            self.log_message("Invalid Firefox installation directory", error=True)
            return False
        
        if not self.is_valid_profile_path(self.profile_path.get()):
            self.log_message("Invalid Firefox profile directory", error=True)
            return False
        
        return True
    
    def install_autoconfig(self):
        if not self.validate_paths():
            return
        
        # Check if we need elevation for Windows Program Files installation
        firefox_path = self.firefox_path.get()
        if platform.system() == "Windows" and self.needs_elevation(firefox_path) and not self.is_admin():
            result = messagebox.askyesno(
                "Administrator Privileges Required",
                f"Firefox is installed in:\n{firefox_path}\n\n"
                "This location requires administrator privileges to modify.\n"
                "Would you like to restart the installer with elevated privileges?\n\n"
                "Click 'Yes' to restart as administrator, or 'No' to continue (may fail).",
                icon='question'
            )
            
            if result:
                self.log_message("Requesting elevated privileges...")
                if self.request_elevation():
                    self.log_message("Restarting with elevated privileges...")
                    self.root.quit()  # Close current instance
                    return
                else:
                    self.log_message("Failed to request elevation, continuing anyway...", error=True)
            else:
                self.log_message("Continuing without elevation (installation may fail)...", error=True)
            
        def install_thread():
            try:
                self.log_message("Starting fx-autoconfig installation...")
                  # Install program files
                self.install_program_files()
                self.log_message("Program files installed successfully")
                
                # Install profile files
                self.install_profile_files()
                self.log_message("Profile files installed successfully")
                
                # Copy/link custom files if specified
                if self.custom_js_path.get() or self.custom_css_path.get():
                    self.install_custom_files()
                    self.log_message("Custom files processed successfully")
                
                self.log_message("fx-autoconfig installed successfully!")
                self.log_message("IMPORTANT: Clear startup cache and restart Firefox to complete installation")
                
            except Exception as e:
                self.log_message(f"Installation failed: {str(e)}", error=True)
                
        # Run installation in separate thread to prevent UI freezing
        threading.Thread(target=install_thread, daemon=True).start()
        
    def install_program_files(self):
        firefox_path = self.firefox_path.get()
        
        # Get repository root directory
        repo_root = self.get_repo_root()
        program_src = os.path.join(repo_root, "program")
        
        if not os.path.exists(program_src):
            raise FileNotFoundError(f"Could not find program directory at {program_src}")
        
        # On macOS, files should go to Contents/Resources/, not Contents/MacOS/
        # According to README: "Copy defaults/ and config.js to /Applications/Firefox.app/Contents/Resources/"        if platform.system() == "Darwin" and firefox_path.endswith("MacOS"):
            # Convert MacOS path to Resources path
            firefox_path = firefox_path.replace("MacOS", "Resources")
        
        # Copy the contents of the program directory (not the directory itself)
        # This follows the manual installation instructions from the README
        self.copy_directory(program_src, firefox_path)
    
    def install_profile_files(self):
        """Copy fx-autoconfig profile files from repository to Firefox profile"""
        profile_path = self.profile_path.get()
        chrome_dir = os.path.join(profile_path, "chrome")
        
        # Get repository root directory
        repo_root = self.get_repo_root()
        if not repo_root:
            raise Exception("Could not find fx-autoconfig repository root")
            
        profile_src = os.path.join(repo_root, "profile", "chrome")
        if not os.path.exists(profile_src):
            raise Exception(f"Profile source directory not found: {profile_src}")
        
        # Copy the contents of the profile/chrome directory (not the directory itself)
        # This follows the manual installation instructions from the README
        self.log_message(f"Copying fx-autoconfig profile files from: {profile_src}")
        self.copy_directory(profile_src, chrome_dir)
        
    def get_repo_root(self):
        # Start from the directory containing this script
        current_dir = Path(__file__).parent.absolute()
        
        # Look for program and profile directories to identify repository root
        for i in range(10):  # Limit search depth
            program_path = current_dir / "program"
            profile_path = current_dir / "profile"
            if program_path.exists() and profile_path.exists():
                return str(current_dir)
                
            parent = current_dir.parent
            if parent == current_dir:
                break  # Reached filesystem root
            current_dir = parent
            
        # Try fallback: assume we're in ui directory
        fallback = Path(__file__).parent.parent
        program_path = fallback / "program"
        profile_path = fallback / "profile"
        if program_path.exists() and profile_path.exists():
            return str(fallback)
            
        # Repository root not found
        return None
        
    def copy_directory(self, src, dst):
        for root, dirs, files in os.walk(src):
            # Calculate relative path
            rel_path = os.path.relpath(root, src)
            
            # Create destination directory
            if rel_path != '.':
                dst_dir = os.path.join(dst, rel_path)
            else:
                dst_dir = dst
            os.makedirs(dst_dir, exist_ok=True)
              # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_dir, file)
                shutil.copy2(src_file, dst_file)

    def install_custom_files(self):
        """Copy or symlink custom files from user-specified directories"""
        profile_path = self.profile_path.get()
        chrome_dir = os.path.join(profile_path, "chrome")
        js_dir = os.path.join(chrome_dir, "JS")
        css_dir = os.path.join(chrome_dir, "CSS")
        
        use_symlinks = self.use_symlinks.get()
        
        # Check if symlinks are supported if user wants to use them
        if use_symlinks and not self.can_create_symlinks():
            self.log_message("Warning: Symlinks not supported on this system, copying files instead")
            use_symlinks = False
        
        # Process JS files directory - copy all contents to chrome/JS/
        custom_js_path = self.custom_js_path.get()
        if custom_js_path and os.path.exists(custom_js_path):
            self.log_message(f"Processing scripts from: {custom_js_path}")
            self._process_custom_directory(custom_js_path, js_dir, use_symlinks, 'scripts')
          # Process CSS files directory - copy all contents to chrome/CSS/
        custom_css_path = self.custom_css_path.get()
        if custom_css_path and os.path.exists(custom_css_path):
            self.log_message(f"Processing styles from: {custom_css_path}")
            self._process_custom_directory(custom_css_path, css_dir, use_symlinks, 'styles')
    
    def _process_custom_directory(self, src_dir, dst_dir, use_symlinks, file_type):
        """Helper method to copy all contents from a custom directory to destination"""
        for root, dirs, files in os.walk(src_dir):
            # Calculate relative path from source directory
            rel_path = os.path.relpath(root, src_dir)
            
            # Create corresponding directory structure in destination
            if rel_path == '.':
                target_dir = dst_dir
            else:
                target_dir = os.path.join(dst_dir, rel_path)
            
            os.makedirs(target_dir, exist_ok=True)
            
            # Process all files in this directory
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                
                # Remove existing file/link if it exists
                if os.path.exists(dst_file) or os.path.islink(dst_file):
                    if os.path.islink(dst_file):
                        os.unlink(dst_file)
                    else:
                        os.remove(dst_file)
                
                # Create symlink or copy file
                try:
                    if use_symlinks:
                        os.symlink(src_file, dst_file)
                        self.log_message(f"Symlinked {file_type}: {file}")
                    else:
                        shutil.copy2(src_file, dst_file)
                        self.log_message(f"Copied {file_type}: {file}")
                except Exception as e:
                    self.log_message(f"Failed to process {file}: {e}", error=True)
                
    def uninstall_autoconfig(self):
        if not self.validate_paths():
            return
          # Create custom dialog for uninstall options
        dialog = tk.Toplevel(self.root)
        dialog.title("Uninstall Options")
        dialog.geometry("550x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Choose Uninstall Option", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Option selection
        uninstall_option = tk.StringVar(value="partial")
        
        # Partial uninstall option
        partial_frame = ttk.Frame(main_frame)
        partial_frame.pack(fill=tk.X, pady=5)
        
        partial_radio = ttk.Radiobutton(partial_frame, text="Partial Uninstall (Recommended)", 
                                       variable=uninstall_option, value="partial")
        partial_radio.pack(anchor=tk.W)
        
        partial_desc = ttk.Label(partial_frame, 
                                text="• Removes fx-autoconfig system files\n"
                                     "• Preserves your custom scripts and styles\n"
                                     "• You can reinstall fx-autoconfig later", 
                                font=('Arial', 9), foreground='gray')
        partial_desc.pack(anchor=tk.W, padx=20, pady=(2, 10))
        
        # Complete uninstall option
        complete_frame = ttk.Frame(main_frame)
        complete_frame.pack(fill=tk.X, pady=5)
        
        complete_radio = ttk.Radiobutton(complete_frame, text="Complete Uninstall", 
                                        variable=uninstall_option, value="complete")
        complete_radio.pack(anchor=tk.W)
        
        complete_desc = ttk.Label(complete_frame,
                                 text="• Removes fx-autoconfig system files\n"
                                      "• Removes CSS/ and JS/ directories completely\n"
                                      "• Removes fx-autoconfig files (utils/, resources/)\n"
                                      "• Preserves existing userChrome.css and other user files", 
                                 font=('Arial', 9), foreground='dark blue')
        complete_desc.pack(anchor=tk.W, padx=20, pady=(2, 10))
        
        # Warning for complete uninstall
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=10)
        
        def update_warning():
            if uninstall_option.get() == "complete":
                warning_label.config(text="Complete removal of fx-autoconfig files while preserving your existing user files.", 
                                   foreground='dark blue')
            else:
                warning_label.config(text="Your custom scripts and styles will be preserved.", 
                                   foreground='green')
        
        warning_label = ttk.Label(warning_frame, text="Your custom scripts and styles will be preserved.", 
                                 font=('Arial', 9, 'bold'), foreground='green')
        warning_label.pack()
        
        # Update warning when option changes
        partial_radio.config(command=update_warning)
        complete_radio.config(command=update_warning)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        def proceed_uninstall():
            is_complete = uninstall_option.get() == "complete"
            dialog.destroy()
            self._perform_uninstall(is_complete)
        
        def cancel_uninstall():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=cancel_uninstall).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Proceed", command=proceed_uninstall).pack(side=tk.RIGHT)
    
    def _perform_uninstall(self, complete_uninstall=False):
        """Perform the actual uninstallation"""
        uninstall_type = "complete" if complete_uninstall else "partial"
        
        # Check if we need elevation for Windows Program Files uninstallation
        firefox_path = self.firefox_path.get()
        if platform.system() == "Windows" and self.needs_elevation(firefox_path) and not self.is_admin():
            result = messagebox.askyesno(
                "Administrator Privileges Required",
                f"Firefox is installed in:\n{firefox_path}\n\n"
                "This location requires administrator privileges to remove fx-autoconfig files.\n"
                "Would you like to restart the installer with elevated privileges?\n\n"
                "Click 'Yes' to restart as administrator, or 'No' to continue (may fail).",
                icon='question'
            )
            
            if result:
                self.log_message("Requesting elevated privileges for uninstallation...")
                if self.request_elevation():
                    self.log_message("Restarting with elevated privileges...")
                    self.root.quit()  # Close current instance
                    return
                else:
                    self.log_message("Failed to request elevation, continuing anyway...", error=True)
            else:
                self.log_message("Continuing without elevation (uninstallation may fail)...", error=True)
        
        # Final confirmation for complete uninstall
        if complete_uninstall:
            result = messagebox.askyesno(
                "Final Confirmation",
                "Are you sure you want to completely remove fx-autoconfig?\n\n"
                "This will remove:\n"
                "• All fx-autoconfig system files\n"
                "• CSS/ and JS/ directories completely (including user scripts)\n"
                "• fx-autoconfig files in utils/ and resources/\n\n"
                "This will preserve:\n"
                "• Your existing userChrome.css and userContent.css\n"
                "• Any other files you added to chrome/ directory\n"
                "• Original files (if symlinked, only links are removed)\n\n"
                "Continue with complete removal?",
                icon='question'
            )
            if not result:
                return
        
        def uninstall_thread():
            try:
                self.log_message(f"Starting {uninstall_type} fx-autoconfig uninstallation...")
                  # Remove program files - only remove files that exist in the repository
                firefox_path = self.firefox_path.get()
                
                # On macOS, files are in Contents/Resources/, not Contents/MacOS/
                if platform.system() == "Darwin" and firefox_path.endswith("MacOS"):
                    firefox_path = firefox_path.replace("MacOS", "Resources")
                
                # Remove only the specific files that fx-autoconfig installs
                repo_root = self.get_repo_root()
                if repo_root:
                    self._remove_program_files(firefox_path, repo_root)
                else:
                    self.log_message("Warning: Could not find repository root, skipping program file removal", error=True)
                  # Handle profile files based on uninstall type
                profile_path = self.profile_path.get()
                chrome_dir = os.path.join(profile_path, "chrome")
                
                if complete_uninstall:
                    # Carefully remove only fx-autoconfig files, preserve existing user files
                    self._remove_fx_autoconfig_files(chrome_dir)
                else:
                    # Remove only utils directory (preserve user scripts)
                    utils_dir = os.path.join(chrome_dir, "utils")
                    if os.path.exists(utils_dir):
                        self._safe_remove_directory(utils_dir)
                        self.log_message("Removed utils directory (user scripts preserved)")
                
                self.log_message(f"fx-autoconfig {uninstall_type} uninstallation completed successfully")
                
                if complete_uninstall:
                    self.log_message("fx-autoconfig files removed while preserving existing user files")
                else:
                    self.log_message("Your custom scripts and styles have been preserved")
                
            except Exception as e:
                self.log_message(f"Uninstallation failed: {str(e)}", error=True)
                
        threading.Thread(target=uninstall_thread, daemon=True).start()
        
    def _safe_remove_directory(self, directory_path):
        """Safely remove a directory, handling symlinks properly"""
        if not os.path.exists(directory_path):
            return
            
        # Walk through all files and subdirectories
        for root, dirs, files in os.walk(directory_path, topdown=False):
            # Remove files (handle symlinks properly)
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.islink(file_path):
                    # Remove symlink, not the target
                    os.unlink(file_path)
                    self.log_message(f"Removed symlink: {file}")
                else:
                    # Remove regular file
                    os.remove(file_path)
                    self.log_message(f"Removed file: {file}")
            
            # Remove empty directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if os.path.islink(dir_path):
                    # Remove directory symlink
                    os.unlink(dir_path)
                    self.log_message(f"Removed directory symlink: {dir_name}")
                else:
                    try:
                        os.rmdir(dir_path)
                        self.log_message(f"Removed directory: {dir_name}")
                    except OSError:
                        # Directory not empty, skip
                        pass
        
        # Finally remove the root directory if empty
        try:
            os.rmdir(directory_path)
        except OSError:
            # Directory not empty, that's okay
            pass
    
    def _remove_fx_autoconfig_files(self, chrome_dir):
        """Remove fx-autoconfig files based on correct assumptions:
        1. CSS/ and JS/ folders can be completely removed (user-provided files)
        2. Other files: only remove if they exist in fx-autoconfig repository
        """
        if not os.path.exists(chrome_dir):
            self.log_message("Chrome directory does not exist")
            return
        
        removed_count = 0
        
        # 1. Completely remove CSS and JS directories (user-provided files)
        user_dirs = ['CSS', 'JS']
        for dir_name in user_dirs:
            dir_path = os.path.join(chrome_dir, dir_name)
            if os.path.exists(dir_path):
                file_count = sum([len(files) for r, d, files in os.walk(dir_path)])
                self._safe_remove_directory(dir_path)
                self.log_message(f"Removed {dir_name}/ directory with {file_count} files")
                removed_count += file_count
        
        # 2. Get repository root to check what files fx-autoconfig actually installs
        repo_root = self.get_repo_root()
        profile_src = os.path.join(repo_root, "profile", "chrome")
        
        if not os.path.exists(profile_src):
            self.log_message("Warning: Could not find fx-autoconfig profile source for comparison")
            return
        
        # 3. Remove only files that exist in the fx-autoconfig repository
        for root, dirs, files in os.walk(profile_src):
            # Calculate relative path from profile/chrome/
            rel_path = os.path.relpath(root, profile_src)
            
            # Skip CSS and JS directories (already handled above)
            if rel_path.startswith('CSS') or rel_path.startswith('JS'):
                continue
            
            # Determine target directory in user's profile
            if rel_path == '.':
                target_dir = chrome_dir
            else:
                target_dir = os.path.join(chrome_dir, rel_path)
            
            # Remove files that exist in fx-autoconfig repository
            for file in files:
                target_file = os.path.join(target_dir, file)
                if os.path.exists(target_file) or os.path.islink(target_file):
                    if os.path.islink(target_file):
                        os.unlink(target_file)
                        self.log_message(f"Removed fx-autoconfig symlink: {os.path.join(rel_path, file)}")
                    else:
                        os.remove(target_file)
                        self.log_message(f"Removed fx-autoconfig file: {os.path.join(rel_path, file)}")
                    removed_count += 1
        
        # 4. Remove empty directories that were created by fx-autoconfig
        # Walk through repository structure to identify fx-autoconfig directories
        for root, dirs, files in os.walk(profile_src, topdown=False):
            rel_path = os.path.relpath(root, profile_src)
            
            # Skip CSS and JS directories (already removed)
            if rel_path.startswith('CSS') or rel_path.startswith('JS') or rel_path == '.':
                continue
            
            target_dir = os.path.join(chrome_dir, rel_path)
            if os.path.exists(target_dir):
                try:
                    # Only remove if directory is empty (no user files)
                    if not os.listdir(target_dir):
                        os.rmdir(target_dir)
                        self.log_message(f"Removed empty fx-autoconfig directory: {rel_path}")
                    else:
                        remaining = os.listdir(target_dir)
                        self.log_message(f"Preserved directory {rel_path}/ with {len(remaining)} user files")
                except OSError:
                    pass
        
        # 5. Check if chrome directory itself can be removed
        try:
            if os.path.exists(chrome_dir) and not os.listdir(chrome_dir):
                os.rmdir(chrome_dir)
                self.log_message("Removed empty chrome directory")
            elif os.path.exists(chrome_dir):
                remaining = os.listdir(chrome_dir)
                self.log_message(f"Preserved chrome directory with {len(remaining)} user items")
        except OSError:
            pass
        
        self.log_message(f"Complete uninstall summary: {removed_count} fx-autoconfig files removed")
    
    def _remove_program_files(self, firefox_path, repo_root):
        """Remove only program files that exist in the fx-autoconfig repository"""
        program_src = os.path.join(repo_root, "program")
        
        # Walk through the repository program directory to find what files to remove
        for root, dirs, files in os.walk(program_src):
            rel_path = os.path.relpath(root, program_src)
            
            # Calculate target directory in Firefox installation
            if rel_path == '.':
                target_dir = firefox_path
            else:
                target_dir = os.path.join(firefox_path, rel_path)
            
            # Remove files that exist in the repository
            for file in files:
                target_file = os.path.join(target_dir, file)
                
                if os.path.exists(target_file):
                    try:
                        os.remove(target_file)
                        self.log_message(f"Removed program file: {os.path.join(rel_path, file) if rel_path != '.' else file}")
                    except Exception as e:
                        self.log_message(f"Failed to remove {target_file}: {e}", error=True)
        
        # Clean up empty directories that we created (but don't remove existing directories)
        # Only remove the specific subdirectories that fx-autoconfig created
        defaults_pref_dir = os.path.join(firefox_path, "defaults", "pref")
        defaults_dir = os.path.join(firefox_path, "defaults")
        
        # Remove defaults/pref if it's empty and was created by fx-autoconfig
        if os.path.exists(defaults_pref_dir) and not os.listdir(defaults_pref_dir):
            try:
                os.rmdir(defaults_pref_dir)
                self.log_message("Removed empty defaults/pref directory")
            except Exception as e:
                self.log_message(f"Could not remove defaults/pref directory: {e}")
        
        # Remove defaults if it's empty and was created by fx-autoconfig
        if os.path.exists(defaults_dir) and not os.listdir(defaults_dir):
            try:
                os.rmdir(defaults_dir)
                self.log_message("Removed empty defaults directory")
            except Exception as e:                self.log_message(f"Could not remove defaults directory: {e}")
    
    def clear_startup_cache(self):
        if not self.profile_path.get():
            self.log_message("Please select a profile directory first", error=True)
            return
        
        # Get the correct startup cache location based on platform
        cache_dir = self.get_startup_cache_path()
        
        if not cache_dir:
            self.log_message("Could not determine startup cache location", error=True)
            return
            
        if not os.path.exists(cache_dir):
            self.log_message(f"Startup cache directory not found: {cache_dir}", error=True)
            return
            
        result = messagebox.askyesno(
            "Clear Startup Cache",
            f"This will delete the startup cache from:\n{cache_dir}\n\n"
            "Firefox must be closed. Continue?"
        )
        
        if not result:
            return
            
        try:
            shutil.rmtree(cache_dir)
            self.log_message("Startup cache cleared successfully")
            self.log_message("Restart Firefox to apply changes")
        except Exception as e:
            self.log_message(f"Failed to clear startup cache: {str(e)}", error=True)
    
    def get_startup_cache_path(self):
        """Get the correct startup cache path for the current platform"""
        profile_path = self.profile_path.get()
        if not profile_path:
            return None
        
        system = platform.system()
        
        if system == "Windows":
            # On Windows, startup cache is in Local AppData, not Roaming
            profile_name = os.path.basename(profile_path)
            cache_dir = os.path.join(
                os.environ.get('LOCALAPPDATA', ''),
                "Mozilla", "Firefox", "Profiles", profile_name, "startupCache"
            )
        else:
            # On macOS and Linux, startup cache is in the profile directory
            cache_dir = os.path.join(profile_path, "startupCache")
        
        return cache_dir
            
    def open_profile_folder(self):
        if not self.profile_path.get():
            self.log_message("Please select a profile directory first", error=True)
            return
              # Try to open chrome directory first, then profile root
        chrome_dir = os.path.join(self.profile_path.get(), "chrome")
        if os.path.exists(chrome_dir):
            target_dir = chrome_dir
        else:
            target_dir = self.profile_path.get()
                
        self.open_in_file_manager(target_dir)
        
    def open_in_file_manager(self, path):
        system = platform.system()
        
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path])
            elif system == "Linux":
                subprocess.run(["xdg-open", path])
            else:
                self.log_message("Opening file manager not supported on this OS", error=True)
                return
                
            self.log_message(f"Opened folder: {path}")
            
        except Exception as e:
            self.log_message(f"Failed to open file manager: {str(e)}", error=True)
    
    def validate_repository(self):
        """Validate that the fx-autoconfig repository structure is available"""
        repo_root = self.get_repo_root()
        if not repo_root:
            self.show_repository_error()
            return False
            
        # Check that required directories exist
        program_dir = os.path.join(repo_root, "program")
        profile_dir = os.path.join(repo_root, "profile")
        
        if not os.path.exists(program_dir) or not os.path.exists(profile_dir):
            self.show_repository_error()
            return False
            
        self.log_message(f"fx-autoconfig repository found at: {repo_root}")
        return True
        
    def show_repository_error(self):
        """Show error dialog when repository structure is not found"""
        error_msg = (
            "fx-autoconfig repository structure not found!\n\n"
            "This installer must be run from within the fx-autoconfig repository.\n"
            "Please ensure you have:\n"
            "• Downloaded the complete fx-autoconfig repository\n"
            "• The 'program/' and 'profile/' directories exist\n"
            "• Running the installer from the correct location\n\n"
            "Installation and profile management will not work without these files."
        )
        
        messagebox.showerror("Repository Not Found", error_msg)
        self.log_message("ERROR: fx-autoconfig repository structure not found", error=True)
        
        # Disable installation-related buttons
        if hasattr(self, 'install_btn'):
            self.install_btn.config(state='disabled')
        if hasattr(self, 'uninstall_btn'):
            self.uninstall_btn.config(state='disabled')

    def simple_markdown_to_text(self, markdown_content):
        """Convert basic markdown to plain text without dependencies"""
        import re
        
        # Remove markdown headers (# ## ###)
        content = re.sub(r'^#{1,6}\s*(.+)$', r'\1', markdown_content, flags=re.MULTILINE)
        
        # Remove code block markers (```
        content = re.sub(r'```[\w]*\n?', '', content)
        
        # Remove inline code markers (`
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Remove bold/italic markers (** __)
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        
        # Convert links [text](url) to text (url)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', content)
        
        # Remove list markers (- * +)
        content = re.sub(r'^[\s]*[-*+]\s*', '• ', content, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def is_admin(self):
        """Check if the current process has admin privileges on Windows"""
        if platform.system() != "Windows":
            return True  # Non-Windows systems don't need UAC elevation
        
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def needs_elevation(self, firefox_path):
        """Check if the Firefox installation path requires admin privileges"""
        if platform.system() != "Windows":
            return False
        
        # Common paths that typically require elevation
        program_files_paths = [
            "C:\\Program Files\\",
            "C:\\Program Files (x86)\\",
            os.environ.get('PROGRAMFILES', '').lower(),
            os.environ.get('PROGRAMFILES(X86)', '').lower()        ]
        
        firefox_path_lower = firefox_path.lower()
        return any(firefox_path_lower.startswith(path.lower()) for path in program_files_paths if path)
    
    def request_elevation(self):
        """Restart the application with elevated privileges"""
        if platform.system() != "Windows":
            return False
        
        try:
            import ctypes
            import sys
            
            # Get the current script path
            script_path = os.path.abspath(__file__)
            
            # Use pythonw.exe to avoid console window
            python_executable = sys.executable
            if python_executable.endswith('python.exe'):
                python_executable = python_executable.replace('python.exe', 'pythonw.exe')
            elif not python_executable.endswith('pythonw.exe'):
                # If it's some other executable, try to find pythonw.exe in the same directory
                import os
                python_dir = os.path.dirname(python_executable)
                pythonw_path = os.path.join(python_dir, 'pythonw.exe')
                if os.path.exists(pythonw_path):
                    python_executable = pythonw_path
            
            # Request elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                python_executable, 
                f'"{script_path}"',
                None, 
                0  # SW_HIDE - Hide the window to prevent console flash
            )
            return True
        except Exception as e:
            self.log_message(f"Failed to request elevation: {e}", error=True)
            return False

def main():
    root = tk.Tk()
    app = FxAutoconfigInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
