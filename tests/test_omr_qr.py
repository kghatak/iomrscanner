import json
import os
import tempfile
import unittest

import cv2
import numpy as np
import qrcode

from pipeline.omr_qr import OmrQrData, OmrQrReader, QrStatus, parse_omr_qr_payload
from pipeline.qr_reading_stage import QrReadingStage


VALID_PAYLOAD = {
    "v": "OMR2",
    "s": "STUDENT-42",
    "e": "EXAM-7",
    "r": "ROLL-2026",
    "n": "0042",
}


class OmrQrTests(unittest.TestCase):
    def test_valid_payload_returns_typed_data(self):
        result = parse_omr_qr_payload(json.dumps(VALID_PAYLOAD))

        self.assertEqual(result.status, QrStatus.VALID)
        self.assertIsInstance(result.data, OmrQrData)
        self.assertEqual(result.data.student_code, "STUDENT-42")
        self.assertEqual(result.data.exam_roll_number, "0042")
        self.assertEqual(result.data.full_exam_roll_number, "ROLL-2026-0042")

    def test_malformed_json_is_rejected(self):
        result = parse_omr_qr_payload("{not-json")

        self.assertEqual(result.status, QrStatus.INVALID_JSON)
        self.assertIsNone(result.data)

    def test_wrong_version_is_rejected(self):
        payload = {**VALID_PAYLOAD, "v": "OMR1"}

        result = parse_omr_qr_payload(json.dumps(payload))

        self.assertEqual(result.status, QrStatus.UNSUPPORTED_VERSION)

    def test_missing_required_fields_are_rejected(self):
        for missing_field in ("s", "e", "r", "n"):
            with self.subTest(missing_field=missing_field):
                payload = {
                    key: value
                    for key, value in VALID_PAYLOAD.items()
                    if key != missing_field
                }

                result = parse_omr_qr_payload(json.dumps(payload))

                self.assertEqual(result.status, QrStatus.INVALID_PAYLOAD)

    def test_blank_image_reports_not_detected(self):
        image = np.full((800, 600, 3), 255, dtype=np.uint8)

        result = OmrQrReader().read([("original", image)])

        self.assertEqual(result.status, QrStatus.NOT_DETECTED)

    def test_detected_but_undecodable_qr_is_distinguished(self):
        class UndecodableDetector:
            def detectAndDecode(self, image):
                points = np.zeros((1, 4, 2), dtype=np.float32)
                return "", points, None

        image = np.full((100, 100, 3), 255, dtype=np.uint8)

        result = OmrQrReader(detector=UndecodableDetector()).read(
            [("original", image)]
        )

        self.assertEqual(result.status, QrStatus.DETECTED_UNREADABLE)

    def test_qr_in_top_right_region_is_decoded(self):
        qr_image = qrcode.make(json.dumps(VALID_PAYLOAD)).convert("RGB")
        qr_array = cv2.cvtColor(np.array(qr_image), cv2.COLOR_RGB2BGR)
        canvas = np.full((1200, 900, 3), 255, dtype=np.uint8)
        qr_height, qr_width = qr_array.shape[:2]
        canvas[30:30 + qr_height, -qr_width - 30:-30] = qr_array

        result = OmrQrReader().read([("original", canvas)])

        self.assertEqual(result.status, QrStatus.VALID)
        self.assertEqual(
            result.data,
            OmrQrData("STUDENT-42", "EXAM-7", "ROLL-2026", "0042"),
        )

    def test_qr_stage_is_non_fatal_and_exposes_identity(self):
        qr_image = qrcode.make(json.dumps(VALID_PAYLOAD)).convert("RGB")
        qr_array = cv2.cvtColor(np.array(qr_image), cv2.COLOR_RGB2BGR)

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "sheet.png")
            cv2.imwrite(image_path, qr_array)
            stage_result = QrReadingStage(object()).process(
                image_path,
                {"original_image_path": image_path},
            )

        self.assertTrue(stage_result["success"])
        self.assertEqual(stage_result["qr_status"], QrStatus.VALID.value)
        self.assertEqual(stage_result["qr_identity"]["student_code"], "STUDENT-42")
        self.assertEqual(stage_result["qr_studentID"], "STUDENT-42")
        self.assertEqual(stage_result["qr_exam_roll_number"], "ROLL-2026-0042")

    def test_qr_stage_does_not_expose_identifiers_when_qr_is_invalid(self):
        blank_image = np.full((200, 200, 3), 255, dtype=np.uint8)

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "blank.png")
            cv2.imwrite(image_path, blank_image)
            stage_result = QrReadingStage(object()).process(
                image_path,
                {"original_image_path": image_path},
            )

        self.assertEqual(stage_result["qr_status"], QrStatus.NOT_DETECTED.value)
        self.assertNotIn("qr_studentID", stage_result)
        self.assertNotIn("qr_exam_roll_number", stage_result)


if __name__ == "__main__":
    unittest.main()