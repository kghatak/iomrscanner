#!/usr/bin/env python3
"""Typed QR payload decoding for OMR sheets."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Tuple

import cv2
import numpy as np


class QrStatus(str, Enum):
    NOT_DETECTED = "not_detected"
    DETECTED_UNREADABLE = "detected_unreadable"
    INVALID_JSON = "invalid_json"
    INVALID_PAYLOAD = "invalid_payload"
    UNSUPPORTED_VERSION = "unsupported_version"
    VALID = "valid"


@dataclass(frozen=True)
class OmrQrData:
    student_code: str
    exam_code: str
    exam_roll: Any
    exam_roll_number: Any
    version: str = "OMR2"

    @property
    def full_exam_roll_number(self) -> str:
        exam_roll = str(self.exam_roll).strip()
        exam_roll_number = str(self.exam_roll_number).strip()
        if exam_roll.endswith("-") or exam_roll_number.startswith("-"):
            return f"{exam_roll}{exam_roll_number}"
        return f"{exam_roll}-{exam_roll_number}"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "student_code": self.student_code,
            "exam_code": self.exam_code,
            "exam_roll": self.exam_roll,
            "exam_roll_number": self.exam_roll_number,
        }


@dataclass(frozen=True)
class OmrQrResult:
    status: QrStatus
    data: Optional[OmrQrData] = None
    source: Optional[str] = None
    message: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.status == QrStatus.VALID and self.data is not None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data.as_dict() if self.data else None,
            "source": self.source,
            "message": self.message,
        }


def parse_omr_qr_payload(payload: str) -> OmrQrResult:
    try:
        parsed = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return OmrQrResult(QrStatus.INVALID_JSON, message="QR payload is not valid JSON")

    if not isinstance(parsed, dict):
        return OmrQrResult(QrStatus.INVALID_PAYLOAD, message="QR payload must be a JSON object")

    if parsed.get("v") != "OMR2":
        return OmrQrResult(
            QrStatus.UNSUPPORTED_VERSION,
            message="QR payload version is not supported",
        )

    if not isinstance(parsed.get("s"), str) or not parsed["s"].strip():
        return OmrQrResult(QrStatus.INVALID_PAYLOAD, message="StudentCode is required")
    if not isinstance(parsed.get("e"), str) or not parsed["e"].strip():
        return OmrQrResult(QrStatus.INVALID_PAYLOAD, message="ExamCode is required")
    if "r" not in parsed or parsed["r"] is None:
        return OmrQrResult(QrStatus.INVALID_PAYLOAD, message="ExamRoll is required")
    if "n" not in parsed or parsed["n"] is None:
        return OmrQrResult(QrStatus.INVALID_PAYLOAD, message="ExamRollNumber is required")

    return OmrQrResult(
        QrStatus.VALID,
        data=OmrQrData(
            student_code=parsed["s"].strip(),
            exam_code=parsed["e"].strip(),
            exam_roll=parsed["r"],
            exam_roll_number=parsed["n"],
        ),
    )


class OmrQrReader:
    """Decode an OMR identity QR using OpenCV's QRCodeDetector."""

    def __init__(self, detector=None):
        self.detector = detector or cv2.QRCodeDetector()

    def read(self, images: Iterable[Tuple[str, np.ndarray]]) -> OmrQrResult:
        best_result = OmrQrResult(QrStatus.NOT_DETECTED, message="No QR code detected")
        result_priority = {
            QrStatus.NOT_DETECTED: 0,
            QrStatus.DETECTED_UNREADABLE: 1,
            QrStatus.INVALID_JSON: 2,
            QrStatus.INVALID_PAYLOAD: 3,
            QrStatus.UNSUPPORTED_VERSION: 4,
            QrStatus.VALID: 5,
        }

        for source_name, image in images:
            if image is None or image.size == 0:
                continue
            for variant_name, candidate in self._candidate_images(image):
                try:
                    decoded, points, _ = self.detector.detectAndDecode(candidate)
                except cv2.error:
                    continue

                candidate_source = f"{source_name}:{variant_name}"
                if decoded:
                    parsed_result = parse_omr_qr_payload(decoded)
                    parsed_result = OmrQrResult(
                        status=parsed_result.status,
                        data=parsed_result.data,
                        source=candidate_source,
                        message=parsed_result.message,
                    )
                    if parsed_result.is_valid:
                        return parsed_result
                    if result_priority[parsed_result.status] > result_priority[best_result.status]:
                        best_result = parsed_result
                elif points is not None and result_priority[best_result.status] < 1:
                    best_result = OmrQrResult(
                        QrStatus.DETECTED_UNREADABLE,
                        source=candidate_source,
                        message="QR code detected but could not be decoded",
                    )

        return best_result

    def _candidate_images(self, image: np.ndarray):
        height, width = image.shape[:2]
        top_right = image[0:max(1, int(height * 0.5)), int(width * 0.5):width]

        for region_name, region in (("full", image), ("top_right", top_right)):
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if region.ndim == 3 else region
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
            variants = (("color", region), ("gray", gray), ("contrast", clahe))

            for variant_name, variant in variants:
                yield f"{region_name}_{variant_name}", variant
                for scale in (1.5, 2.0):
                    enlarged = cv2.resize(
                        variant,
                        None,
                        fx=scale,
                        fy=scale,
                        interpolation=cv2.INTER_CUBIC,
                    )
                    yield f"{region_name}_{variant_name}_{scale:g}x", enlarged