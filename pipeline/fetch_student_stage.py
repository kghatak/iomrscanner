#!/usr/bin/env python3
"""
Fetch Student Stage Implementation

This stage fetches student data from the backend API after roll number extraction.
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any
from .base_stage import PipelineStage


class FetchStudentStage(PipelineStage):
    """Stage 4: Fetch student data from backend API using roll number"""
    
    def __init__(self, processor_instance):
        super().__init__(processor_instance)
        # Backend API configuration
        self.base_url = "https://bigmandev03.azurewebsites.net"
        #self.base_url = "http://localhost:5010"
        self.endpoint = "/result/roll"
        # Default tenant (will be overridden from context)
        self.default_tenant = "c2023-jgm"
        self.headers = {
            "Content-Type": "application/json",
            "user-tenantid": self.default_tenant
        }
    
    def get_stage_name(self) -> str:
        return "fetch_student"
    
    def get_stage_description(self) -> str:
        return "Fetch student data from backend API"
    
    def _make_api_call(self, roll_number: str, headers: Dict[str, str], class_name: str) -> tuple:
        """
        Make the API call to fetch student data for a given roll number.
        Includes retry logic for 404 responses.
        
        Args:
            roll_number: The roll number to look up
            headers: HTTP headers for the request
            class_name: Class name for logging
            
        Returns:
            Tuple of (response, api_url, retry_count) or raises an exception
        """
        import urllib.parse
        encoded_roll_number = urllib.parse.quote(roll_number, safe='')
        api_url = f"{self.base_url}{self.endpoint}/{encoded_roll_number}"
        
        print(f"[{class_name}] API URL: {api_url}")
        print(f"[{class_name}] Headers: {headers}")
        
        max_retries = 1  # Retry once for 404
        retry_count = 0
        response = None
        
        print(f"[{class_name}] Making API request...")
        while retry_count <= max_retries:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=30  # 30 second timeout
            )
            
            print(f"[{class_name}] API Response Status: {response.status_code}")
            print(f"[{class_name}] API Response Headers: {dict(response.headers)}")
            
            # If 404 and we haven't retried yet, wait and retry
            if response.status_code == 404 and retry_count < max_retries:
                retry_count += 1
                print(f"[{class_name}] ⚠️ Received 404, retrying (attempt {retry_count}/{max_retries})...")
                print(f"[{class_name}] Waiting 1 second before retry...")
                time.sleep(1)  # Wait 1 second before retry
                print(f"[{class_name}] 🔄 Retrying API request...")
                continue  # Retry the request
            
            # Break out of loop if not 404 or if we've already retried
            break
        
        return response, api_url, retry_count
    
    def _handle_success_response(self, response, roll_number: str, api_url: str, context: Dict[str, Any], class_name: str) -> Dict[str, Any]:
        """
        Handle a successful (200) API response - parse student data and return stage result.
        
        Args:
            response: The HTTP response object
            roll_number: The roll number used
            api_url: The API URL called
            context: Pipeline context
            class_name: Class name for logging
            
        Returns:
            Stage result dictionary
        """
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
            
            # Get tenant from context (default to c2023-jgm if not provided)
            tenant = context.get('tenant', self.default_tenant)
            print(f"[{class_name}] Using tenant from context: {tenant}")
            
            # Update headers with tenant from context
            headers = {
                "Content-Type": "application/json",
                "user-tenantid": tenant
            }
            
            try:
                response, api_url, retry_count = self._make_api_call(roll_number, headers, class_name)
                
                # Check if request was successful
                if response.status_code == 200:
                    return self._handle_success_response(response, roll_number, api_url, context, class_name)
                
                elif response.status_code == 404:
                    # This means we got 404 after retry(ies)
                    if retry_count > 0:
                        print(f"[{class_name}] ❌ ERROR: Student not found (404) after {retry_count} retry attempt(s)")
                    else:
                        print(f"[{class_name}] ❌ ERROR: Student not found (404)")
                    print(f"[{class_name}] Response content: {response.text}")
                    
                    # --- Ask user to correct the roll number via dialog ---
                    print(f"[{class_name}] 🔄 Roll number '{roll_number}' may be incorrect. Asking user for correction...")
                    roll_number_input_helper = context.get('_roll_number_input_helper')
                    expected_prefix = context.get('expected_roll_number_prefix', '')
                    
                    if roll_number_input_helper and callable(roll_number_input_helper):
                        print(f"[{class_name}] Dialog helper available, requesting user input...")
                        print(f"[{class_name}] Expected prefix: '{expected_prefix}'")
                        
                        # Use rotated image path if available, otherwise original
                        image_to_show = context.get('rotated_image_path', image_path)
                        
                        try:
                            user_roll_number = roll_number_input_helper(image_to_show, expected_prefix)
                            if user_roll_number:
                                print(f"[{class_name}] ✅ User provided corrected roll number: '{user_roll_number}'")
                                
                                # Update context with the corrected roll number
                                context['roll_number'] = user_roll_number
                                
                                # Update prefix/suffix in context if the corrected roll number has a dash
                                if '-' in user_roll_number:
                                    # Find the last dash followed by exactly 4 digits
                                    import re
                                    dash_match = re.search(r'^(.*)-(\d{4})$', user_roll_number)
                                    if dash_match:
                                        context['roll_number_prefix'] = dash_match.group(1)
                                        context['roll_number_suffix'] = dash_match.group(2)
                                        print(f"[{class_name}] Updated context - roll_number_prefix: '{dash_match.group(1)}', roll_number_suffix: '{dash_match.group(2)}'")
                                
                                # Retry API call with corrected roll number
                                print(f"[{class_name}] 🔄 Retrying API call with corrected roll number: '{user_roll_number}'")
                                try:
                                    new_response, new_api_url, new_retry_count = self._make_api_call(user_roll_number, headers, class_name)
                                    
                                    if new_response.status_code == 200:
                                        return self._handle_success_response(new_response, user_roll_number, new_api_url, context, class_name)
                                    else:
                                        print(f"[{class_name}] ❌ ERROR: API still returned {new_response.status_code} with corrected roll number")
                                        print(f"[{class_name}] Response content: {new_response.text}")
                                        
                                        # Write error response to error file
                                        error_data = {
                                            'status_code': new_response.status_code,
                                            'error': f'Student not found after user correction (HTTP {new_response.status_code})',
                                            'original_roll_number': roll_number,
                                            'corrected_roll_number': user_roll_number,
                                            'url': new_api_url,
                                            'response_text': new_response.text,
                                            'retry_count': new_retry_count
                                        }
                                        self._write_json_to_file(error_data, user_roll_number, context, "error")
                                        
                                        return self.create_stage_result(
                                            success=False,
                                            error=f"Student not found in database (even after user correction to '{user_roll_number}')",
                                            student_data=None,
                                            api_response={
                                                'status_code': new_response.status_code,
                                                'success': False,
                                                'url': new_api_url,
                                                'roll_number': user_roll_number,
                                                'original_roll_number': roll_number,
                                                'error': 'Student not found after correction',
                                                'retry_count': new_retry_count
                                            }
                                        )
                                        
                                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                                    print(f"[{class_name}] ❌ ERROR: API request failed with corrected roll number: {str(e)}")
                                    return self.create_stage_result(
                                        success=False,
                                        error=f"API request failed with corrected roll number: {str(e)}",
                                        student_data=None,
                                        api_response={
                                            'status_code': None,
                                            'success': False,
                                            'roll_number': user_roll_number,
                                            'original_roll_number': roll_number,
                                            'error': str(e)
                                        }
                                    )
                            else:
                                print(f"[{class_name}] ❌ User cancelled roll number input")
                        except Exception as e:
                            print(f"[{class_name}] ⚠️ Exception while showing roll number dialog: {str(e)}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"[{class_name}] ⚠️ Roll number input dialog helper not available in context")
                    
                    # If we get here, either user cancelled, dialog wasn't available, or dialog errored
                    # Write error response to error file
                    error_data = {
                        'status_code': response.status_code,
                        'error': 'Student not found',
                        'roll_number': roll_number,
                        'url': api_url,
                        'response_text': response.text,
                        'retry_count': retry_count
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
                            'error': 'Student not found',
                            'retry_count': retry_count
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
