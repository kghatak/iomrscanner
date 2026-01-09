#!/usr/bin/env python3
"""
OMR Column Rectangle Estimation Helper Functions

This module provides helper functions for estimating missing column rectangles
when not all ArUco markers are detected.
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple


def estimated_column_rectangle_one_missing_point(
    rectangle_id: str,
    detected_markers: List[int],
    detected_rectangles: Dict[str, Tuple[int, int, int, int]],
    detection_info: Dict,
    marker_ids: List[int]
) -> Optional[Tuple[int, int, int, int]]:
    """
    Estimate a column rectangle when exactly one marker is missing.
    
    Uses the two corners that are present to estimate the missing corner.
    
    Args:
        rectangle_id: Identifier for the rectangle (e.g., 'col1_rect')
        detected_markers: List of all detected marker IDs
        detected_rectangles: Dictionary of already detected rectangles with their coordinates
        detection_info: Detection information containing marker_midpoints and detected_ids
        marker_ids: List of 4 marker IDs defining the rectangle [a, b, c, d]
            where:
                a = top-left
                b = bottom-left
                c = top-right
                d = bottom-right
    
    Returns:
        Tuple of (x_min, y_min, x_max, y_max) or None if estimation failed
    """
    class_name = "ColumnEstimation"
    
    print(f"[{class_name}] ====== Attempting One Missing Point Estimation ======")
    print(f"[{class_name}] Required marker IDs: {marker_ids}")
    print(f"[{class_name}] Detected markers: {detected_markers}")
    
    # Check which markers are missing
    missing_markers = [m for m in marker_ids if m not in detected_markers]
    present_markers = [m for m in marker_ids if m in detected_markers]
    
    print(f"[{class_name}] Present markers: {present_markers}")
    print(f"[{class_name}] Missing markers: {missing_markers}")
    
    # This method handles exactly one missing marker
    if len(missing_markers) != 1:
        print(f"[{class_name}] ❌ One missing point logic requires exactly 1 missing marker, found {len(missing_markers)}")
        return None
    
    missing_marker_id = missing_markers[0]
    print(f"[{class_name}] Missing marker ID: {missing_marker_id}")
    
    # Get marker positions
    marker_midpoints = detection_info.get('marker_midpoints', [])
    detected_ids = detection_info.get('detected_ids', [])
    
    if len(marker_midpoints) != len(detected_ids):
        print(f"[{class_name}] ❌ ERROR: Mismatch between marker midpoints and detected IDs")
        return None
    
    # Create a mapping of marker_id -> (x, y) position
    marker_positions = {}
    for i, marker_id in enumerate(detected_ids):
        if marker_id in marker_ids:  # Only store positions for markers in this rectangle
            midpoint = marker_midpoints[i]
            marker_positions[marker_id] = (int(midpoint[0]), int(midpoint[1]))
            print(f"[{class_name}]   Marker {marker_id}: ({marker_positions[marker_id][0]}, {marker_positions[marker_id][1]})")
    
    # Check we have positions for all present markers
    if len(marker_positions) != len(present_markers):
        print(f"[{class_name}] ❌ ERROR: Missing positions for some present markers")
        return None
    
    # Unpack marker positions
    # a = top-left, b = bottom-left, c = top-right, d = bottom-right
    a_id, b_id, c_id, d_id = marker_ids
    a = marker_positions.get(a_id)
    b = marker_positions.get(b_id)
    c = marker_positions.get(c_id)
    d = marker_positions.get(d_id)
    
    print(f"[{class_name}] Marker positions:")
    print(f"[{class_name}]   a (top-left, ID={a_id}): {a}")
    print(f"[{class_name}]   b (bottom-left, ID={b_id}): {b}")
    print(f"[{class_name}]   c (top-right, ID={c_id}): {c}")
    print(f"[{class_name}]   d (bottom-right, ID={d_id}): {d}")
    
    # Estimate based on which marker is missing
    estimated_positions = {}
    
    if missing_marker_id == a_id:  # Top-left missing
        print(f"[{class_name}] Estimating top-left (a) from bottom-left (b) and top-right (c)")
        # a.x = b.x (same x as bottom-left)
        # a.y = c.y (same y as top-right)
        if b and c:
            estimated_a = (b[0], c[1])
            estimated_positions[a_id] = estimated_a
            print(f"[{class_name}]   Estimated a (top-left): {estimated_a}")
            print(f"[{class_name}]   Using b.x={b[0]} and c.y={c[1]}")
        else:
            print(f"[{class_name}] ❌ ERROR: Missing b or c for estimation")
            return None
            
    elif missing_marker_id == b_id:  # Bottom-left missing
        print(f"[{class_name}] Estimating bottom-left (b) from top-left (a) and bottom-right (d)")
        # b.x = a.x (same x as top-left)
        # b.y = d.y (same y as bottom-right)
        if a and d:
            estimated_b = (a[0], d[1])
            estimated_positions[b_id] = estimated_b
            print(f"[{class_name}]   Estimated b (bottom-left): {estimated_b}")
            print(f"[{class_name}]   Using a.x={a[0]} and d.y={d[1]}")
        else:
            print(f"[{class_name}] ❌ ERROR: Missing a or d for estimation")
            return None
            
    elif missing_marker_id == c_id:  # Top-right missing
        print(f"[{class_name}] Estimating top-right (c) from top-left (a) and bottom-right (d)")
        # c.x = d.x (same x as bottom-right)
        # c.y = a.y (same y as top-left)
        if a and d:
            estimated_c = (d[0], a[1])
            estimated_positions[c_id] = estimated_c
            print(f"[{class_name}]   Estimated c (top-right): {estimated_c}")
            print(f"[{class_name}]   Using d.x={d[0]} and a.y={a[1]}")
        else:
            print(f"[{class_name}] ❌ ERROR: Missing a or d for estimation")
            return None
            
    elif missing_marker_id == d_id:  # Bottom-right missing
        print(f"[{class_name}] Estimating bottom-right (d) from bottom-left (b) and top-right (c)")
        # d.x = c.x (same x as top-right)
        # d.y = b.y (same y as bottom-left)
        if b and c:
            estimated_d = (c[0], b[1])
            estimated_positions[d_id] = estimated_d
            print(f"[{class_name}]   Estimated d (bottom-right): {estimated_d}")
            print(f"[{class_name}]   Using c.x={c[0]} and b.y={b[1]}")
        else:
            print(f"[{class_name}] ❌ ERROR: Missing b or c for estimation")
            return None
    
    # Combine all positions (present + estimated)
    all_positions = {}
    all_positions.update(marker_positions)  # Present markers
    all_positions.update(estimated_positions)  # Estimated marker
    
    print(f"[{class_name}] All marker positions (including estimated):")
    final_a = all_positions.get(a_id)
    final_b = all_positions.get(b_id)
    final_c = all_positions.get(c_id)
    final_d = all_positions.get(d_id)
    
    if not all([final_a, final_b, final_c, final_d]):
        print(f"[{class_name}] ❌ ERROR: Could not get all 4 corner positions")
        return None
    
    print(f"[{class_name}]   a (top-left): {final_a}")
    print(f"[{class_name}]   b (bottom-left): {final_b}")
    print(f"[{class_name}]   c (top-right): {final_c}")
    print(f"[{class_name}]   d (bottom-right): {final_d}")
    
    # Calculate bounding rectangle from all 4 corners
    x_coords = [final_a[0], final_b[0], final_c[0], final_d[0]]
    y_coords = [final_a[1], final_b[1], final_c[1], final_d[1]]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    estimated_rect = (x_min, y_min, x_max, y_max)
    
    print(f"[{class_name}] ✅ Estimated rectangle: {estimated_rect}")
    print(f"[{class_name}]   Dimensions: {x_max - x_min} x {y_max - y_min} pixels")
    print(f"[{class_name}] ====== One Missing Point Estimation Complete ======")
    
    return estimated_rect


def estimated_column_rectangle_two_missing_points(
    rectangle_id: str,
    detected_markers: List[int],
    detected_rectangles: Dict[str, Tuple[int, int, int, int]],
    detection_info: Dict,
    marker_ids: List[int]
) -> Optional[Tuple[int, int, int, int]]:
    """
    Estimate a column rectangle when exactly two markers are missing.
    
    TODO: Implementation to be added later.
    
    Args:
        rectangle_id: Identifier for the rectangle (e.g., 'col1_rect')
        detected_markers: List of all detected marker IDs
        detected_rectangles: Dictionary of already detected rectangles with their coordinates
        detection_info: Detection information containing marker_midpoints and detected_ids
        marker_ids: List of 4 marker IDs defining the rectangle [a, b, c, d]
            where:
                a = top-left
                b = bottom-left
                c = top-right
                d = bottom-right
    
    Returns:
        Tuple of (x_min, y_min, x_max, y_max) or None if estimation failed
    """
    class_name = "ColumnEstimation"
    
    print(f"[{class_name}] ====== Attempting Two Missing Points Estimation ======")
    print(f"[{class_name}] Required marker IDs: {marker_ids}")
    print(f"[{class_name}] Detected markers: {detected_markers}")
    
    # Check which markers are missing
    missing_markers = [m for m in marker_ids if m not in detected_markers]
    present_markers = [m for m in marker_ids if m in detected_markers]
    
    print(f"[{class_name}] Present markers: {present_markers}")
    print(f"[{class_name}] Missing markers: {missing_markers}")
    
    # This method handles exactly two missing markers
    if len(missing_markers) != 2:
        print(f"[{class_name}] ❌ Two missing points logic requires exactly 2 missing markers, found {len(missing_markers)}")
        return None
    
    print(f"[{class_name}] Missing marker IDs: {missing_markers}")
    print(f"[{class_name}] TODO: Two missing points estimation logic to be implemented")
    
    return None


def estimated_column_rectangle_at_least_one_point(
    rectangle_id: str,
    detected_markers: List[int],
    detected_rectangles: Dict[str, Tuple[int, int, int, int]],
    detection_info: Dict,
    marker_ids: List[int]
) -> Optional[Tuple[int, int, int, int]]:
    """
    Estimate a column rectangle using at least one available point and average dimensions
    from detected rectangles.
    
    Algorithm:
    1. Check there should be at least one detected_rectangle
    2. From detected_rectangles find the average width and average height
    3. Find one available point of the missing rectangle
    4. Apply the average width and height to find other three points
    
    Args:
        rectangle_id: Identifier for the rectangle (e.g., 'col1_rect')
        detected_markers: List of all detected marker IDs
        detected_rectangles: Dictionary of already detected rectangles with their coordinates
            Format: {'col1_rect': (x_min, y_min, x_max, y_max), ...}
        detection_info: Detection information containing marker_midpoints and detected_ids
        marker_ids: List of 4 marker IDs defining the rectangle [a, b, c, d]
            where:
                a = top-left
                b = bottom-left
                c = top-right
                d = bottom-right
    
    Returns:
        Tuple of (x_min, y_min, x_max, y_max) or None if estimation failed
    """
    class_name = "ColumnEstimation"
    
    print(f"[{class_name}] ====== Attempting At Least One Point Estimation ======")
    print(f"[{class_name}] Required marker IDs: {marker_ids}")
    print(f"[{class_name}] Detected markers: {detected_markers}")
    
    # Step 1: Check there should be at least one detected_rectangle
    if not detected_rectangles or len(detected_rectangles) == 0:
        print(f"[{class_name}] ❌ No detected rectangles available for reference")
        print(f"[{class_name}] Cannot calculate average dimensions")
        return None
    
    print(f"[{class_name}] Step 1: Found {len(detected_rectangles)} detected rectangle(s)")
    for rect_id, rect in detected_rectangles.items():
        print(f"[{class_name}]   {rect_id}: {rect}")
    
    # Step 2: Calculate average width and height from detected_rectangles
    widths = []
    heights = []
    
    for rect_id, rect in detected_rectangles.items():
        x_min, y_min, x_max, y_max = rect
        width = x_max - x_min
        height = y_max - y_min
        widths.append(width)
        heights.append(height)
        print(f"[{class_name}]   {rect_id}: width={width}, height={height}")
    
    avg_width = int(sum(widths) / len(widths))
    avg_height = int(sum(heights) / len(heights))
    
    print(f"[{class_name}] Step 2: Average dimensions calculated")
    print(f"[{class_name}]   Average width: {avg_width} pixels")
    print(f"[{class_name}]   Average height: {avg_height} pixels")
    
    # Step 3: Find one available point of the missing rectangle
    present_markers = [m for m in marker_ids if m in detected_markers]
    missing_markers = [m for m in marker_ids if m not in detected_markers]
    
    print(f"[{class_name}] Step 3: Finding available points")
    print(f"[{class_name}]   Present markers: {present_markers}")
    print(f"[{class_name}]   Missing markers: {missing_markers}")
    
    if len(present_markers) == 0:
        print(f"[{class_name}] ❌ No markers available for this rectangle")
        return None
    
    # Get marker positions
    marker_midpoints = detection_info.get('marker_midpoints', [])
    detected_ids = detection_info.get('detected_ids', [])
    
    if len(marker_midpoints) != len(detected_ids):
        print(f"[{class_name}] ❌ ERROR: Mismatch between marker midpoints and detected IDs")
        return None
    
    # Create a mapping of marker_id -> (x, y) position
    marker_positions = {}
    for i, marker_id in enumerate(detected_ids):
        if marker_id in marker_ids:  # Only store positions for markers in this rectangle
            midpoint = marker_midpoints[i]
            marker_positions[marker_id] = (int(midpoint[0]), int(midpoint[1]))
            print(f"[{class_name}]   Marker {marker_id}: ({marker_positions[marker_id][0]}, {marker_positions[marker_id][1]})")
    
    if len(marker_positions) == 0:
        print(f"[{class_name}] ❌ ERROR: No marker positions found")
        return None
    
    # Unpack marker positions
    # a = top-left, b = bottom-left, c = top-right, d = bottom-right
    a_id, b_id, c_id, d_id = marker_ids
    a = marker_positions.get(a_id)
    b = marker_positions.get(b_id)
    c = marker_positions.get(c_id)
    d = marker_positions.get(d_id)
    
    print(f"[{class_name}] Available marker positions:")
    print(f"[{class_name}]   a (top-left, ID={a_id}): {a}")
    print(f"[{class_name}]   b (bottom-left, ID={b_id}): {b}")
    print(f"[{class_name}]   c (top-right, ID={c_id}): {c}")
    print(f"[{class_name}]   d (bottom-right, ID={d_id}): {d}")
    
    # Step 4: Use one available point + average dimensions to estimate other three points
    # Priority order: a (top-left) > c (top-right) > b (bottom-left) > d (bottom-right)
    estimated_positions = {}
    
    if a:  # Use top-left (a) as reference
        print(f"[{class_name}] Step 4: Using top-left (a) as reference point")
        print(f"[{class_name}]   Reference point a: {a}")
        estimated_positions[a_id] = a
        # Calculate other points
        estimated_positions[b_id] = (a[0], a[1] + avg_height)  # bottom-left: same x, y + height
        estimated_positions[c_id] = (a[0] + avg_width, a[1])  # top-right: x + width, same y
        estimated_positions[d_id] = (a[0] + avg_width, a[1] + avg_height)  # bottom-right: x + width, y + height
        print(f"[{class_name}]   Estimated b (bottom-left): {estimated_positions[b_id]}")
        print(f"[{class_name}]   Estimated c (top-right): {estimated_positions[c_id]}")
        print(f"[{class_name}]   Estimated d (bottom-right): {estimated_positions[d_id]}")
        
    elif c:  # Use top-right (c) as reference
        print(f"[{class_name}] Step 4: Using top-right (c) as reference point")
        print(f"[{class_name}]   Reference point c: {c}")
        estimated_positions[c_id] = c
        # Calculate other points
        estimated_positions[a_id] = (c[0] - avg_width, c[1])  # top-left: x - width, same y
        estimated_positions[b_id] = (c[0] - avg_width, c[1] + avg_height)  # bottom-left: x - width, y + height
        estimated_positions[d_id] = (c[0], c[1] + avg_height)  # bottom-right: same x, y + height
        print(f"[{class_name}]   Estimated a (top-left): {estimated_positions[a_id]}")
        print(f"[{class_name}]   Estimated b (bottom-left): {estimated_positions[b_id]}")
        print(f"[{class_name}]   Estimated d (bottom-right): {estimated_positions[d_id]}")
        
    elif b:  # Use bottom-left (b) as reference
        print(f"[{class_name}] Step 4: Using bottom-left (b) as reference point")
        print(f"[{class_name}]   Reference point b: {b}")
        estimated_positions[b_id] = b
        # Calculate other points
        estimated_positions[a_id] = (b[0], b[1] - avg_height)  # top-left: same x, y - height
        estimated_positions[c_id] = (b[0] + avg_width, b[1] - avg_height)  # top-right: x + width, y - height
        estimated_positions[d_id] = (b[0] + avg_width, b[1])  # bottom-right: x + width, same y
        print(f"[{class_name}]   Estimated a (top-left): {estimated_positions[a_id]}")
        print(f"[{class_name}]   Estimated c (top-right): {estimated_positions[c_id]}")
        print(f"[{class_name}]   Estimated d (bottom-right): {estimated_positions[d_id]}")
        
    elif d:  # Use bottom-right (d) as reference
        print(f"[{class_name}] Step 4: Using bottom-right (d) as reference point")
        print(f"[{class_name}]   Reference point d: {d}")
        estimated_positions[d_id] = d
        # Calculate other points
        estimated_positions[a_id] = (d[0] - avg_width, d[1] - avg_height)  # top-left: x - width, y - height
        estimated_positions[b_id] = (d[0] - avg_width, d[1])  # bottom-left: x - width, same y
        estimated_positions[c_id] = (d[0], d[1] - avg_height)  # top-right: same x, y - height
        print(f"[{class_name}]   Estimated a (top-left): {estimated_positions[a_id]}")
        print(f"[{class_name}]   Estimated b (bottom-left): {estimated_positions[b_id]}")
        print(f"[{class_name}]   Estimated c (top-right): {estimated_positions[c_id]}")
    else:
        print(f"[{class_name}] ❌ ERROR: No markers available for estimation")
        return None
    
    # Combine all positions (present + estimated)
    all_positions = {}
    all_positions.update(marker_positions)  # Present markers
    all_positions.update(estimated_positions)  # Estimated markers
    
    print(f"[{class_name}] All marker positions (including estimated):")
    final_a = all_positions.get(a_id)
    final_b = all_positions.get(b_id)
    final_c = all_positions.get(c_id)
    final_d = all_positions.get(d_id)
    
    if not all([final_a, final_b, final_c, final_d]):
        print(f"[{class_name}] ❌ ERROR: Could not get all 4 corner positions")
        return None
    
    print(f"[{class_name}]   a (top-left): {final_a}")
    print(f"[{class_name}]   b (bottom-left): {final_b}")
    print(f"[{class_name}]   c (top-right): {final_c}")
    print(f"[{class_name}]   d (bottom-right): {final_d}")
    
    # Calculate bounding rectangle from all 4 corners
    x_coords = [final_a[0], final_b[0], final_c[0], final_d[0]]
    y_coords = [final_a[1], final_b[1], final_c[1], final_d[1]]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    estimated_rect = (x_min, y_min, x_max, y_max)
    
    print(f"[{class_name}] ✅ Estimated rectangle: {estimated_rect}")
    print(f"[{class_name}]   Dimensions: {x_max - x_min} x {y_max - y_min} pixels")
    print(f"[{class_name}]   (Using average: {avg_width} x {avg_height})")
    print(f"[{class_name}] ====== At Least One Point Estimation Complete ======")
    
    return estimated_rect


def estimated_column_rectangle(
    rectangle_id: str,
    detected_markers: List[int],
    detected_rectangles: Dict[str, Tuple[int, int, int, int]],
    detection_info: Dict,
    marker_ids: List[int]
) -> Optional[Tuple[int, int, int, int]]:
    """
    Estimate a column rectangle when some markers are missing.
    
    Tries estimation methods in order:
    1. One missing point estimation
    2. Two missing points estimation (if step 1 fails)
    3. At least one point estimation (if steps 1 and 2 fail)
    
    Args:
        rectangle_id: Identifier for the rectangle (e.g., 'col1_rect')
        detected_markers: List of all detected marker IDs
        detected_rectangles: Dictionary of already detected rectangles with their coordinates
            Format: {'col1_rect': (x_min, y_min, x_max, y_max), ...}
        detection_info: Detection information containing marker_midpoints and detected_ids
        marker_ids: List of 4 marker IDs defining the rectangle [a, b, c, d]
            where:
                a = top-left
                b = bottom-left
                c = top-right
                d = bottom-right
    
    Returns:
        Tuple of (x_min, y_min, x_max, y_max) or None if estimation failed
    """
    class_name = "ColumnEstimation"
    
    print(f"[{class_name}] ====== Estimating {rectangle_id} ======")
    print(f"[{class_name}] Required marker IDs: {marker_ids}")
    print(f"[{class_name}] Detected markers: {detected_markers}")
    
    # Step 1: Try one missing point estimation
    print(f"[{class_name}] Step 1: Trying one missing point estimation...")
    result = estimated_column_rectangle_one_missing_point(
        rectangle_id, detected_markers, detected_rectangles, detection_info, marker_ids
    )
    
    if result:
        print(f"[{class_name}] ✅ Step 1 succeeded: One missing point estimation worked")
        return result
    
    print(f"[{class_name}] ❌ Step 1 failed: One missing point estimation did not work")
    
    # Step 2: Try two missing points estimation
    print(f"[{class_name}] Step 2: Trying two missing points estimation...")
    result = estimated_column_rectangle_two_missing_points(
        rectangle_id, detected_markers, detected_rectangles, detection_info, marker_ids
    )
    
    if result:
        print(f"[{class_name}] ✅ Step 2 succeeded: Two missing points estimation worked")
        return result
    
    print(f"[{class_name}] ❌ Step 2 failed: Two missing points estimation did not work")
    
    # Step 3: Try at least one point estimation
    print(f"[{class_name}] Step 3: Trying at least one point estimation...")
    result = estimated_column_rectangle_at_least_one_point(
        rectangle_id, detected_markers, detected_rectangles, detection_info, marker_ids
    )
    
    if result:
        print(f"[{class_name}] ✅ Step 3 succeeded: At least one point estimation worked")
        return result
    
    print(f"[{class_name}] ❌ Step 3 failed: At least one point estimation did not work")
    print(f"[{class_name}] ❌ All estimation methods failed for {rectangle_id}")
    print(f"[{class_name}] ====== Estimation Failed ======")
    
    return None

