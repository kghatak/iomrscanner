"""
Utility functions for PDF processing with Poppler support.
This module provides cross-platform Poppler path detection for pdf2image.
"""
import os
import sys
import glob
import shutil
import platform


def find_poppler_path():
    """
    Find Poppler installation on Windows.
    Returns a tuple: (found: bool, path: str or None)
    - If found in a specific location: (True, path)
    - If found in system PATH: (True, None)
    - If not found: (False, None)
    
    On non-Windows platforms, always returns (True, None) as Poppler
    should be installed via system package manager.
    """
    # Non-Windows platforms use system Poppler
    if platform.system() != 'Windows':
        return (True, None)
    
    # Windows-specific logic
    # First, check if poppler is in system PATH
    if shutil.which("pdfinfo") or shutil.which("pdftoppm"):
        return (True, None)  # Found in PATH, no need to specify path
    
    # Get the application directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Common installation locations for Poppler on Windows
    # Priority order: bundled > user installation > system installation
    possible_paths = [
        # Check bundled Poppler first (highest priority)
        os.path.join(app_dir, "poppler_bundle", "bin"),
        os.path.join(app_dir, "_internal", "poppler_bundle", "bin"),  # PyInstaller internal
        os.path.join(app_dir, "poppler", "bin"),
        os.path.join(app_dir, "_internal", "poppler", "bin"),  # PyInstaller internal
        # Check in application directory (for manual bundling)
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler_bundle", "bin"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler", "Library", "bin"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler", "bin"),
        # Check in common user installation directories
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin",
        r"C:\poppler-*\Library\bin",
        r"C:\poppler-*\bin",
        # Check in Program Files
        r"C:\Program Files\poppler\Library\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\Library\bin",
        r"C:\Program Files (x86)\poppler\bin",
        r"C:\Program Files\poppler-*\Library\bin",
        r"C:\Program Files (x86)\poppler-*\Library\bin",
    ]
    
    # Try to find pdfinfo.exe or pdftoppm.exe in these locations
    for path_pattern in possible_paths:
        # Handle both direct paths and glob patterns
        paths_to_check = [path_pattern]
        if '*' in path_pattern:
            paths_to_check = glob.glob(path_pattern)
        
        for path in paths_to_check:
            if os.path.exists(path):
                # Check if pdfinfo.exe or pdftoppm.exe exists
                if os.path.exists(os.path.join(path, "pdfinfo.exe")) or \
                   os.path.exists(os.path.join(path, "pdftoppm.exe")):
                    return (True, path)
    
    return (False, None)  # Not found


def convert_pdf_with_poppler(pdf_path, **kwargs):
    """
    Convert PDF to images using pdf2image with automatic Poppler path detection.
    
    Args:
        pdf_path: Path to the PDF file
        **kwargs: Additional arguments to pass to convert_from_path
        
    Returns:
        List of PIL Image objects
        
    Raises:
        ImportError: If pdf2image is not installed
        RuntimeError: If Poppler is not found on Windows
        Exception: Any other errors from pdf2image
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError("pdf2image is not installed. Please install it with: pip install pdf2image")
    
    # Check for Poppler on Windows
    if platform.system() == 'Windows':
        found, poppler_path = find_poppler_path()
        if not found:
            raise RuntimeError(
                "Poppler is not found on your system.\n\n"
                "To use PDF processing on Windows, you need to install Poppler:\n\n"
                "1. Download Poppler for Windows from:\n"
                "   https://github.com/oschwartz10612/poppler-windows/releases/\n\n"
                "2. Extract the downloaded archive to a folder (e.g., C:\\Program Files\\poppler)\n\n"
                "3. Add the 'bin' folder to your system PATH or place it in one of these locations:\n"
                "   - C:\\Program Files\\poppler-{version}\\Library\\bin\n"
                "   - C:\\poppler\\Library\\bin\n"
                "   - In the same directory as this application"
            )
        
        # Add poppler_path to kwargs if found in specific location
        if poppler_path:
            kwargs['poppler_path'] = poppler_path
    
    # Convert PDF to images
    return convert_from_path(pdf_path, **kwargs)


def get_poppler_install_instructions():
    """
    Get platform-specific installation instructions for Poppler.
    
    Returns:
        String with installation instructions
    """
    system = platform.system()
    
    if system == 'Windows':
        return (
            "Poppler Installation for Windows:\n\n"
            "1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/\n"
            "2. Extract to: C:\\Program Files\\poppler\n"
            "3. Add bin folder to system PATH: C:\\Program Files\\poppler\\Library\\bin\n"
            "4. Restart your application"
        )
    elif system == 'Darwin':  # macOS
        return (
            "Poppler Installation for macOS:\n\n"
            "Using Homebrew:\n"
            "  brew install poppler\n\n"
            "Using MacPorts:\n"
            "  sudo port install poppler"
        )
    elif system == 'Linux':
        return (
            "Poppler Installation for Linux:\n\n"
            "Debian/Ubuntu:\n"
            "  sudo apt-get install poppler-utils\n\n"
            "Fedora/RHEL:\n"
            "  sudo dnf install poppler-utils\n\n"
            "Arch Linux:\n"
            "  sudo pacman -S poppler"
        )
    else:
        return "Please install Poppler using your system's package manager."

