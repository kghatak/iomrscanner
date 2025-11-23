#!/usr/bin/env python3
"""
Fetch Student Stage Implementation

This stage fetches student data from the backend API after roll number extraction.
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from .base_stage import PipelineStage


class FetchStudentStage(PipelineStage):
    """Stage 4: Fetch student data from backend API using roll number"""
    
    def __init__(self, processor_instance):
        super().__init__(processor_instance)
        # Backend API configuration
        self.base_url = "https://bigmandev03.azurewebsites.net"
        # self.base_url = "http://localhost:5010"
        self.endpoint = "/result/roll"
        self.headers = {
            "Content-Type": "application/json",
            "user-tenantid": "c2023-jgm"
        }
    
    def get_stage_name(self) -> str:
        return "fetch_student"
    
    def get_stage_description(self) -> str:
        return "Fetch student data from backend API"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting Fetch Student Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        
        try:
            # Check if roll number is available from previous stage
            roll_number = context.get('roll_number')
            
            if not roll_number:
                print(f"[{class_name}] ❌ ERROR: No roll number found in context")
                print(f"[{class_name}] Context keys: {list(context.keys())}")
                return self.create_stage_result(
                    success=False,
                    error="No roll number available for API call",
                    student_data=None,
                    api_response=None
                )
            
            print(f"[{class_name}] Roll number found: {roll_number}")
            
            # URL encode the roll number for the API call
            import urllib.parse
            encoded_roll_number = urllib.parse.quote(roll_number, safe='')
            api_url = f"{self.base_url}{self.endpoint}/{encoded_roll_number}"
            
            print(f"[{class_name}] API URL: {api_url}")
            print(f"[{class_name}] Headers: {self.headers}")
            
            # Make the API call
            print(f"[{class_name}] Making API request...")
            try:
                response = requests.get(
                    api_url,
                    headers=self.headers,
                    timeout=30  # 30 second timeout
                )
                
                print(f"[{class_name}] API Response Status: {response.status_code}")
                print(f"[{class_name}] API Response Headers: {dict(response.headers)}")
                
                # Check if request was successful
                if response.status_code == 200:
                    print(f"[{class_name}] ✅ API call successful!")
                    
                    try:
                        # Parse JSON response
                        student_data = response.json()
                        print(f"[{class_name}] Student data parsed successfully")
                        print(f"[{class_name}] Student data keys: {list(student_data.keys()) if isinstance(student_data, dict) else 'Not a dictionary'}")
                        
                        # Write JSON response to success file
                        self._write_json_to_file(student_data, roll_number, context, "success")
                        
                        # Store student data in context
                        context['student_data'] = student_data
                        context['api_response'] = {
                            'status_code': response.status_code,
                            'success': True,
                            'url': api_url,
                            'roll_number': roll_number
                        }
                        
                        # Extract specific fields from API response (robust to key casing)
                        def pick(d: Dict[str, Any], keys: list) -> Optional[Any]:
                            for k in keys:
                                if isinstance(d, dict) and k in d:
                                    return d.get(k)
                            # Try case-insensitive lookup
                            if isinstance(d, dict):
                                lower_map = {str(k).lower(): k for k in d.keys()}
                                for k in keys:
                                    lk = str(k).lower()
                                    if lk in lower_map:
                                        return d.get(lower_map[lk])
                            return None
                        
                        student_class = None
                        exam_code = None
                        student_code = None
                        
                        if isinstance(student_data, dict):
                            student_class = pick(student_data, ['Class', 'StudentClass'])
                            exam_code = pick(student_data, ['ExamCode'])
                            student_code = pick(student_data, ['StudentCode'])
                            
                            # Also check common nesting keys if not found at top-level
                            if student_class is None or exam_code is None or student_code is None:
                                for nest_key in ['data', 'student', 'result']:
                                    nested = student_data.get(nest_key)
                                    if isinstance(nested, dict):
                                        student_class = student_class or pick(nested, ['Class', 'StudentClass'])
                                        exam_code = exam_code or pick(nested, ['ExamCode'])
                                        student_code = student_code or pick(nested, ['StudentCode'])
                        
                        # Persist to context if available
                        if student_class is not None:
                            context['student_class'] = student_class
                        if exam_code is not None:
                            context['exam_code'] = exam_code
                        if student_code is not None:
                            context['student_code'] = student_code
                        
                        return self.create_stage_result(
                            success=True,
                            student_data=student_data,
                            api_response=context['api_response'],
                            roll_number=roll_number,
                            student_class=student_class,
                            exam_code=exam_code,
                            student_code=student_code
                        )
                        
                    except json.JSONDecodeError as e:
                        print(f"[{class_name}] ❌ ERROR: Failed to parse JSON response")
                        print(f"[{class_name}] JSON Error: {str(e)}")
                        print(f"[{class_name}] Response content: {response.text[:500]}...")
                        
                        return self.create_stage_result(
                            success=False,
                            error=f"Invalid JSON response from API: {str(e)}",
                            student_data=None,
                            api_response={
                                'status_code': response.status_code,
                                'success': False,
                                'url': api_url,
                                'roll_number': roll_number,
                                'error': 'Invalid JSON'
                            }
                        )
                
                elif response.status_code == 404:
                    print(f"[{class_name}] ❌ ERROR: Student not found (404)")
                    print(f"[{class_name}] Response content: {response.text}")
                    
                    # Write error response to error file
                    error_data = {
                        'status_code': response.status_code,
                        'error': 'Student not found',
                        'roll_number': roll_number,
                        'url': api_url,
                        'response_text': response.text
                    }
                    self._write_json_to_file(error_data, roll_number, context, "error")
                    
                    return self.create_stage_result(
                        success=False,
                        error="Student not found in database",
                        student_data=None,
                        api_response={
                            'status_code': response.status_code,
                            'success': False,
                            'url': api_url,
                            'roll_number': roll_number,
                            'error': 'Student not found'
                        }
                    )
                
                elif response.status_code == 401:
                    print(f"[{class_name}] ❌ ERROR: Unauthorized (401)")
                    print(f"[{class_name}] Response content: {response.text}")
                    
                    # Write error response to error file
                    error_data = {
                        'status_code': response.status_code,
                        'error': 'Unauthorized access',
                        'roll_number': roll_number,
                        'url': api_url,
                        'response_text': response.text
                    }
                    self._write_json_to_file(error_data, roll_number, context, "error")
                    
                    return self.create_stage_result(
                        success=False,
                        error="Unauthorized access to API",
                        student_data=None,
                        api_response={
                            'status_code': response.status_code,
                            'success': False,
                            'url': api_url,
                            'roll_number': roll_number,
                            'error': 'Unauthorized'
                        }
                    )
                
                else:
                    print(f"[{class_name}] ❌ ERROR: API returned status code {response.status_code}")
                    print(f"[{class_name}] Response content: {response.text}")
                    
                    # Write error response to error file
                    error_data = {
                        'status_code': response.status_code,
                        'error': f'HTTP {response.status_code}',
                        'roll_number': roll_number,
                        'url': api_url,
                        'response_text': response.text
                    }
                    self._write_json_to_file(error_data, roll_number, context, "error")
                    
                    return self.create_stage_result(
                        success=False,
                        error=f"API error: HTTP {response.status_code}",
                        student_data=None,
                        api_response={
                            'status_code': response.status_code,
                            'success': False,
                            'url': api_url,
                            'roll_number': roll_number,
                            'error': f'HTTP {response.status_code}'
                        }
                    )
                    
            except requests.exceptions.Timeout:
                print(f"[{class_name}] ❌ ERROR: API request timeout")
                return self.create_stage_result(
                    success=False,
                    error="API request timeout",
                    student_data=None,
                    api_response={
                        'status_code': None,
                        'success': False,
                        'url': api_url,
                        'roll_number': roll_number,
                        'error': 'Timeout'
                    }
                )
                
            except requests.exceptions.ConnectionError:
                print(f"[{class_name}] ❌ ERROR: Connection error to API")
                return self.create_stage_result(
                    success=False,
                    error="Connection error to API server",
                    student_data=None,
                    api_response={
                        'status_code': None,
                        'success': False,
                        'url': api_url,
                        'roll_number': roll_number,
                        'error': 'Connection error'
                    }
                )
                
            except requests.exceptions.RequestException as e:
                print(f"[{class_name}] ❌ ERROR: Request exception: {str(e)}")
                return self.create_stage_result(
                    success=False,
                    error=f"API request failed: {str(e)}",
                    student_data=None,
                    api_response={
                        'status_code': None,
                        'success': False,
                        'url': api_url,
                        'roll_number': roll_number,
                        'error': str(e)
                    }
                )
                
        except Exception as e:
            print(f"[{class_name}] ❌ EXCEPTION in fetch_student_stage: {str(e)}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            
            return self.create_stage_result(
                success=False,
                error=f"Unexpected error in fetch student stage: {str(e)}",
                student_data=None,
                api_response=None
            )
        
        finally:
            print(f"[{class_name}] ====== Fetch Student Stage Complete ======")
    
    def _write_json_to_file(self, json_data: Dict[str, Any], roll_number: str, context: Dict[str, Any], folder_type: str) -> str:
        """
        Write JSON response to a file in the specified folder (success or error).
        
        Args:
            json_data: The JSON data to write
            roll_number: The roll number for filename
            context: Pipeline context (to get output folder info)
            folder_type: Either "success" or "error"
            
        Returns:
            Path to the written JSON file
        """
        class_name = self.__class__.__name__
        
        try:
            # Get the output folder from the processor
            output_folder = getattr(self.processor, 'output_folder', None)
            if not output_folder:
                print(f"[{class_name}] WARNING: No output folder found, cannot write JSON file")
                return None
            
            # Create the target folder
            target_folder = os.path.join(output_folder, folder_type)
            os.makedirs(target_folder, exist_ok=True)
            print(f"[{class_name}] Created/verified {folder_type} folder: {target_folder}")
            
            # Sanitize roll number for filename
            safe_roll_number = "".join(c for c in roll_number if c.isalnum() or c in ('_', '-'))
            if not safe_roll_number:
                safe_roll_number = "unknown_roll"
            
            # Create JSON filename
            json_filename = f"{safe_roll_number}_student_data.json"
            json_file_path = os.path.join(target_folder, json_filename)
            
            # Write JSON data to file
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"[{class_name}] ✅ JSON response written to: {json_file_path}")
            print(f"[{class_name}] JSON file size: {os.path.getsize(json_file_path)} bytes")
            
            return json_file_path
            
        except Exception as e:
            print(f"[{class_name}] ❌ ERROR writing JSON file: {str(e)}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            return None
