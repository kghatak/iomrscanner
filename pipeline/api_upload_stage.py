#!/usr/bin/env python3
"""
API Upload Stage Implementation

This stage uploads processed data to API.
"""

import os
import time
import uuid
import requests
import urllib.parse
from .base_stage import PipelineStage
from typing import Dict, Any


class APIUploadStage(PipelineStage):
    """Stage 5: Upload processed data to API"""
    
    def __init__(self, processor_instance):
        super().__init__(processor_instance)
        # Backend API configuration (same as FetchStudentStage)
        self.base_url = "https://bigmandev03.azurewebsites.net"
        # self.base_url = "http://localhost:5010"
        self.endpoint = "/result/roll"
    
    def get_stage_name(self) -> str:
        return "api_upload"
    
    def get_stage_description(self) -> str:
        return "Upload processed data to API"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting API Upload Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Get answer validation result from context
            answer_validation_result = context.get('answer_validation_result')
            roll_number = context.get('roll_number', 'Unknown')
            
            print(f"[{class_name}] Roll number from context: {roll_number}")
            print(f"[{class_name}] Answer validation result available: {bool(answer_validation_result)}")
            
            if not answer_validation_result:
                error_msg = "No answer validation result found in context. Cannot upload."
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    upload_id=None
                )
            
            print(f"[{class_name}] Answer validation result keys: {list(answer_validation_result.keys())}")
            
            # Get tenant from context (required for headers)
            tenant = context.get('tenant', 'c2023-jgm')
            print(f"[{class_name}] Using tenant: {tenant}")
            
            # Make actual API PATCH call
            print(f"[{class_name}] Initiating API PATCH upload")
            upload_result = self._upload_to_api(answer_validation_result, roll_number, tenant)
            print(f"[{class_name}] API upload complete")
            print(f"[{class_name}] Upload success: {upload_result['success']}")
            
            if upload_result['success']:
                print(f"[{class_name}] ✅ SUCCESS: Data uploaded successfully")
                print(f"[{class_name}] API Response Status: {upload_result.get('status_code')}")
                print(f"[{class_name}] API Response: {upload_result.get('response')}")
                print(f"[{class_name}] Returning success result")
                return self.create_stage_result(
                    success=True,
                    upload_id=upload_result.get('upload_id'),
                    api_response=upload_result.get('response'),
                    status_code=upload_result.get('status_code')
                )
            else:
                error_msg = upload_result.get('error', 'Unknown error')
                print(f"[{class_name}] ❌ FAILURE: Upload failed - {error_msg}")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    upload_id=None,
                    status_code=upload_result.get('status_code')
                )
                
        except Exception as e:
            error_msg = f"API upload failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Returning failure result")
            return self.create_stage_result(
                success=False,
                error=error_msg,
                upload_id=None
            )
        finally:
            print(f"[{class_name}] ====== API Upload Stage Complete ======\n")
    
    def _upload_to_api(self, payload: Dict[str, Any], roll_number: str, tenant: str) -> Dict[str, Any]:
        """
        Upload answer validation result to API via PATCH request with retry logic.
        
        Args:
            payload: Answer validation result dictionary (from context['answer_validation_result'])
            roll_number: Roll number for URL endpoint (format: "JGMR2507-0105" -> roll="JGMR2507", number="0105")
            tenant: Tenant ID for headers
            
        Returns:
            Upload result dictionary with success status, response, and error information
        """
        class_name = self.__class__.__name__
        print(f"[{class_name}] _upload_to_api() called")
        print(f"[{class_name}] Roll number: {roll_number}")
        print(f"[{class_name}] Tenant: {tenant}")
        print(f"[{class_name}] Full payload keys: {list(payload.keys())}")
        
        # Parse roll number to extract roll and number parts
        # Format: "JGMR2507-0105" -> roll="JGMR2507", number="0105"
        if '-' in roll_number:
            roll, number = roll_number.split('-', 1)
        else:
            # If no dash, try to split at a reasonable point (e.g., last 4 digits as number)
            # This is a fallback - ideally roll numbers should have dashes
            print(f"[{class_name}] ⚠️  WARNING: Roll number has no dash separator. Attempting to parse...")
            if len(roll_number) >= 4:
                roll = roll_number[:-4]
                number = roll_number[-4:]
            else:
                roll = roll_number
                number = ""
                print(f"[{class_name}] ⚠️  WARNING: Could not parse roll number. Using full value as roll.")
        
        print(f"[{class_name}] Parsed roll: {roll}, number: {number}")
        
        # Filter payload to only include category marks (exclude metadata)
        # Exclude: roll_number, tenant, total_marks_obtained, correct_answers, incorrect_answers, skipped_answers
        excluded_keys = {'roll_number', 'tenant', 'total_marks_obtained', 'correct_answers', 
                        'incorrect_answers', 'skipped_answers'}
        category_payload = {k: v for k, v in payload.items() if k not in excluded_keys}
        
        print(f"[{class_name}] Category payload keys: {list(category_payload.keys())}")
        print(f"[{class_name}] Category payload: {category_payload}")
        
        # Prepare headers (same format as FetchStudentStage)
        headers = {
            "Content-Type": "application/json",
            "user-tenantid": tenant
        }
        
        # URL encode roll and number for the API endpoint
        encoded_roll = urllib.parse.quote(roll, safe='')
        encoded_number = urllib.parse.quote(number, safe='')
        api_url = f"{self.base_url}{self.endpoint}/{encoded_roll}/{encoded_number}"
        
        print(f"[{class_name}] API URL: {api_url}")
        print(f"[{class_name}] Headers: {headers}")
        
        # Retry logic: 3 attempts with 1 second wait between retries
        max_retries = 3
        retry_count = 0
        last_error = None
        last_status_code = None
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    print(f"[{class_name}] ⏳ Waiting 1 second before retry {retry_count}/{max_retries}...")
                    time.sleep(1)
                    print(f"[{class_name}] 🔄 Retrying API request (attempt {retry_count + 1}/{max_retries + 1})...")
                else:
                    print(f"[{class_name}] Making PATCH request (attempt 1/{max_retries + 1})...")
                
                # Make PATCH request
                response = requests.patch(
                    api_url,
                    json=category_payload,
                    headers=headers,
                    timeout=30  # 30 second timeout
                )
                
                last_status_code = response.status_code
                print(f"[{class_name}] API Response Status: {response.status_code}")
                print(f"[{class_name}] API Response Headers: {dict(response.headers)}")
                
                # Try to parse JSON response
                try:
                    response_json = response.json()
                    print(f"[{class_name}] API Response JSON: {response_json}")
                except ValueError:
                    response_text = response.text[:500]  # First 500 chars
                    print(f"[{class_name}] API Response (non-JSON): {response_text}")
                    response_json = {'raw_response': response_text}
                
                # Check if request was successful (2xx status codes)
                if 200 <= response.status_code < 300:
                    print(f"[{class_name}] ✅ Upload successful (Status: {response.status_code})")
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'response': response_json,
                        'upload_id': response_json.get('upload_id') or response_json.get('id') or str(uuid.uuid4()),
                        'retry_count': retry_count
                    }
                else:
                    # Non-2xx status code - will retry if attempts remain
                    error_msg = f"API returned error status {response.status_code}: {response_json.get('message', response.text[:200])}"
                    last_error = error_msg
                    print(f"[{class_name}] ❌ Upload failed: {error_msg}")
                    
                    if retry_count < max_retries:
                        print(f"[{class_name}] Will retry after waiting...")
                        retry_count += 1
                        continue
                    else:
                        # No more retries
                        return {
                            'success': False,
                            'status_code': response.status_code,
                            'response': response_json,
                            'error': error_msg,
                            'upload_id': None,
                            'retry_count': retry_count
                        }
                    
            except requests.exceptions.Timeout:
                error_msg = "API request timed out after 30 seconds"
                last_error = error_msg
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    return {
                        'success': False,
                        'status_code': None,
                        'response': None,
                        'error': error_msg,
                        'upload_id': None,
                        'retry_count': retry_count
                    }
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                last_error = error_msg
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    return {
                        'success': False,
                        'status_code': None,
                        'response': None,
                        'error': error_msg,
                        'upload_id': None,
                        'retry_count': retry_count
                    }
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                last_error = error_msg
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    return {
                        'success': False,
                        'status_code': None,
                        'response': None,
                        'error': error_msg,
                        'upload_id': None,
                        'retry_count': retry_count
                    }
                    
            except Exception as e:
                error_msg = f"Unexpected error during API upload: {str(e)}"
                last_error = error_msg
                print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
                import traceback
                print(f"[{class_name}] Traceback: {traceback.format_exc()}")
                
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    return {
                        'success': False,
                        'status_code': None,
                        'response': None,
                        'error': error_msg,
                        'upload_id': None,
                        'retry_count': retry_count
                    }
        
        # If we get here, all retries exhausted
        print(f"[{class_name}] ❌ All {max_retries + 1} attempts failed")
        return {
            'success': False,
            'status_code': last_status_code,
            'response': None,
            'error': last_error or 'All retry attempts exhausted',
            'upload_id': None,
            'retry_count': retry_count
        }
