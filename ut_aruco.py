#!/usr/bin/env python3
"""
Test script for ArUco marker detection and image processing
"""

import cv2
import numpy as np
import os
from image_processor import ImageProcessor

def create_test_aruco_image(output_path, marker_ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], image_size=(1200, 800)):
    """
    Create a test image with ArUco markers using DICT_4X4_50 format
    
    Args:
        output_path: Where to save the test image
        marker_ids: List of marker IDs to include (valid range: 0-49 for DICT_4X4_50, default: 0-9 for 10 markers)
        image_size: Tuple of (width, height) for the output image
    """
    # Create a white background
    image = np.ones((image_size[1], image_size[0], 3), dtype=np.uint8) * 255
    
    # Get ArUco dictionary (4x4_50 format)
    try:
        # Try new style first (OpenCV >= 4.7)
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    except AttributeError:
        # Fall back to old style (OpenCV < 4.7)
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    
    # Marker size
    marker_size = 10 # Use small images.
    
    # Positions for 10 markers (2 rows of 5)
    margin = 50
    spacing_x = (image_size[0] - 2 * margin - 5 * marker_size) // 4
    spacing_y = (image_size[1] - 2 * margin - 2 * marker_size) // 1
    
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
            # Try new style first (OpenCV >= 4.7)
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
        except AttributeError:
            # Fall back to old style (OpenCV < 4.7)
            marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, marker_size)
        
        # Convert marker to 3-channel
        marker_img_3ch = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
        
        # Place marker on image
        x, y = positions[i]
        image[y:y+marker_size, x:x+marker_size] = marker_img_3ch
    
    # Add some text in the center
    text = f"Test Image with ArUco Markers: {marker_ids}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
    text_x = (image_size[0] - text_size[0]) // 2
    text_y = image_size[1] // 2
    
    cv2.putText(image, text, (text_x, text_y), font, 0.7, (0, 0, 0), 2)
    
    # Save image
    cv2.imwrite(output_path, image)
    print(f"Created test image: {output_path}")
