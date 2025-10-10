#!/usr/bin/env python3
"""
ML Dataset Generator Stage

This stage extracts circle patches and creates a dataset for training
an ML model to classify marked vs unmarked circles.

Uses traditional image processing for initial labeling, which can be
manually reviewed and corrected later.
"""

import os
import cv2
import numpy as np
import pandas as pd
import json
from .base_stage import PipelineStage
from typing import Dict, Any, List, Tuple, Optional


class MLDatasetGeneratorStage(PipelineStage):
    """Stage: Generate ML training dataset from circle patches"""
    
    def get_stage_name(self) -> str:
        return "ml_dataset_generator"
    
    def get_stage_description(self) -> str:
        return "Generate ML training dataset from OMR circle patches"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting ML Dataset Generator Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        
        try:
            # Use the VISUALIZATION image (with blue circles) for patch extraction
            viz_image_path = context.get('visualization_image_path', image_path)
            print(f"[{class_name}] Using visualization image: {os.path.basename(viz_image_path)}")
            print(f"[{class_name}] This image contains rectangles and blue grid circles")
            
            # Read the visualization image
            image = cv2.imread(viz_image_path)
            
            if image is None:
                error_msg = "Could not read visualization image for dataset generation"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(success=False, error=error_msg)
            
            print(f"[{class_name}] Visualization image loaded - Shape: {image.shape}")
            
            # Store the original image path for dataset naming
            image_to_process = context.get('current_image_path', image_path)
            
            # Create dataset output directory
            base_name = os.path.splitext(image_to_process)[0]
            dataset_dir = f"{base_name}_ml_dataset"
            patches_dir = os.path.join(dataset_dir, "patches")
            
            os.makedirs(patches_dir, exist_ok=True)
            print(f"[{class_name}] Dataset directory: {dataset_dir}")
            
            # Process all 4 columns
            all_patch_data = []
            total_patches = 0
            
            for col_idx in range(1, 5):
                print(f"[{class_name}] ========================================")
                print(f"[{class_name}] Processing Column {col_idx}")
                
                # Get grid data
                grid_key = f"col{col_idx}_grid"
                grid_data = context.get(grid_key)
                
                if not grid_data:
                    print(f"[{class_name}] ⚠️ WARNING: No grid data for column {col_idx}")
                    continue
                
                r_mean_key = f"r_mean_col_{col_idx}"
                r_mean = context.get(r_mean_key, 16)
                
                # Get the EXACT grid circles that were used to draw blue circles
                grid_circles = grid_data.get('grid_circles', [])
                x_means = grid_data.get('x_means', [])
                y_means = grid_data.get('y_means', [])
                
                print(f"[{class_name}] Grid circles: {len(grid_circles)}")
                print(f"[{class_name}] X groups: {len(x_means)}, Y groups: {len(y_means)}")
                print(f"[{class_name}] Using EXACT blue circle coordinates from grid_circles list")
                
                # Use the EXACT coordinates from grid_circles (same as blue circles)
                # Grid circles are ordered: row-by-row, then column-by-column
                # So for each row (question), we have 4 columns (a, b, c, d)
                num_options = len(x_means)  # Should be 4 (a, b, c, d)
                num_questions = len(y_means)  # Should be 25
                
                if len(grid_circles) != num_options * num_questions:
                    print(f"[{class_name}] ⚠️ WARNING: Grid circle count mismatch!")
                    print(f"[{class_name}]   Expected: {num_options * num_questions}, Got: {len(grid_circles)}")
                
                # Extract patches using EXACT blue circle coordinates
                circle_idx = 0
                for question_num in range(1, num_questions + 1):
                    for option_idx in range(num_options):
                        if circle_idx >= len(grid_circles):
                            print(f"[{class_name}] ⚠️ Ran out of grid circles at index {circle_idx}")
                            break
                        
                        # Get EXACT coordinates from the blue circle grid
                        x, y = grid_circles[circle_idx]
                        option_letter = chr(ord('a') + option_idx)
                        
                        # Extract patch using EXACT blue circle center
                        patch, metrics = self._extract_circle_patch(
                            image, x, y, r_mean
                        )
                        
                        if patch is None:
                            circle_idx += 1
                            continue
                        
                        # Traditional threshold-based classification
                        initial_label = self._classify_circle_traditional(
                            patch, metrics
                        )
                        
                        # Save patch
                        patch_name = f"col{col_idx}_q{question_num:02d}_opt_{option_letter}.png"
                        patch_path = os.path.join(patches_dir, patch_name)
                        cv2.imwrite(patch_path, patch)
                        
                        # Store metadata
                        patch_info = {
                            'image_name': patch_name,
                            'source_image': filename,
                            'column': col_idx,
                            'question': question_num,
                            'option': option_letter,
                            'x': x,
                            'y': y,
                            'r_mean': r_mean,
                            'mean_intensity': metrics['mean_intensity'],
                            'std_intensity': metrics['std_intensity'],
                            'fill_ratio': metrics['fill_ratio'],
                            'edge_score': metrics['edge_score'],
                            'initial_label': initial_label,
                            'reviewed_label': '',  # To be filled by manual review
                            'confidence': metrics['confidence']
                        }
                        
                        all_patch_data.append(patch_info)
                        total_patches += 1
                        circle_idx += 1
                
                print(f"[{class_name}] Column {col_idx}: Extracted {circle_idx} patches using exact blue circle coordinates")
            
            # Save metadata as CSV
            metadata_path = os.path.join(dataset_dir, "metadata.csv")
            df = pd.DataFrame(all_patch_data)
            df.to_csv(metadata_path, index=False)
            print(f"[{class_name}] Metadata saved to: {metadata_path}")
            
            # Save summary as JSON
            summary = {
                'source_image': filename,
                'total_patches': total_patches,
                'patches_per_column': total_patches // 4,
                'initial_marked': len(df[df['initial_label'] == 'marked']),
                'initial_unmarked': len(df[df['initial_label'] == 'unmarked']),
                'dataset_directory': dataset_dir,
                'patches_directory': patches_dir,
                'metadata_file': metadata_path
            }
            
            summary_path = os.path.join(dataset_dir, "summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Dataset generation summary:")
            print(f"[{class_name}]   Total patches: {total_patches}")
            print(f"[{class_name}]   Initial 'marked': {summary['initial_marked']}")
            print(f"[{class_name}]   Initial 'unmarked': {summary['initial_unmarked']}")
            print(f"[{class_name}]   Dataset directory: {dataset_dir}")
            
            result = self.create_stage_result(
                success=True,
                dataset_directory=dataset_dir,
                patches_directory=patches_dir,
                metadata_file=metadata_path,
                total_patches=total_patches,
                initial_marked=summary['initial_marked'],
                initial_unmarked=summary['initial_unmarked']
            )
            
            print(f"[{class_name}] ✅ SUCCESS: ML dataset generation complete")
            return result
            
        except Exception as e:
            error_msg = f"ML dataset generation failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            import traceback
            print(f"[{class_name}] Traceback: {traceback.format_exc()}")
            return self.create_stage_result(success=False, error=error_msg)
        finally:
            print(f"[{class_name}] ====== ML Dataset Generator Stage Complete ======\n")
    
    def _extract_circle_patch(self, image, x: int, y: int, r_mean: float) -> Tuple[Optional[np.ndarray], Dict]:
        """
        Extract a square patch around the PERFECT normalized grid circle.
        
        Uses the exact grid circle center (x_mean, y_mean) and r_mean to create
        a tight, consistent bounding box around each circle.
        
        Args:
            image: Source image
            x, y: Perfect grid circle center coordinates
            r_mean: Mean radius for this column
            
        Returns:
            Tuple of (patch_image, metrics_dict)
        """
        class_name = self.__class__.__name__
        
        # Patch size: 2 × radius (i.e., diameter)
        # This creates a tight crop: center ± radius
        patch_size = int(2 * r_mean)
        
        # Make patch size even for perfect centering
        if patch_size % 2 != 0:
            patch_size += 1
        
        half_size = patch_size // 2
        
        # Calculate bounding box centered EXACTLY on (x, y)
        x1 = x - half_size
        y1 = y - half_size
        x2 = x + half_size
        y2 = y + half_size
        
        # Handle edge cases - pad if necessary to maintain consistent size
        pad_left = max(0, -x1)
        pad_top = max(0, -y1)
        pad_right = max(0, x2 - image.shape[1])
        pad_bottom = max(0, y2 - image.shape[0])
        
        # Adjust bounds to valid image region
        x1_safe = max(0, x1)
        y1_safe = max(0, y1)
        x2_safe = min(image.shape[1], x2)
        y2_safe = min(image.shape[0], y2)
        
        # Extract the patch from the image
        patch = image[y1_safe:y2_safe, x1_safe:x2_safe].copy()
        
        # Pad if patch is near image edges to maintain consistent size
        if pad_left > 0 or pad_top > 0 or pad_right > 0 or pad_bottom > 0:
            patch = cv2.copyMakeBorder(
                patch,
                pad_top, pad_bottom, pad_left, pad_right,
                cv2.BORDER_CONSTANT,
                value=(255, 255, 255)  # White padding
            )
        
        # Verify patch size
        if patch.shape[0] != patch_size or patch.shape[1] != patch_size:
            # Force resize if size mismatch (shouldn't happen, but safety check)
            patch = cv2.resize(patch, (patch_size, patch_size))
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        
        # Create circular mask for the EXACT circle region
        # The circle is now perfectly centered in the patch
        center = (patch_size // 2, patch_size // 2)
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # Use 0.9 * r_mean since patch is tighter now (diameter-sized)
        inner_radius = int(r_mean * 0.9)
        cv2.circle(mask, center, inner_radius, 255, -1)
        
        # Calculate metrics from the perfect circular region
        inner_pixels = gray[mask == 255]
        
        if len(inner_pixels) == 0:
            print(f"[{class_name}] ⚠️ Warning: No pixels in circle mask at ({x}, {y})")
            return None, {}
        
        mean_intensity = np.mean(inner_pixels)
        std_intensity = np.std(inner_pixels)
        
        # Calculate fill ratio (percentage of dark pixels)
        # Adaptive threshold based on image characteristics
        threshold = 180  # Pixels darker than this are "filled"
        dark_pixels = np.sum(inner_pixels < threshold)
        fill_ratio = dark_pixels / len(inner_pixels)
        
        # Edge detection score within the circle
        edges = cv2.Canny(gray, 50, 150)
        edge_score = np.sum(edges[mask == 255]) / len(inner_pixels)
        
        metrics = {
            'mean_intensity': float(mean_intensity),
            'std_intensity': float(std_intensity),
            'fill_ratio': float(fill_ratio),
            'edge_score': float(edge_score),
            'patch_size': patch_size,
            'inner_radius': inner_radius,
            'confidence': 0.0  # Will be calculated during classification
        }
        
        return patch, metrics
    
    def _classify_circle_traditional(self, patch: np.ndarray, metrics: Dict) -> str:
        """
        Classify circle as marked or unmarked using traditional methods.
        
        Args:
            patch: Circle patch image
            metrics: Pre-calculated metrics
            
        Returns:
            'marked' or 'unmarked'
        """
        fill_ratio = metrics['fill_ratio']
        mean_intensity = metrics['mean_intensity']
        std_intensity = metrics['std_intensity']
        
        # Decision logic based on multiple features
        # Threshold tuned for pencil/pen marks on white paper
        
        # Primary: Fill ratio (dark pixels)
        if fill_ratio > 0.35:  # More than 35% dark pixels
            label = 'marked'
            confidence = min(0.95, 0.5 + fill_ratio)
        elif fill_ratio < 0.15:  # Less than 15% dark pixels
            label = 'unmarked'
            confidence = min(0.95, 0.5 + (1 - fill_ratio))
        else:
            # Ambiguous region - use additional features
            if mean_intensity < 180 and std_intensity > 20:
                label = 'marked'
                confidence = 0.6
            else:
                label = 'unmarked'
                confidence = 0.6
        
        metrics['confidence'] = confidence
        
        return label

