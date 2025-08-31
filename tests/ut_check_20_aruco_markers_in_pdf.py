#!/usr/bin/env python3
"""
Test script to check for the presence of all 20 ArUco markers (IDs 1-20) on each page of a PDF in the test_input_pdf folder.
Prints a summary of which markers are found/missing per page.
"""
import os
import sys
import cv2
import numpy as np
from pdf2image import convert_from_path

# Settings
INPUT_DIR = "test_input_pdf"
OUTPUT_DIR = os.path.join(INPUT_DIR, "pages")
ARUCO_MARKER_IDS = list(range(1, 21))
DPI = 300

os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_pdf_file(input_dir):
    pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"[ERROR] No PDF found in {input_dir}")
        sys.exit(1)
    if len(pdfs) > 1:
        print(f"[WARNING] Multiple PDFs found in {input_dir}, using the first: {pdfs[0]}")
    return os.path.join(input_dir, pdfs[0])

def extract_images_from_pdf(pdf_path, out_dir, dpi):
    print(f"[INFO] Extracting images from PDF '{pdf_path}' into '{out_dir}' at {dpi} DPI...")
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(out_dir, f"page_{i+1}.png")
        img.save(img_path, "PNG")
        print(f"  - Extracted: {img_path}")
        image_paths.append(img_path)
    print(f"[INFO] Extracted {len(image_paths)} images from PDF.")
    return image_paths

def detect_aruco_in_images(image_paths, expected_ids):
    print(f"[INFO] Detecting ArUco markers in {len(image_paths)} images...")
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    all_passed = True
    summary = []
    for i, img_path in enumerate(image_paths):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        corners, ids, _ = detector.detectMarkers(img)
        found = ids.flatten().tolist() if ids is not None else []
        missing = [mid for mid in expected_ids if mid not in found]
        summary.append({
            "page": i+1,
            "found": found,
            "missing": missing
        })
        print(f"Page {i+1}: Found {len(found)} markers. IDs: {found}")
        if missing:
            print(f"  MISSING: {missing}")
            all_passed = False
        else:
            print(f"  All {len(expected_ids)} markers present.")
    print("\n========== SUMMARY ==========")
    for s in summary:
        print(f"Page {s['page']}: Found {len(s['found'])}, Missing {len(s['missing'])}")
        if s['missing']:
            print(f"  Missing IDs: {s['missing']}")
    print("\n========== TEST", "PASSED ==========" if all_passed else "FAILED ==========")
    return all_passed

def main():
    pdf_path = find_pdf_file(INPUT_DIR)
    image_paths = extract_images_from_pdf(pdf_path, OUTPUT_DIR, DPI)
    detect_aruco_in_images(image_paths, ARUCO_MARKER_IDS)
    print("Done.")

if __name__ == "__main__":
    main()
