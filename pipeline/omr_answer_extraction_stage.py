#!/usr/bin/env python3
"""
OMR Answer Extraction Stage Implementation

This stage detects OMR bubbles (circles) in each column and prepares them for analysis.
"""

import os
import cv2
import numpy as np
from .base_stage import PipelineStage
from typing import Dict, Any, List, Tuple, Optional


class OMRAnswerExtractionStage(PipelineStage):
    """Stage: Extract OMR answer bubbles using circle detection"""
    
    def get_stage_name(self) -> str:
        return "omr_answer_extraction"
    
    def get_stage_description(self) -> str:
        return "Extract OMR answer bubbles using circle detection"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting OMR Answer Extraction Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Get the image to process
            image_to_process = context.get('current_image_path', image_path)
            print(f"[{class_name}] Image to process: {os.path.basename(image_to_process)}")
            
            # Read the image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_to_process)
            
            if image is None:
                error_msg = "Could not read image for OMR answer extraction"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg
                )
            
            print(f"[{class_name}] Image loaded - Shape: {image.shape}")
            
            # Get existing visualization image from context (with rectangles)
            viz_rect_image_path = context.get('visualization_image_path')
            
            if viz_rect_image_path and os.path.exists(viz_rect_image_path):
                print(f"[{class_name}] Loading existing visualization image: {os.path.basename(viz_rect_image_path)}")
                print(f"[{class_name}] This image contains rectangles from previous stages")
                viz_image = cv2.imread(viz_rect_image_path)
            else:
                print(f"[{class_name}] No visualization image found, creating new one")
                viz_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
                viz_image = cv2.cvtColor(viz_image, cv2.COLOR_GRAY2BGR)
            
            # Create two separate copies:
            # 1. viz_grid_image - for blue grid circles (with rectangles)
            # 2. viz_circle_image - for green/red detected circles (with rectangles)
            viz_grid_image = viz_image.copy()
            viz_circle_image = viz_image.copy()
            print(f"[{class_name}] Created copies for grid and circle visualizations")
            
            # Create visualization subfolder
            image_dir = os.path.dirname(image_to_process)
            viz_folder = os.path.join(image_dir, "visualization")
            os.makedirs(viz_folder, exist_ok=True)
            
            # Create paths for visualization images in subfolder
            base_name = os.path.basename(os.path.splitext(image_to_process)[0])
            viz_grid_image_path = os.path.join(viz_folder, f"{base_name}_visualization.png")
            viz_circle_image_path = os.path.join(viz_folder, f"{base_name}_visualization_circles.png")
            print(f"[{class_name}] Grid visualization image path: {viz_grid_image_path}")
            print(f"[{class_name}] Circle visualization image path: {viz_circle_image_path}")
            
            # Process all 4 columns
            print(f"[{class_name}] Processing 4 OMR columns for circle detection...")
            
            column_keys = ['col1_rect', 'col2_rect', 'col3_rect', 'col4_rect']
            mean_radii = {}
            all_circles_data = {}
            all_grid_data = {}
            
            for col_idx, col_key in enumerate(column_keys, 1):
                print(f"[{class_name}] ========================================")
                print(f"[{class_name}] Processing Column {col_idx}")
                
                col_rect = context.get(col_key)
                
                if not col_rect:
                    print(f"[{class_name}] ⚠️ WARNING: {col_key} not found in context, skipping")
                    continue
                
                print(f"[{class_name}] Rectangle from context: {col_rect}")
                
                # Detect circles in this column
                circles_dict, r_mean = self._detect_circles_in_column(
                    image, col_rect, col_idx
                )
                
                if circles_dict is not None:
                    normal_circles = circles_dict.get('normal', [])
                    outlier_circles = circles_dict.get('outliers', [])
                    total_circles = len(normal_circles) + len(outlier_circles)
                    
                    print(f"[{class_name}] ✅ Column {col_idx}: Detected {total_circles} circles total")
                    print(f"[{class_name}] ✅ Column {col_idx}:   - {len(normal_circles)} normal circles")
                    print(f"[{class_name}] ✅ Column {col_idx}:   - {len(outlier_circles)} outlier circles")
                    print(f"[{class_name}] ✅ Column {col_idx}: Mean radius = {r_mean:.2f} pixels")
                    
                    # Store mean radius in context
                    mean_radii[f"r_mean_col_{col_idx}"] = r_mean
                    all_circles_data[f"col{col_idx}_circles"] = circles_dict
                    
                    # Mark circles on circle visualization image
                    self._mark_circles_on_image(viz_circle_image, circles_dict, r_mean, col_rect)
                    print(f"[{class_name}] Circles marked on circle visualization image")
                    
                    # Create grid from detected circles
                    print(f"[{class_name}] Creating regularized grid for column {col_idx}...")
                    grid_data = self._group_circles_into_grid(circles_dict, r_mean, col_idx)
                    
                    if grid_data is not None:
                        all_grid_data[f"col{col_idx}_grid"] = grid_data
                        print(f"[{class_name}] ✅ Grid created: {grid_data['x_groups_count']} x {grid_data['y_groups_count']} = {len(grid_data['grid_circles'])} circles")
                        
                        # Mark grid circles in blue on grid visualization (not on circle viz)
                        self._mark_grid_circles_on_image(viz_grid_image, grid_data, r_mean)
                        print(f"[{class_name}] Grid circles marked in blue on grid visualization image")
                    else:
                        print(f"[{class_name}] ⚠️ Failed to create grid for column {col_idx}")
                else:
                    print(f"[{class_name}] ⚠️ Column {col_idx}: No circles detected")
            
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Circle detection summary:")
            for col_idx in range(1, 5):
                key = f"r_mean_col_{col_idx}"
                if key in mean_radii:
                    circles_dict = all_circles_data.get(f'col{col_idx}_circles', {})
                    if isinstance(circles_dict, dict):
                        normal_count = len(circles_dict.get('normal', []))
                        outlier_count = len(circles_dict.get('outliers', []))
                        total_count = normal_count + outlier_count
                        print(f"[{class_name}]   Column {col_idx}: {total_count} circles ({normal_count} normal, {outlier_count} outliers), r_mean = {mean_radii[key]:.2f}")
                    else:
                        print(f"[{class_name}]   Column {col_idx}: circles data format error")
                else:
                    print(f"[{class_name}]   Column {col_idx}: No circles detected")
            
            # Save both visualization images
            print(f"[{class_name}] Saving grid visualization image to: {viz_grid_image_path}")
            cv2.imwrite(viz_grid_image_path, viz_grid_image)
            print(f"[{class_name}] Grid visualization image saved")
            
            print(f"[{class_name}] Saving circle visualization image to: {viz_circle_image_path}")
            cv2.imwrite(viz_circle_image_path, viz_circle_image)
            print(f"[{class_name}] Circle visualization image saved")
            
            # Explain what each visualization contains
            print(f"[{class_name}] Grid visualization (rectangles + blue grid): {os.path.basename(viz_grid_image_path)}")
            print(f"[{class_name}] Circle visualization (rectangles + green/red circles): {os.path.basename(viz_circle_image_path)}")
            
            # Calculate total circles detected
            total_circles_detected = 0
            for i in range(1, 5):
                circles_dict = all_circles_data.get(f'col{i}_circles', {})
                if isinstance(circles_dict, dict):
                    total_circles_detected += len(circles_dict.get('normal', []))
                    total_circles_detected += len(circles_dict.get('outliers', []))
            
            # Calculate total grid circles
            total_grid_circles = 0
            for i in range(1, 5):
                grid_data = all_grid_data.get(f'col{i}_grid', {})
                if isinstance(grid_data, dict):
                    total_grid_circles += len(grid_data.get('grid_circles', []))
            
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Grid creation summary:")
            for col_idx in range(1, 5):
                grid_key = f"col{col_idx}_grid"
                if grid_key in all_grid_data:
                    grid_data = all_grid_data[grid_key]
                    x_count = grid_data.get('x_groups_count', 0)
                    y_count = grid_data.get('y_groups_count', 0)
                    total = len(grid_data.get('grid_circles', []))
                    print(f"[{class_name}]   Column {col_idx}: {x_count} x {y_count} = {total} grid circles")
                else:
                    print(f"[{class_name}]   Column {col_idx}: No grid created")
            print(f"[{class_name}] Total grid circles: {total_grid_circles}")
            
            # Create result
            result = self.create_stage_result(
                success=True,
                circles_detected=total_circles_detected,
                grid_circles_count=total_grid_circles,
                visualization_circle_image_path=viz_circle_image_path
            )
            
            # Add mean radii, circle data, and grid data to result for context update
            result.update(mean_radii)
            result.update(all_circles_data)
            result.update(all_grid_data)
            
            print(f"[{class_name}] Context will be updated with mean radii:")
            for key, value in mean_radii.items():
                print(f"[{class_name}]   {key}: {value:.2f}")
            
            print(f"[{class_name}] ✅ SUCCESS: OMR answer extraction complete")
            return result
            
        except Exception as e:
            error_msg = f"OMR answer extraction failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            import traceback
            print(f"[{class_name}] Traceback: {traceback.format_exc()}")
            return self.create_stage_result(
                success=False,
                error=error_msg
            )
        finally:
            print(f"[{class_name}] ====== OMR Answer Extraction Stage Complete ======\n")
    
    def _detect_circles_in_column(self, image, col_rect: Tuple[int, int, int, int], 
                                  col_number: int) -> Tuple[Optional[Dict], float]:
        """
        Detect circles in a column rectangle using Hough Circle Transform.
        
        Args:
            image: OpenCV image
            col_rect: Column rectangle (x_min, y_min, x_max, y_max)
            col_number: Column number (1-4)
            
        Returns:
            Tuple of (circles_dict, mean_radius)
            circles_dict: Dict with 'normal' and 'outliers' lists of (x, y, radius) tuples or None
            mean_radius: Mean radius of filtered circles or 0.0
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _detect_circles_in_column() called for column {col_number}")
        
        x_min, y_min, x_max, y_max = col_rect
        
        # Crop column region
        print(f"[{class_name}] Cropping column region: ({x_min}, {y_min}) to ({x_max}, {y_max})")
        column_region = image[y_min:y_max, x_min:x_max]
        
        if column_region.size == 0:
            print(f"[{class_name}] ❌ ERROR: Cropped region is empty")
            return None, 0.0
        
        print(f"[{class_name}] Column region shape: {column_region.shape}")
        
        # Convert to grayscale
        print(f"[{class_name}] Converting to grayscale")
        gray = cv2.cvtColor(column_region, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        print(f"[{class_name}] Applying Gaussian blur")
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using Hough Circle Transform
        print(f"[{class_name}] Applying Hough Circle Transform...")
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,  # Minimum distance between circle centers
            param1=50,   # Upper threshold for Canny edge detector
            param2=30,   # Threshold for circle detection
            minRadius=5,  # Minimum circle radius
            maxRadius=50  # Maximum circle radius
        )
        
        if circles is None:
            print(f"[{class_name}] No circles detected in column {col_number}")
            return None, 0.0
        
        # Convert to proper format
        circles = np.round(circles[0, :]).astype("int")
        print(f"[{class_name}] Initial circles detected: {len(circles)}")
        
        # Extract radii
        radii = circles[:, 2]
        print(f"[{class_name}] Radius range: {radii.min():.1f} to {radii.max():.1f} pixels")
        
        # Simple outlier detection: exclude top 5 and bottom 5 circles by radius
        print(f"[{class_name}] Excluding top 5 and bottom 5 circles by radius...")
        
        # Sort circles by radius to identify outliers
        sorted_indices = np.argsort(radii)
        
        num_circles = len(circles)
        num_bottom_outliers = min(5, num_circles // 2)  # Don't exceed half the circles
        num_top_outliers = min(5, num_circles // 2)
        
        # Get indices for bottom 5, top 5, and middle circles
        bottom_outlier_indices = sorted_indices[:num_bottom_outliers]
        top_outlier_indices = sorted_indices[-num_top_outliers:]
        normal_indices = sorted_indices[num_bottom_outliers:-num_top_outliers] if num_circles > (num_bottom_outliers + num_top_outliers) else []
        
        # Separate circles
        filtered_circles = circles[normal_indices] if len(normal_indices) > 0 else np.array([])
        outlier_circles = np.concatenate([circles[bottom_outlier_indices], circles[top_outlier_indices]])
        
        print(f"[{class_name}] Bottom 5 outliers: radii {radii[bottom_outlier_indices].min():.1f} to {radii[bottom_outlier_indices].max():.1f}")
        if len(top_outlier_indices) > 0:
            print(f"[{class_name}] Top 5 outliers: radii {radii[top_outlier_indices].min():.1f} to {radii[top_outlier_indices].max():.1f}")
        print(f"[{class_name}] Normal circles: {len(filtered_circles)}")
        print(f"[{class_name}] Outlier circles: {len(outlier_circles)} (5 bottom + 5 top)")
        
        if len(filtered_circles) == 0:
            print(f"[{class_name}] ⚠️ WARNING: No circles remaining after filtering")
            return None, 0.0
        
        # Calculate mean radius from normal circles
        r_mean = np.mean(filtered_circles[:, 2])
        print(f"[{class_name}] Mean radius (r_mean_col_{col_number}): {r_mean:.2f} pixels")
        
        # Convert circles to absolute coordinates (add column offset)
        absolute_normal_circles = []
        for (x, y, r) in filtered_circles:
            abs_x = x + x_min
            abs_y = y + y_min
            absolute_normal_circles.append((abs_x, abs_y, r))
        
        absolute_outlier_circles = []
        for (x, y, r) in outlier_circles:
            abs_x = x + x_min
            abs_y = y + y_min
            absolute_outlier_circles.append((abs_x, abs_y, r))
        
        print(f"[{class_name}] Converted to absolute coordinates")
        print(f"[{class_name}] Sample normal circle: {absolute_normal_circles[0] if absolute_normal_circles else 'None'}")
        print(f"[{class_name}] Sample outlier circle: {absolute_outlier_circles[0] if absolute_outlier_circles else 'None'}")
        
        circles_dict = {
            'normal': absolute_normal_circles,
            'outliers': absolute_outlier_circles
        }
        
        return circles_dict, float(r_mean)
    
    def _mark_circles_on_image(self, viz_image, circles_dict: Dict, r_mean: float, col_rect: Tuple):
        """
        Mark detected circles on the visualization image.
        Normal circles (middle 90%) in green with r_mean radius.
        Outlier circles (top/bottom 5%) in red with their original radius.
        
        Args:
            viz_image: Visualization image to mark on
            circles_dict: Dict with 'normal' and 'outliers' lists of (x, y, radius) tuples
            r_mean: Mean radius to use for normal circles
            col_rect: Column rectangle (for reference)
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _mark_circles_on_image() called")
        
        normal_circles = circles_dict.get('normal', [])
        outlier_circles = circles_dict.get('outliers', [])
        
        print(f"[{class_name}] Number of normal circles to mark: {len(normal_circles)}")
        print(f"[{class_name}] Number of outlier circles to mark: {len(outlier_circles)}")
        print(f"[{class_name}] Using r_mean: {r_mean:.2f} for normal circles")
        
        # Mark normal circles with green color (1 pixel line) using r_mean
        r_mean_int = int(round(r_mean))
        for i, (x, y, r) in enumerate(normal_circles):
            # Draw circle with 1 pixel line width in green using r_mean
            cv2.circle(viz_image, (x, y), r_mean_int, (0, 255, 0), 1)  # Green circle, 1 pixel
            
            if i == 0:
                print(f"[{class_name}] First normal circle marked at: ({x}, {y}) with r_mean {r_mean_int}")
            if i == len(normal_circles) - 1:
                print(f"[{class_name}] Last normal circle marked at: ({x}, {y}) with r_mean {r_mean_int}")
        
        # Mark outlier circles with red color (1 pixel line) using their original radius
        for i, (x, y, r) in enumerate(outlier_circles):
            # Draw circle with 1 pixel line width in red using original radius
            cv2.circle(viz_image, (x, y), r, (0, 0, 255), 1)  # Red circle, 1 pixel
            
            if i == 0:
                print(f"[{class_name}] First outlier circle marked at: ({x}, {y}) with original radius {r}")
            if i == len(outlier_circles) - 1:
                print(f"[{class_name}] Last outlier circle marked at: ({x}, {y}) with original radius {r}")
        
        print(f"[{class_name}] Marked {len(normal_circles)} normal circles in green (r_mean={r_mean_int})")
        print(f"[{class_name}] Marked {len(outlier_circles)} outlier circles in red (original radius)")
    
    def _group_circles_into_grid(self, circles_dict: Dict, r_mean: float, col_number: int) -> Optional[Dict]:
        """
        Group circles into a 4x25 grid based on X and Y positions.
        
        Uses only normal circles (excludes outliers) to build the grid structure.
        Uses hierarchical clustering based on 2*r_mean threshold:
        - Circles with X positions < 2*r_mean apart belong to same X group (expect 4 groups)
        - Circles with Y positions < 2*r_mean apart belong to same Y group (expect 25 groups)
        
        Args:
            circles_dict: Dict with 'normal' and 'outliers' lists of (x, y, radius) tuples
            r_mean: Mean radius for grouping threshold
            col_number: Column number (1-4)
            
        Returns:
            Dict with grid information or None if grouping fails
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _group_circles_into_grid() called for column {col_number}")
        
        # Use only normal circles for grid grouping (exclude outliers to avoid interference)
        normal_circles = circles_dict.get('normal', [])
        outlier_circles = circles_dict.get('outliers', [])
        all_circles = normal_circles  # Only use normal circles for grid structure
        
        if len(all_circles) == 0:
            print(f"[{class_name}] No normal circles to group")
            return None
        
        print(f"[{class_name}] Grouping {len(all_circles)} normal circles (excluding {len(outlier_circles)} outliers, threshold: 2*r_mean = {2*r_mean:.2f})")
        
        # Extract X and Y positions from normal circles only
        x_positions = np.array([x for x, y, r in all_circles])
        y_positions = np.array([y for x, y, r in all_circles])
        
        print(f"[{class_name}] X range: {x_positions.min():.1f} to {x_positions.max():.1f}")
        print(f"[{class_name}] Y range: {y_positions.min():.1f} to {y_positions.max():.1f}")
        
        # Group X positions (expect 4 groups for a, b, c, d)
        x_groups = self._group_positions(x_positions, 2 * r_mean)
        print(f"[{class_name}] Found {len(x_groups)} X groups (expected 4)")
        
        # Group Y positions (expect 25 groups for questions 1-25 or 26-50, etc.)
        y_groups = self._group_positions(y_positions, 2 * r_mean)
        print(f"[{class_name}] Found {len(y_groups)} Y groups (expected 25)")
        
        # Calculate mean positions for each group
        x_means = [np.mean(group) for group in x_groups]
        y_means = [np.mean(group) for group in y_groups]
        
        # Sort to ensure proper order
        x_means = sorted(x_means)
        y_means = sorted(y_means)
        
        print(f"[{class_name}] X means: {[f'{x:.1f}' for x in x_means]}")
        print(f"[{class_name}] Y means (first 5): {[f'{y:.1f}' for y in y_means[:5]]}")
        print(f"[{class_name}] Y means (last 5): {[f'{y:.1f}' for y in y_means[-5:]]}")
        
        # Create grid of circles at intersections of x_means and y_means
        grid_circles = []
        for y_mean in y_means:
            for x_mean in x_means:
                grid_circles.append((int(round(x_mean)), int(round(y_mean))))
        
        print(f"[{class_name}] Created grid with {len(grid_circles)} circles ({len(x_means)} x {len(y_means)})")
        
        return {
            'x_means': x_means,
            'y_means': y_means,
            'grid_circles': grid_circles,
            'x_groups_count': len(x_groups),
            'y_groups_count': len(y_groups)
        }
    
    def _group_positions(self, positions: np.ndarray, threshold: float) -> List[List[float]]:
        """
        Group positions using threshold-based clustering.
        
        Positions that are < threshold apart belong to the same group.
        
        Args:
            positions: Array of positions (X or Y coordinates)
            threshold: Distance threshold for grouping
            
        Returns:
            List of groups, where each group is a list of positions
        """
        if len(positions) == 0:
            return []
        
        # Sort positions for efficient grouping
        sorted_positions = np.sort(positions)
        
        groups = []
        current_group = [sorted_positions[0]]
        
        for i in range(1, len(sorted_positions)):
            # If current position is close to previous one, add to current group
            if sorted_positions[i] - sorted_positions[i-1] < threshold:
                current_group.append(sorted_positions[i])
            else:
                # Start a new group
                groups.append(current_group)
                current_group = [sorted_positions[i]]
        
        # Don't forget the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _mark_grid_circles_on_image(self, viz_image, grid_data: Dict, r_mean: float):
        """
        Mark the regularized grid circles in blue on the visualization image.
        
        Args:
            viz_image: Visualization image to mark on
            grid_data: Grid information from _group_circles_into_grid
            r_mean: Mean radius to use for grid circles
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _mark_grid_circles_on_image() called")
        
        grid_circles = grid_data.get('grid_circles', [])
        r_mean_int = int(round(r_mean))
        
        print(f"[{class_name}] Marking {len(grid_circles)} grid circles in blue with r_mean={r_mean_int}")
        
        # Mark grid circles in blue (1 pixel line) using r_mean
        for i, (x, y) in enumerate(grid_circles):
            cv2.circle(viz_image, (x, y), r_mean_int, (255, 0, 0), 1)  # Blue circle, 1 pixel
            
            if i == 0:
                print(f"[{class_name}] First grid circle marked at: ({x}, {y})")
            if i == len(grid_circles) - 1:
                print(f"[{class_name}] Last grid circle marked at: ({x}, {y})")
        
        print(f"[{class_name}] Marked {len(grid_circles)} grid circles in blue")

