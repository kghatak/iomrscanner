#!/usr/bin/env python3
"""
Create a test image with ArUco markers and a roll number for pipeline testing
"""

import cv2
import numpy as np
import os

def create_test_image_with_roll():
    """Create a test image with ArUco markers and roll number"""
    
    # Image dimensions
    width, height = 1200, 800
    
    # Create white background
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Initialize ArUco dictionary
    try:
        # Try new API first
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        aruco_params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Generate markers
        marker_size = 50
        marker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Position markers in a grid (2 rows, 5 columns)
        margin = 50
        spacing_x = (width - 2 * margin - 5 * marker_size) // 4
        spacing_y = (height - 2 * margin - 2 * marker_size) // 1
        
        positions = []
        # Top row (5 markers)
        for i in range(5):
            x = margin + i * (marker_size + spacing_x)
            y = margin
            positions.append((x, y))
        
        # Bottom row (5 markers)
        for i in range(5):
            x = margin + i * (marker_size + spacing_x)
            y = margin + marker_size + spacing_y
            positions.append((x, y))
        
        # Generate and place markers
        for i, marker_id in enumerate(marker_ids[:len(positions)]):
            try:
                # Try new style first
                marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
            except AttributeError:
                # Fall back to old style
                marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, marker_size)
            
            # Convert marker to 3-channel
            marker_img_3ch = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
            
            # Place marker on image
            x, y = positions[i]
            image[y:y+marker_size, x:x+marker_size] = marker_img_3ch
        
        # Add roll number text in the center
        roll_number = "Roll No: 123456"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 3
        color = (0, 0, 0)  # Black text
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(roll_number, font, font_scale, thickness)
        
        # Calculate position to center the text
        text_x = (width - text_width) // 2
        text_y = height // 2 + text_height // 2
        
        # Add text
        cv2.putText(image, roll_number, (text_x, text_y), font, font_scale, color, thickness)
        
        # Add some additional text
        additional_text = "Test OMR Sheet"
        (text_width2, text_height2), baseline2 = cv2.getTextSize(additional_text, font, 1.0, 2)
        text_x2 = (width - text_width2) // 2
        text_y2 = text_y + 50
        
        cv2.putText(image, additional_text, (text_x2, text_y2), font, 1.0, color, 2)
        
        # Save image
        output_path = "test_images/complete_markers_with_roll.jpg"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)
        
        print(f"✅ Created test image with roll number: {output_path}")
        print(f"📝 Roll number: {roll_number}")
        print(f"🎯 ArUco markers: {marker_ids}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None

if __name__ == "__main__":
    create_test_image_with_roll()
