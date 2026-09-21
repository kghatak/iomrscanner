#!/usr/bin/env python3
"""Extended QR, OCR, and ArUco validation for every OMR PDF page."""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pytesseract

from pdf_utils import convert_pdf_with_poppler
from pipeline.omr_qr import OmrQrReader
from pipeline.roll_number_extraction_stage import RollNumberExtractionStage
from test_qr_roll_pdf import (
    DEFAULT_PDF,
    RollOcrProcessor,
    detect_markers,
    get_page_count,
    normalize_roll,
    parse_page_range,
    qr_roll_number,
    scan_roll_number,
)


DEFAULT_REPORT_NAME = "test_omr_with_qr_code_report.txt"


def normalize_student_id(value) -> str:
    if value is None:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def extract_student_id(ocr_text: str) -> str:
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    label_pattern = re.compile(r"STUDENT\s*(?:ID|1D)\s*[:\-]?\s*(.*)", re.IGNORECASE)
    identifier_pattern = re.compile(r"\b([A-Z]{2,}[A-Z0-9]{6,})\b", re.IGNORECASE)

    for index, line in enumerate(lines):
        label_match = label_pattern.search(line)
        if not label_match:
            continue

        candidates = [label_match.group(1)]
        if index + 1 < len(lines):
            candidates.append(lines[index + 1])

        for candidate in candidates:
            identifier_match = identifier_pattern.search(candidate)
            if identifier_match:
                return identifier_match.group(1).upper()

    return ""


def full_page_student_id(image: np.ndarray) -> tuple[str, str]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ocr_text = pytesseract.image_to_string(gray, config="--psm 11")
    return extract_student_id(ocr_text), ocr_text


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
        return {"page": page_number, "error": "PDF page could not be rendered"}

    image = cv2.cvtColor(np.array(pages[0].convert("RGB")), cv2.COLOR_RGB2BGR)
    detected_ids, _ = detect_markers(image)
    qr_result = qr_reader.read([(f"page_{page_number}", image)])
    scanned_roll, _ = scan_roll_number(image, roll_stage, verbose)
    scanned_student_id, _ = full_page_student_id(image)

    expected_roll = qr_roll_number(qr_result.data) if qr_result.is_valid else ""
    expected_student_id = qr_result.data.student_code if qr_result.is_valid else ""
    roll_match = bool(
        expected_roll
        and scanned_roll
        and normalize_roll(expected_roll) == normalize_roll(scanned_roll)
    )
    student_id_match = bool(
        expected_student_id
        and scanned_student_id
        and normalize_student_id(expected_student_id)
        == normalize_student_id(scanned_student_id)
    )

    return {
        "page": page_number,
        "qr_status": qr_result.status.value,
        "qr_roll": expected_roll,
        "ocr_roll": scanned_roll or "",
        "roll_match": roll_match,
        "qr_student_id": expected_student_id,
        "ocr_student_id": scanned_student_id,
        "student_id_match": student_id_match,
        "aruco_count": len(detected_ids),
        "aruco_ids": sorted(detected_ids),
    }


def format_page_result(result: dict) -> str:
    if result.get("error"):
        return f"Page {result['page']:>3}: ERROR | {result['error']}"

    roll_status = "MATCH" if result["roll_match"] else "MISMATCH"
    student_status = "MATCH" if result["student_id_match"] else "MISMATCH"
    return (
        f"Page {result['page']:>3}: "
        f"Roll={roll_status} (QR={result['qr_roll'] or '-'}, OCR={result['ocr_roll'] or '-'}) | "
        f"StudentID={student_status} "
        f"(QR={result['qr_student_id'] or '-'}, OCR={result['ocr_student_id'] or '-'}) | "
        f"ArUco={result['aruco_count']} IDs={result['aruco_ids']} | "
        f"QRStatus={result['qr_status']}"
    )


def build_summary(results: list[dict]) -> dict:
    total = len(results)
    roll_matches = sum(result.get("roll_match", False) for result in results)
    student_matches = sum(result.get("student_id_match", False) for result in results)
    errors = sum("error" in result for result in results)
    valid_qr = sum(result.get("qr_status") == "valid" for result in results)
    marker_counts = [result["aruco_count"] for result in results if "aruco_count" in result]

    return {
        "total": total,
        "roll_matches": roll_matches,
        "student_matches": student_matches,
        "valid_qr": valid_qr,
        "errors": errors,
        "aruco_min": min(marker_counts) if marker_counts else 0,
        "aruco_max": max(marker_counts) if marker_counts else 0,
        "aruco_average": sum(marker_counts) / len(marker_counts) if marker_counts else 0.0,
    }


def format_summary(summary: dict) -> list[str]:
    total = summary["total"]
    roll_rate = summary["roll_matches"] / total * 100 if total else 0.0
    student_rate = summary["student_matches"] / total * 100 if total else 0.0
    qr_rate = summary["valid_qr"] / total * 100 if total else 0.0
    return [
        f"Pages tested: {total}",
        f"Roll matches: {summary['roll_matches']}/{total} ({roll_rate:.2f}%)",
        f"Student ID matches: {summary['student_matches']}/{total} ({student_rate:.2f}%)",
        f"Valid QR payloads: {summary['valid_qr']}/{total} ({qr_rate:.2f}%)",
        (
            "ArUco markers per page: "
            f"min={summary['aruco_min']}, max={summary['aruco_max']}, "
            f"average={summary['aruco_average']:.2f}"
        ),
        f"Processing errors: {summary['errors']}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate QR identity, full-page OCR Student ID, roll OCR, and ArUco markers."
    )
    parser.add_argument("pdf_path", nargs="?", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--pages", help='Pages such as "1", "1-10", or "1,5,9-12"')
    parser.add_argument(
        "--report",
        type=Path,
        help="Report path (default: beside the PDF as test_omr_with_qr_code_report.txt)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed existing roll OCR output",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path.resolve()
    if not pdf_path.is_file():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        return 2

    try:
        page_count = get_page_count(pdf_path)
        page_numbers = parse_page_range(args.pages, page_count)
    except (KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    report_path = (
        args.report.resolve()
        if args.report
        else pdf_path.with_name(DEFAULT_REPORT_NAME)
    )
    qr_reader = OmrQrReader()
    roll_stage = RollNumberExtractionStage(RollOcrProcessor())
    results = []

    print(f"Testing {len(page_numbers)} of {page_count} pages at 300 DPI")
    for page_number in page_numbers:
        try:
            result = process_page(
                pdf_path,
                page_number,
                300,
                qr_reader,
                roll_stage,
                args.verbose,
            )
        except Exception as error:
            result = {"page": page_number, "error": str(error)}
        results.append(result)
        print(format_page_result(result))

    summary = build_summary(results)
    summary_lines = format_summary(summary)
    report_lines = [
        "Extended OMR QR/OCR/ArUco Test Report",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"PDF: {pdf_path}",
        "DPI: 300",
        "=" * 120,
        *[format_page_result(result) for result in results],
        "=" * 120,
        "Summary",
        *summary_lines,
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("-" * 80)
    for line in summary_lines:
        print(line)
    print(f"Report: {report_path}")

    all_passed = (
        summary["roll_matches"] == summary["total"]
        and summary["student_matches"] == summary["total"]
        and summary["valid_qr"] == summary["total"]
        and summary["errors"] == 0
    )
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())