#!/usr/bin/env python3
"""Check QR identity against the printed roll number on every OMR PDF page."""

import argparse
import contextlib
import io
import os
import re
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from pdf2image import pdfinfo_from_path

from pdf_utils import convert_pdf_with_poppler, find_poppler_path
from pipeline.omr_qr import OmrQrReader
from pipeline.roll_number_extraction_stage import RollNumberExtractionStage


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = PROJECT_ROOT / "tests" / "test_omr_with_qr_code.pdf"


class RollOcrProcessor:
    """Minimum processor surface required by RollNumberExtractionStage."""


def normalize_roll(value) -> str:
    if value is None:
        return ""
    normalized = str(value).strip().upper()
    normalized = re.sub(r"[\s_]+", "", normalized)
    return re.sub(r"[‐‑‒–—−]", "-", normalized)


def qr_roll_number(qr_data) -> str:
    exam_roll = normalize_roll(qr_data.exam_roll)
    exam_roll_number = normalize_roll(qr_data.exam_roll_number)
    if not exam_roll or not exam_roll_number:
        return ""
    if exam_roll.endswith("-") or exam_roll_number.startswith("-"):
        return f"{exam_roll}{exam_roll_number}"
    return f"{exam_roll}-{exam_roll_number}"


def parse_page_range(value: Optional[str], page_count: int) -> list[int]:
    if not value:
        return list(range(1, page_count + 1))

    pages = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start > end:
                raise ValueError(f"Invalid descending page range: {part}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))

    invalid_pages = sorted(page for page in pages if page < 1 or page > page_count)
    if invalid_pages:
        raise ValueError(f"Pages outside PDF range 1-{page_count}: {invalid_pages}")
    return sorted(pages)


def get_page_count(pdf_path: Path) -> int:
    poppler_path = None
    if os.name == "nt":
        found, poppler_path = find_poppler_path()
        if not found:
            raise RuntimeError("Poppler was not found; see the PDF prerequisites in README.md")
    return int(pdfinfo_from_path(str(pdf_path), poppler_path=poppler_path)["Pages"])


def detect_markers(image: np.ndarray) -> tuple[list[int], list[tuple[int, int]]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is None:
        return [], []

    detected_ids = ids.flatten().tolist()
    midpoints = [
        tuple(np.mean(marker_corners[0], axis=0).astype(int))
        for marker_corners in corners
    ]
    return detected_ids, midpoints


def scan_roll_number(
    image: np.ndarray,
    roll_stage: RollNumberExtractionStage,
    verbose: bool,
) -> tuple[Optional[str], str]:
    detected_ids, marker_midpoints = detect_markers(image)
    detection_info = {
        "detected_ids": detected_ids,
        "marker_midpoints": marker_midpoints,
    }

    output = io.StringIO()
    stream = sys.stdout if verbose else output
    with contextlib.redirect_stdout(stream):
        roll_number, extracted_text, _ = roll_stage._extract_roll_number_with_markers(
            image,
            detection_info,
            detected_ids,
        )
    return roll_number, extracted_text


def process_page(
    pdf_path: Path,
    page_number: int,
    dpi: int,
    qr_reader: OmrQrReader,
    roll_stage: RollNumberExtractionStage,
    verbose: bool,
) -> dict:
    pages = convert_pdf_with_poppler(
        str(pdf_path),
        dpi=dpi,
        first_page=page_number,
        last_page=page_number,
        fmt="png",
        thread_count=1,
    )
    if not pages:
        return {"page": page_number, "status": "render_failed"}

    image = cv2.cvtColor(np.array(pages[0].convert("RGB")), cv2.COLOR_RGB2BGR)
    qr_result = qr_reader.read([(f"page_{page_number}", image)])
    scanned_roll, ocr_text = scan_roll_number(image, roll_stage, verbose)

    expected_roll = qr_roll_number(qr_result.data) if qr_result.is_valid else ""
    normalized_scanned = normalize_roll(scanned_roll)
    matched = bool(expected_roll and normalized_scanned == normalize_roll(expected_roll))

    if not qr_result.is_valid:
        status = qr_result.status.value
    elif not scanned_roll:
        status = "roll_unreadable"
    elif matched:
        status = "match"
    else:
        status = "mismatch"

    return {
        "page": page_number,
        "status": status,
        "qr_status": qr_result.status.value,
        "expected_roll": expected_roll,
        "scanned_roll": scanned_roll or "",
        "ocr_text": ocr_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare each OMR page's QR roll identity with its OCR-scanned roll number."
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        type=Path,
        default=DEFAULT_PDF,
        help=f"PDF to test (default: {DEFAULT_PDF})",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI (default: 300)")
    parser.add_argument(
        "--pages",
        help='Pages to test, for example "1", "1-10", or "1,5,9-12"',
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output from the existing roll OCR implementation",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path.resolve()
    if not pdf_path.is_file():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if args.dpi < 72:
        print("ERROR: --dpi must be at least 72", file=sys.stderr)
        return 2

    try:
        page_count = get_page_count(pdf_path)
        page_numbers = parse_page_range(args.pages, page_count)
    except (KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"PDF: {pdf_path}")
    print(f"Pages: {len(page_numbers)} of {page_count} | DPI: {args.dpi}")
    print("-" * 78)

    qr_reader = OmrQrReader()
    roll_stage = RollNumberExtractionStage(RollOcrProcessor())
    counts = {"match": 0, "mismatch": 0, "qr_failure": 0, "roll_unreadable": 0}

    for page_number in page_numbers:
        try:
            result = process_page(
                pdf_path,
                page_number,
                args.dpi,
                qr_reader,
                roll_stage,
                args.verbose,
            )
        except Exception as error:
            result = {"page": page_number, "status": "error", "error": str(error)}

        status = result["status"]
        if status == "match":
            counts["match"] += 1
        elif status == "mismatch":
            counts["mismatch"] += 1
        elif status == "roll_unreadable":
            counts["roll_unreadable"] += 1
        else:
            counts["qr_failure"] += 1

        expected = result.get("expected_roll", "-")
        scanned = result.get("scanned_roll", "-")
        print(
            f"Page {page_number:>3}: {status:<20} "
            f"QR={expected or '-':<22} OCR={scanned or '-'}"
        )
        if result.get("error"):
            print(f"          Error: {result['error']}")

    print("-" * 78)
    print(
        f"Summary: matched={counts['match']}, mismatched={counts['mismatch']}, "
        f"roll_unreadable={counts['roll_unreadable']}, qr/errors={counts['qr_failure']}"
    )

    failures = counts["mismatch"] + counts["roll_unreadable"] + counts["qr_failure"]
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())