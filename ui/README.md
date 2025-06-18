# fx-autoconfig GUI Installer

A cross-platform graphical user interface for installing and managing fx-autoconfig, the Firefox userChrome.js manager.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)

## Features

- **🔍 Auto-detection**: Automatically detects Firefox installation and profile directories
- **⚡ Easy Installation**: One-click installation of fx-autoconfig components
- **👥 Profile Management**: Detects and manages multiple Firefox profiles
- **� Custom Files Support**: Import existing userChrome scripts and styles
- **🔗 Symlink Support**: Create symlinks for live editing or copy files
- **�🗂️ Startup Cache Management**: Built-in startup cache clearing functionality
- **🌐 Cross-platform**: Works on Windows, macOS, and Linux
- **📦 No Dependencies**: Uses only Python standard library (Tkinter)
- **💾 Configuration Memory**: Remembers your paths between sessions

## Requirements

- **Python 3.6 or later** (with Tkinter support)
- **Firefox 102+** (ESR 102 not supported)

Most Python installations include Tkinter by default. If not:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **CentOS/RHEL**: `sudo yum install tkinter` or `sudo dnf install python3-tkinter`
- **macOS**: Tkinter is included with Python from python.org
- **Windows**: Tkinter is included with Python

## Quick Start

### Direct Python Execution

1. **Download** the installer:
   ```bash
   curl -O https://raw.githubusercontent.com/MrOtherGuy/fx-autoconfig/master/ui/fx_autoconfig_installer.py
   ```

2. **Run** the installer:
   ```bash
   python fx_autoconfig_installer.py
   ```
   or
   ```bash
   python3 fx_autoconfig_installer.py
   ```

### From Repository

1. **Clone** the repository:
   ```bash
   git clone https://github.com/MrOtherGuy/fx-autoconfig.git
   cd fx-autoconfig/ui
   ```

2. **Run** the installer:
   ```bash
   python fx_autoconfig_installer.py
   ```

## Usage Guide

### Installation Steps

1. **Launch** the installer
2. **Auto-detect Firefox**: Click "Auto-detect" or manually browse to your Firefox installation directory
3. **Select Profile**: Click "Detect Profiles" to choose from available profiles, or browse manually
4. **(Optional) Custom Files**: Browse to a directory containing your existing userChrome scripts and styles
5. **Choose Copy/Symlink**: Select whether to copy files or create symlinks (symlinks preserve live editing)
6. **Install**: Click "Install fx-autoconfig" to set up the userChrome.js manager
7. **Clear Cache**: After installation, click "Clear Startup Cache" (**required** for first use)
8. **Add Scripts**: Use "Open Profile Folder" to navigate to chrome/JS/ and add more .uc.js scripts

### What the Installer Does

#### Firefox Installation Directory
```
Firefox/
├── config.js                    # ← Main autoconfig file
└── defaults/
    └── pref/
        └── config-prefs.js      # ← Configuration preferences
```

#### Firefox Profile Directory
```
Profile/
└── chrome/
    ├── JS/                      # ← Your userChrome scripts (.uc.js)
    ├── CSS/                     # ← Your userChrome styles (.uc.css)
    ├── resources/               # ← Script resources and data files        └── utils/                   # ← fx-autoconfig core files
            ├── boot.sys.mjs         # ← Main loader
            ├── utils.sys.mjs        # ← Utility functions
            ├── fs.sys.mjs           # ← File system operations
            ├── uc_api.sys.mjs       # ← Modern API interface
            └── chrome.manifest      # ← Chrome URL mappings

#### Custom Files Directory (Optional)
If you specify a custom files directory, the installer will:
- **Follow typical installation patterns** (e.g., "copy contents of `src/` to `chrome/JS/`")
- Copy or symlink `.uc.js/.uc.mjs/.sys.mjs` files to `chrome/JS/`
- Copy or symlink `.uc.css` files to `chrome/CSS/`
- Copy or symlink other files to `chrome/resources/`
- **Preserve subdirectory structure** within each target folder
- **Symlinks** preserve live editing - changes to original files reflect immediately
- **Copying** creates independent copies in the profile

**Example**: If you point to a folder containing `src/second_sidebar/` and `src/second_sidebar.uc.mjs`, the installer will place these in `chrome/JS/second_sidebar/` and `chrome/JS/second_sidebar.uc.mjs` respectively.

## How It Works

The installer follows the same manual installation process described in the main README:

1. **Program Files**: Copies the contents of the `program/` directory to your Firefox installation directory
   - On Windows/Linux: Files go to the same directory as the firefox executable
   - On macOS: Files go to `/Applications/Firefox.app/Contents/Resources/`

2. **Profile Files**: Copies the contents of the `profile/chrome/` directory to your Firefox profile's `chrome/` directory

3. **Custom Files**: Optionally copies or symlinks your existing userChrome scripts and styles:
   - `.uc.js/.uc.mjs/.sys.mjs` files → `chrome/JS/`
   - `.uc.css` files → `chrome/CSS/`
   - Other files → `chrome/resources/`

This approach ensures the installer stays in sync with the manual installation instructions and doesn't require maintaining duplicate file contents.

## Platform-Specific Information

### Windows
- **Firefox Path**: `C:\Program Files\Mozilla Firefox\`
- **Profile Path**: `%APPDATA%\Mozilla\Firefox\Profiles\`
- **Python**: Download from [python.org](https://python.org) or Microsoft Store

### macOS
- **Firefox Path**: `/Applications/Firefox.app/Contents/MacOS/`
- **Profile Path**: `~/Library/Application Support/Firefox/Profiles/`
- **Python**: Use Homebrew (`brew install python`) or download from python.org

### Linux
- **Firefox Path**: `/usr/lib/firefox/` or `/usr/lib64/firefox/`
- **Profile Path**: `~/.mozilla/firefox/`
- **Python**: Usually pre-installed, or install via package manager

## Troubleshooting

### Common Issues

**"Python not found"**
- Install Python 3.6+ from [python.org](https://python.org)
- Ensure Python is in your system PATH

**"No module named tkinter"**
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- CentOS/RHEL: `sudo dnf install python3-tkinter`

**"Permission denied" during installation**
- Run as administrator/root
- Ensure Firefox is completely closed

**Auto-detection fails**
- Manually browse to Firefox installation directory
- Check the help tab for common Firefox locations

**Scripts not loading after installation**
1. Clear startup cache using the installer
2. Restart Firefox completely
3. Check that scripts are in `profile/chrome/JS/`
4. Verify scripts are enabled: Firefox Menu → Tools → userScripts

### Getting Help

1. **Check the Help tab** in the installer for detailed instructions
2. **Read the main README** at the repository root
3. **Visit the Issues page** on GitHub for community support
4. **Check Firefox compatibility** - ESR 102 is not supported

## Development

### File Structure
```
ui/
├── fx_autoconfig_installer.py   # Main installer application
├── README.md                   # This file
└── installer_config.json       # User configuration (created at runtime)
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Test on multiple platforms
4. Submit a pull request

### Architecture

- **Main Class**: `FxAutoconfigInstaller` - handles all UI and logic
- **Threading**: Non-blocking operations for file copying
- **Configuration**: JSON-based settings persistence
- **Cross-platform**: Uses `platform.system()` for OS detection
- **Error Handling**: Comprehensive exception handling with user feedback

## License

This GUI installer follows the same license as the main fx-autoconfig project.

## Acknowledgments

- Built for the [fx-autoconfig](https://github.com/MrOtherGuy/fx-autoconfig) project by MrOtherGuy
- Uses Python's built-in Tkinter for cross-platform GUI support
- No external dependencies required
