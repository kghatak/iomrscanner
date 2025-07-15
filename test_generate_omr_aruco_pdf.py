#!/usr/bin/env python3
"""
Generate a dummy multi-page OMR sheet PDF with 100 questions and ArUco markers (pixel size 10) at various places,
then extract the pages and test ArUco marker detection on each page.
"""
import os
from fpdf import FPDF
import cv2
import numpy as np
from pdf2image import convert_from_path

# Settings
NUM_QUESTIONS = 100
QUESTIONS_PER_PAGE = 25
NUM_PAGES = (NUM_QUESTIONS + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE
ARUCO_MARKER_IDS = [1, 2, 3, 4]
ARUCO_SIZE = 12  # pixels
PDF_DIR = "test_pdfs"
PDF_PATH = os.path.join(PDF_DIR, "omr_aruco_test.pdf")
IMG_TMP_DIR = os.path.join(PDF_DIR, "omr_tmp")
PAGE_IMG_DIR = os.path.join(PDF_DIR, "omr_pages")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(IMG_TMP_DIR, exist_ok=True)
os.makedirs(PAGE_IMG_DIR, exist_ok=True)

def generate_aruco_marker_images(marker_ids, size, out_dir):
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    img_paths = {}
    for marker_id in marker_ids:
        img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
        img_path = os.path.join(out_dir, f"aruco_{marker_id}_{size}.png")
        cv2.imwrite(img_path, img)
        img_paths[marker_id] = img_path
        print(f"[INFO] Generated ArUco marker {marker_id} at {img_path}")
    return img_paths

def draw_omr_page(pdf, page_num, aruco_imgs):
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Dummy OMR Sheet - Page {page_num+1}", ln=1)
    # Place ArUco markers at corners
    margin = 5
    positions = [
        (margin, margin),  # top-left
        (200 - margin - ARUCO_SIZE, margin),  # top-right
        (margin, 290 - margin - ARUCO_SIZE),  # bottom-left
        (200 - margin - ARUCO_SIZE, 290 - margin - ARUCO_SIZE)  # bottom-right
    ]
    for (x, y), marker_id in zip(positions, ARUCO_MARKER_IDS):
        pdf.image(aruco_imgs[marker_id], x=x, y=y, w=ARUCO_SIZE, h=ARUCO_SIZE)
    # Draw OMR bubbles (simulate with rectangles)
    start_y = 30
    bubble_w, bubble_h = 6, 6
    gap_y = 10
    for i in range(QUESTIONS_PER_PAGE):
        q_num = page_num * QUESTIONS_PER_PAGE + i + 1
        if q_num > NUM_QUESTIONS:
            break
        y = start_y + i * gap_y
        pdf.set_xy(20, y)
        pdf.cell(20, bubble_h, f"Q{q_num:03d}")
        # Draw 4 options
        for opt in range(4):
            x = 50 + opt * (bubble_w + 8)
            pdf.rect(x, y, bubble_w, bubble_h)
            pdf.set_xy(x + bubble_w + 1, y)
            pdf.cell(5, bubble_h, chr(65 + opt))

def extract_images_from_pdf(pdf_path, out_dir):
    print(f"[INFO] Extracting images from PDF '{pdf_path}' into '{out_dir}'...")
    os.makedirs(out_dir, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=600)
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
    for i, img_path in enumerate(image_paths):
        print(f"  - Processing: {img_path}")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        corners, ids, _ = detector.detectMarkers(img)
        found = ids.flatten().tolist() if ids is not None else []
        print(f"    Detected IDs: {found}")
        # Check if all expected marker IDs are present
        missing = [mid for mid in expected_ids if mid not in found]
        if not missing:
            print(f"    PASS: All expected markers {expected_ids} found on page {i+1}")
        else:
            print(f"    FAIL: Missing markers {missing} on page {i+1}")
            all_passed = False
    print("\n========== TEST", "PASSED ==========" if all_passed else "FAILED ==========")
    return all_passed

def main():
    print(f"Generating ArUco marker images (size={ARUCO_SIZE})...")
    aruco_imgs = generate_aruco_marker_images(ARUCO_MARKER_IDS, ARUCO_SIZE, IMG_TMP_DIR)
    print(f"Creating OMR PDF with {NUM_PAGES} pages and {NUM_QUESTIONS} questions...")
    pdf = FPDF(unit="mm", format=(210, 297))  # A4 size
    for page_num in range(NUM_PAGES):
        draw_omr_page(pdf, page_num, aruco_imgs)
    pdf.output(PDF_PATH)
    print(f"PDF saved to: {PDF_PATH}")
    print("\nExtracting images from PDF and testing ArUco detection...")
    page_imgs = extract_images_from_pdf(PDF_PATH, PAGE_IMG_DIR)
    detect_aruco_in_images(page_imgs, ARUCO_MARKER_IDS)
    print("Done.")

if __name__ == "__main__":
    main()
