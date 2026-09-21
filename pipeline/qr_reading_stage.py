#!/usr/bin/env python3
"""Non-fatal QR identity reading stage."""

import os
from typing import Any, Dict

import cv2

from .base_stage import PipelineStage
from .omr_qr import OmrQrReader, OmrQrResult, QrStatus


class QrReadingStage(PipelineStage):
    def get_stage_name(self) -> str:
        return "qr_reading"

    def get_stage_description(self) -> str:
        return "Read and validate OMR identity QR code"

    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        image_paths = [
            ("original", context.get("original_image_path")),
            ("current", image_path),
            ("perspective_corrected", context.get("perspective_corrected_image_path")),
            ("corrected", context.get("corrected_image_path")),
        ]
        images = []
        seen_paths = set()

        try:
            for source_name, candidate_path in image_paths:
                if not candidate_path:
                    continue
                normalized_path = os.path.abspath(candidate_path)
                if normalized_path in seen_paths:
                    continue
                seen_paths.add(normalized_path)
                candidate_image = cv2.imread(candidate_path)
                if candidate_image is not None:
                    images.append((source_name, candidate_image))

            qr_result = OmrQrReader().read(images)
        except Exception as error:
            qr_result = OmrQrResult(
                status=QrStatus.DETECTED_UNREADABLE,
                message=f"QR reading failed: {type(error).__name__}",
            )

        print(f"[{self.__class__.__name__}] QR status: {qr_result.status.value}")

        result = self.create_stage_result(
            success=True,
            qr_status=qr_result.status.value,
            qr_result=qr_result,
        )
        if qr_result.is_valid:
            result["qr_identity"] = qr_result.data.as_dict()
            result["qr_studentID"] = qr_result.data.student_code
            result["qr_exam_roll_number"] = qr_result.data.full_exam_roll_number

        return result