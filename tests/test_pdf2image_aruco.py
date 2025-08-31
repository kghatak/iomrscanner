#!/usr/bin/env python3
"""
Test: Generate a multi-page PDF with ArUco markers 1-20, extract images, and verify detection.
"""
import os
import cv2
import numpy as np
from fpdf import FPDF
from pdf2image import convert_from_path

def generate_aruco_marker_images(marker_ids, size=200, out_dir="test_pdfs/aruco_imgs"):
    print(f"[INFO] Generating ArUco marker images for IDs: {marker_ids} (size={size}) in '{out_dir}'...")
    os.makedirs(out_dir, exist_ok=True)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    image_paths = []
    for marker_id in marker_ids:
        print(f"  - Generating marker ID {marker_id}")
        img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
        img_path = os.path.join(out_dir, f"aruco_{marker_id}.png")
        cv2.imwrite(img_path, img)
        print(f"    Saved: {img_path}")
        image_paths.append(img_path)
    print(f"[INFO] Generated {len(image_paths)} marker images.")
    return image_paths

def create_pdf_with_images(image_paths, pdf_path):
    print(f"[INFO] Creating PDF '{pdf_path}' with {len(image_paths)} images...")
    pdf = FPDF()
    for img_path in image_paths:
        print(f"  - Adding image to PDF: {img_path}")
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        marker_id = os.path.splitext(os.path.basename(img_path))[0].split('_')[-1]
        pdf.cell(0, 10, f"ArUco Marker ID: {marker_id}", ln=1)
        pdf.image(img_path, x=10, y=20, w=60, h=60)
    pdf.output(pdf_path)
    print(f"[INFO] PDF created: {pdf_path}")

def extract_images_from_pdf(pdf_path, out_dir):
    print(f"[INFO] Extracting images from PDF '{pdf_path}' into '{out_dir}'...")
    os.makedirs(out_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(out_dir, f"page_{i+1}.png")
        img.save(img_path, "PNG")
        print(f"  - Extracted: {img_path}")
        image_paths.append(img_path)
    print(f"[INFO] Extracted {len(image_paths)} images from PDF.")
    return image_paths

def detect_aruco_in_images(image_paths):
    print(f"[INFO] Detecting ArUco markers in {len(image_paths)} images...")
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    results = {}
    for img_path in image_paths:
        print(f"  - Processing: {img_path}")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        corners, ids, _ = detector.detectMarkers(img)
        found = ids.flatten().tolist() if ids is not None else []
        print(f"    Detected IDs: {found}")
        results[img_path] = found
    print(f"[INFO] Detection complete.")
    return results

def main():
    base_dir = "test_pdfs"
    marker_ids = list(range(1, 21))
    print("========== PDF2IMAGE ARUCO TEST ==========")
    print("Step 1: Generate ArUco marker images")
    aruco_imgs = generate_aruco_marker_images(marker_ids, out_dir=os.path.join(base_dir, "aruco_imgs"))
    pdf_path = os.path.join(base_dir, "test_pdf_aruco.pdf")
    print("\nStep 2: Create PDF with marker images")
    create_pdf_with_images(aruco_imgs, pdf_path)
    print("\nStep 3: Extract images from PDF")
    extracted_imgs = extract_images_from_pdf(pdf_path, os.path.join(base_dir, "pdf_pages"))
    print("\nStep 4: Detect ArUco markers in extracted images")
    results = detect_aruco_in_images(extracted_imgs)
    print("\nStep 5: Summary and PASS/FAIL check")
    all_passed = True
    for i, marker_id in enumerate(marker_ids):
        found = results[extracted_imgs[i]]
        if marker_id in found:
            print(f"PASS: Marker {marker_id} found on page {i+1}")
        else:
            print(f"FAIL: Marker {marker_id} NOT found on page {i+1}")
            all_passed = False
    print("\n========== TEST", "PASSED ==========" if all_passed else "FAILED ==========")

if __name__ == "__main__":
    main()
