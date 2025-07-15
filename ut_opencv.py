#!/usr/bin/env python3
"""
Simple test for OpenCV ArUco functionality
"""

import cv2
import numpy as np
import os
import sys
import platform

def test_opencv_aruco():
    print("Testing OpenCV ArUco functionality...")
    print(f"OpenCV version: {cv2.__version__}")
    
    # Test initialization
    try:
        # Try new API first
        print("Testing new ArUco API...")
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        aruco_params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        
        # Test marker generation
        marker_img = cv2.aruco.generateImageMarker(aruco_dict, 0, 100)
        print("✓ New ArUco API working correctly")
        use_new_api = True
        
    except AttributeError as e:
        print(f"New API not available: {e}")
        try:
            # Try old API
            print("Testing old ArUco API...")
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            aruco_params = cv2.aruco.DetectorParameters_create()
            
            # Test marker generation
            marker_img = cv2.aruco.drawMarker(aruco_dict, 0, 100)
            print("✓ Old ArUco API working correctly")
            use_new_api = False
            
        except Exception as e2:
            print(f"✗ Both APIs failed: {e2}")
            return False
    
    # Test detection on generated marker
    print("Testing marker detection...")
    try:
        # Create a test image with the marker
        test_image = np.ones((300, 300), dtype=np.uint8) * 255
        marker_size = marker_img.shape[0]
        start_x = (300 - marker_size) // 2
        start_y = (300 - marker_size) // 2
        test_image[start_y:start_y+marker_size, start_x:start_x+marker_size] = marker_img
        
        # Detect markers
        if use_new_api:
            corners, ids, rejected = detector.detectMarkers(test_image)
        else:
            corners, ids, rejected = cv2.aruco.detectMarkers(test_image, aruco_dict, parameters=aruco_params)
        
        if ids is not None and len(ids) > 0:
            print(f"✓ Successfully detected marker ID: {ids[0][0]}")
            return True
        else:
            print("✗ Failed to detect generated marker")
            return False
            
    except Exception as e:
        print(f"✗ Detection test failed: {e}")
        return False

def debug_environment():
    print("\nEnvironment Debugging Information:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"NumPy Version: {np.__version__}")
    print(f"Executable Path: {sys.executable}")
    print(f"Environment Path: {os.environ.get('PATH')}")
