#!/usr/bin/env python3
"""
Test script for PDF to image extraction using pdf2image
"""
import os
import sys

def test_pdf2image(pdf_path=None):
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("pdf2image is not installed. Please install it with 'pip install pdf2image'.")
        return False
    if pdf_path is None:
        print("No PDF path provided. Usage: python test_pdf2image.py <file.pdf>")
        return False
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        return False
    output_folder = os.path.splitext(pdf_path)[0] + "_test_pages"
    os.makedirs(output_folder, exist_ok=True)
    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            img_path = os.path.join(output_folder, f"page_{i+1}.png")
            img.save(img_path, "PNG")
            print(f"Saved: {img_path}")
        print(f"Extracted {len(images)} pages from {pdf_path} to {output_folder}")
        return True
    except Exception as e:
        print(f"Error extracting images: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf2image.py <file.pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    success = test_pdf2image(pdf_path)
    print(f"Test {'PASSED' if success else 'FAILED'}")
