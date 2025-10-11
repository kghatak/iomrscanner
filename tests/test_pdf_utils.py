"""
Test script for PDF utilities with Poppler detection.
This script tests the new pdf_utils module to ensure it properly handles
Poppler detection on Windows and other platforms.
"""
import os
import sys

# Add parent directory to path to import pdf_utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_utils import find_poppler_path, get_poppler_install_instructions, convert_pdf_with_poppler
import platform


def test_poppler_detection():
    """Test Poppler path detection."""
    print("=" * 60)
    print("Testing Poppler Detection")
    print("=" * 60)
    
    system = platform.system()
    print(f"Operating System: {system}")
    print()
    
    found, poppler_path = find_poppler_path()
    
    if found:
        if poppler_path:
            print(f"✅ Poppler found at: {poppler_path}")
            # Verify the path exists
            if os.path.exists(poppler_path):
                print(f"✅ Path exists and is accessible")
                # Check for key executables
                if system == 'Windows':
                    pdfinfo = os.path.join(poppler_path, "pdfinfo.exe")
                    pdftoppm = os.path.join(poppler_path, "pdftoppm.exe")
                else:
                    pdfinfo = os.path.join(poppler_path, "pdfinfo")
                    pdftoppm = os.path.join(poppler_path, "pdftoppm")
                
                if os.path.exists(pdfinfo):
                    print(f"✅ Found pdfinfo")
                if os.path.exists(pdftoppm):
                    print(f"✅ Found pdftoppm")
            else:
                print(f"❌ Path does not exist!")
        else:
            print("✅ Poppler found in system PATH")
    else:
        print("❌ Poppler not found!")
        print("\nInstallation Instructions:")
        print(get_poppler_install_instructions())
    
    return found


def test_pdf_conversion(pdf_path=None):
    """Test PDF to image conversion."""
    print("\n" + "=" * 60)
    print("Testing PDF Conversion")
    print("=" * 60)
    
    if not pdf_path:
        # Look for test PDF in test_input_pdf folder
        test_pdf_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_input_pdf"
        )
        
        # Try to find a PDF file
        if os.path.exists(test_pdf_dir):
            for file in os.listdir(test_pdf_dir):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(test_pdf_dir, file)
                    break
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("⚠️  No PDF file found for testing. Skipping conversion test.")
        print("   To test conversion, provide a PDF path:")
        print(f"   python {os.path.basename(__file__)} <path-to-pdf>")
        return False
    
    print(f"PDF File: {pdf_path}")
    
    try:
        print("Attempting to convert PDF to images...")
        images = convert_pdf_with_poppler(pdf_path)
        print(f"✅ Successfully converted PDF!")
        print(f"   Number of pages: {len(images)}")
        print(f"   First page size: {images[0].size}")
        return True
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Please install pdf2image: pip install pdf2image")
        return False
    except RuntimeError as e:
        print(f"❌ Runtime Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_install_instructions():
    """Test installation instructions."""
    print("\n" + "=" * 60)
    print("Testing Installation Instructions")
    print("=" * 60)
    
    instructions = get_poppler_install_instructions()
    print(instructions)
    
    # Verify instructions are not empty
    if instructions and len(instructions) > 50:
        print("\n✅ Installation instructions generated successfully")
        return True
    else:
        print("\n❌ Installation instructions seem incomplete")
        return False


def main():
    """Run all tests."""
    print("PDF Utils Test Suite")
    print("=" * 60)
    
    # Get PDF path from command line if provided
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    results = []
    
    # Test 1: Poppler detection
    results.append(("Poppler Detection", test_poppler_detection()))
    
    # Test 2: Installation instructions
    results.append(("Installation Instructions", test_install_instructions()))
    
    # Test 3: PDF conversion (only if Poppler is found)
    if results[0][1]:  # If Poppler was found
        results.append(("PDF Conversion", test_pdf_conversion(pdf_path)))
    else:
        print("\n⚠️  Skipping PDF conversion test (Poppler not found)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Please review the output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

