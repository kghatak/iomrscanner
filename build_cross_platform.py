#!/usr/bin/env python3
"""
Cross-platform build script for Image Folder Analyzer
Supports Windows EXE, macOS DMG, and Linux AppImage builds
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from build_config import (
    APP_NAME, APP_VERSION, CURRENT_OS, CURRENT_PLATFORM, 
    NSIS_CONFIG, DMG_CONFIG
)

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"[SUCCESS] {cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running: {cmd}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def install_dependencies():
    """Install required build dependencies for current platform"""
    print(f"[INSTALL] Installing build dependencies for {CURRENT_OS}...")
    
    base_dependencies = ['pyinstaller']
    platform_dependencies = CURRENT_PLATFORM['build_tools']
    
    all_dependencies = list(set(base_dependencies + platform_dependencies))
    
    for dep in all_dependencies:
        if dep == 'nsis':
            if CURRENT_OS == 'windows':
                print("[WARNING] NSIS installer needs to be downloaded separately from:")
                print("   https://nsis.sourceforge.io/Download")
            else:
                print(f"[WARNING] NSIS not needed on {CURRENT_OS}")
        elif dep == 'appimagetool':
            if CURRENT_OS == 'linux':
                print("[WARNING] AppImageTool needs to be downloaded separately from:")
                print("   https://github.com/AppImage/AppImageKit/releases")
            else:
                print(f"[WARNING] AppImageTool not needed on {CURRENT_OS}")
        else:
            run_command(f"pip install {dep}")

def create_app_bundle():
    """Create the application bundle using PyInstaller"""
    print(f"[BUILD] Creating {CURRENT_OS} app bundle with PyInstaller...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Build PyInstaller command
    cmd_parts = [
        'pyinstaller',
        '--windowed',  # No console
        '--onedir',    # Create a bundle
        '--clean',
        '--noconfirm',
        f'--name="{APP_NAME}"',
        '--add-data=ui:ui',  # Include UI package
    ]
    
    # Add platform-specific icon
    icon_path = CURRENT_PLATFORM['icon']
    if os.path.exists(icon_path):
        cmd_parts.append(f'--icon={icon_path}')
    
    # Platform-specific options
    if CURRENT_OS == 'windows':
        cmd_parts.append('--noconsole')  # Extra Windows option
    elif CURRENT_OS == 'darwin':
        cmd_parts.append(f'--osx-bundle-identifier={APP_NAME.lower().replace(" ", ".")}.app')
    
    # Add the main script
    cmd_parts.append('main.py')
    
    cmd = ' '.join(cmd_parts)
    run_command(cmd)
    
    app_name = f"{APP_NAME}{CURRENT_PLATFORM['file_extension']}"
    print(f"[SUCCESS] App bundle created: dist/{app_name}")

def create_windows_installer():
    """Create Windows NSIS installer"""
    print("[BUILD] Creating Windows NSIS installer...")
    
    # Create NSIS script
    nsis_script = f'''
!include "MUI2.nsh"

Name "{NSIS_CONFIG['name']}"
OutFile "{APP_NAME.replace(' ', '_')}_v{APP_VERSION}_Setup.exe"
InstallDir "{NSIS_CONFIG['install_dir']}"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "{NSIS_CONFIG['icon']}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\{APP_NAME}\\*"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" "DisplayName" "{APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\{APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    CreateShortCut "$DESKTOP\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME}.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\\{APP_NAME}"
    Delete "$DESKTOP\\{APP_NAME}.lnk"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
SectionEnd
'''
    
    # Write NSIS script
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    # Create LICENSE.txt if it doesn't exist
    if not os.path.exists('LICENSE.txt'):
        with open('LICENSE.txt', 'w') as f:
            f.write(f"{APP_NAME} License\\n\\nAdd your license text here.")
    
    # Run NSIS compiler
    try:
        run_command('makensis installer.nsi')
        print(f"[SUCCESS] Windows installer created: {APP_NAME.replace(' ', '_')}_v{APP_VERSION}_Setup.exe")
    except:
        print("[ERROR] NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        create_simple_zip_installer()
    
    # Clean up
    if os.path.exists('installer.nsi'):
        os.remove('installer.nsi')

def create_simple_zip_installer():
    """Create a simple ZIP installer as fallback"""
    print("[BUILD] Creating ZIP installer...")
    
    zip_name = f"{APP_NAME.replace(' ', '_')}_v{APP_VERSION}_{CURRENT_OS}.zip"
    
    # Create installation instructions
    if CURRENT_OS == 'windows':
        instructions = f'''
# {APP_NAME} v{APP_VERSION} - Windows Installation

## Installation:
1. Extract all files to a folder (e.g., C:\\Program Files\\{APP_NAME})
2. Run "{APP_NAME}.exe" to start the application
3. Optionally create shortcuts on desktop or start menu

## System Requirements:
- Windows 10 or later
- No additional dependencies required

## Uninstallation:
Simply delete the folder containing the application.

---
Created with PyQt5 and PyInstaller
'''
    else:
        instructions = f'''
# {APP_NAME} v{APP_VERSION} - Installation Instructions

## Installation:
1. Extract the archive to your preferred location
2. Run the application executable
3. Enjoy using {APP_NAME}!

## System Requirements:
- Compatible operating system
- No additional dependencies required

## Uninstallation:
Simply delete the application folder.

---
Created with PyQt5 and PyInstaller
'''
    
    # Create temporary directory
    installer_dir = "installer_temp"
    os.makedirs(installer_dir, exist_ok=True)
    
    # Copy the app
    app_folder = f"dist/{APP_NAME}"
    if os.path.exists(app_folder):
        shutil.copytree(app_folder, f"{installer_dir}/{APP_NAME}")
    
    # Create installation instructions
    with open(f'{installer_dir}/README.txt', 'w') as f:
        f.write(instructions)
    
    # Create ZIP
    shutil.make_archive(zip_name.replace('.zip', ''), 'zip', installer_dir)
    
    # Clean up
    shutil.rmtree(installer_dir)
    
    print(f"[SUCCESS] ZIP installer created: {zip_name}")

def create_installer():
    """Create installer for current platform"""
    if CURRENT_OS == 'windows':
        create_windows_installer()
    elif CURRENT_OS == 'darwin':
        create_dmg_installer()
    elif CURRENT_OS == 'linux':
        create_appimage()
    else:
        create_simple_zip_installer()

def create_dmg_installer():
    """Create macOS DMG installer"""
    print("[BUILD] Creating DMG installer...")
    
    # Create DMG settings file
    dmg_settings = f'''
import os

# DMG settings
files = ['dist/{APP_NAME}.app']
symlinks = {{'Applications': '/Applications'}}
badge_icon = None
icon_locations = {{
    '{APP_NAME}.app': (150, 200),
    'Applications': (500, 200),
}}
background = None
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180
window_rect = ((100, 100), (640, 480))
default_view = 'icon-view'
show_icon_preview = False
include_icon_view_settings = 'auto'
include_list_view_settings = 'auto'
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom'
text_size = 12
icon_size = 128
'''
    
    with open('dmg_settings.py', 'w') as f:
        f.write(dmg_settings)
    
    # Create DMG
    dmg_name = f"{APP_NAME.replace(' ', '_')}_v{APP_VERSION}.dmg"
    try:
        run_command(f'dmgbuild -s dmg_settings.py "{APP_NAME}" "{dmg_name}"')
        print(f"[SUCCESS] DMG created: {dmg_name}")
    except:
        print("[ERROR] dmgbuild not found or failed. Creating ZIP installer instead...")
        create_simple_zip_installer()
    
    # Clean up
    if os.path.exists('dmg_settings.py'):
        os.remove('dmg_settings.py')

def create_appimage():
    """Create Linux AppImage (placeholder)"""
    print("[BUILD] Linux AppImage creation not implemented yet")
    print("Creating ZIP installer instead...")
    create_simple_zip_installer()

def main():
    """Main build process"""
    print(f"[BUILD] Building {APP_NAME} v{APP_VERSION} for {CURRENT_OS}")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("[ERROR] Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    try:
        # Step 1: Install dependencies
        install_dependencies()
        
        # Step 2: Create app bundle
        create_app_bundle()
        
        # Step 3: Create platform-specific installer
        create_installer()
        
        print("\\n" + "=" * 50)
        print("[SUCCESS] Build completed successfully!")
        print(f"[INFO] Check the project directory for your {CURRENT_OS} installer files")
        
        if CURRENT_OS == 'windows':
            print("\\n[INFO] For Windows builds:")
            print("   - Install NSIS for professional installers")
            print("   - Add .ico icon file for better appearance")
        
    except KeyboardInterrupt:
        print("\\n[CANCELLED] Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n[ERROR] Build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
