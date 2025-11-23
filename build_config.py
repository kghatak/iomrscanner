#!/usr/bin/env python3
"""
Build configuration for Image Folder Analyzer
"""
import platform

APP_NAME = "Bignan Mancha OMR Reader"
APP_VERSION = "2.0.8"
APP_BUNDLE_ID = "com.bignanmancha.omr.reader"
APP_AUTHOR = "Bignan Mancha"
APP_DESCRIPTION = "OMR (Optical Mark Recognition) sheet processing and analysis tool"

# Platform detection
CURRENT_OS = platform.system().lower()

# PyInstaller configuration (cross-platform)
PYINSTALLER_CONFIG = {
    'name': APP_NAME,
    'version': APP_VERSION,
    'windowed': True,  # No console window
    'one_file': False,  # Create a bundle instead of single file
    'clean': True,
    'noconfirm': True,
}

# Platform-specific configurations
PLATFORM_CONFIG = {
    'windows': {
        'icon': 'assets/app_icon.ico',  # Windows ICO format
        'installer_type': 'nsis',  # NSIS installer
        'file_extension': '.exe',
        'installer_extension': '.exe',
        'build_tools': ['pyinstaller', 'nsis'],  # NSIS for Windows installer
    },
    'darwin': {  # macOS
        'icon': 'assets/app_icon.icns',  # macOS ICNS format
        'installer_type': 'dmg',
        'file_extension': '.app',
        'installer_extension': '.dmg',
        'build_tools': ['pyinstaller', 'dmgbuild'],
    },
    'linux': {
        'icon': 'assets/app_icon.png',  # PNG for Linux
        'installer_type': 'appimage',
        'file_extension': '',
        'installer_extension': '.AppImage',
        'build_tools': ['pyinstaller', 'appimagetool'],
    }
}

# Get current platform config
CURRENT_PLATFORM = PLATFORM_CONFIG.get(CURRENT_OS, PLATFORM_CONFIG['linux'])

# DMG configuration (macOS only)
DMG_CONFIG = {
    'title': f"{APP_NAME} {APP_VERSION}",
    'background': 'assets/dmg_background.png',  # Optional: custom background
    'icon_size': 128,
    'window_size': (640, 480),
    'icon_positions': {
        f'{APP_NAME}.app': (150, 200),
        'Applications': (500, 200)
    }
}

# NSIS configuration (Windows only)
NSIS_CONFIG = {
    'name': APP_NAME,
    'version': APP_VERSION,
    'publisher': APP_AUTHOR,
    'description': APP_DESCRIPTION,
    'license': 'LICENSE.txt',  # Optional: license file
    'icon': CURRENT_PLATFORM['icon'],
    'install_dir': f'$PROGRAMFILES\\{APP_NAME}',
    'start_menu': True,
    'desktop_shortcut': True,
    'uninstaller': True,
}
