#!/usr/bin/env python3
"""
Test script for API upload functionality with dummy data.

This script tests the PATCH API call to /result/roll/<roll>/<number> endpoint with dummy answer validation data.
"""

import requests
import urllib.parse
import json

# API configuration (same as in fetch_student_stage.py and api_upload_stage.py)
# BASE_URL = "https://bigmandev03.azurewebsites.net"
BASE_URL = "http://localhost:5010"  # Uncomment to test against localhost
ENDPOINT = "/result/roll"

# Dummy data - simulating answer_validation_result from AnswerValidationStage
def create_dummy_answer_validation_result():
    """Create dummy answer validation result data."""
    return {
        "roll_number": "JAMB2501-001",
        "tenant": "c2023-jgm",
        "Mathematics": 45,  # Marks obtained in Mathematics category
        "Physics": 38,       # Marks obtained in Physics category
        "Chemistry": 42,     # Marks obtained in Chemistry category
        "Biology": 40,       # Marks obtained in Biology category
        "total_marks_obtained": 165,
        "correct_answers": 82,
        "incorrect_answers": 15,
        "skipped_answers": 3
    }

def test_api_upload(roll_number: str, tenant: str, payload: dict):
    """
    Test API upload with PATCH request.
    
    Args:
        roll_number: Roll number for URL endpoint (format: "JGMR2507-0105" -> roll="JGMR2507", number="0105")
        tenant: Tenant ID for headers
        payload: Payload dictionary to send (should only contain category marks)
    """
    print("=" * 80)
    print("Testing API Upload")
    print("=" * 80)
    
    # Parse roll number to extract roll and number parts
    if '-' in roll_number:
        roll, number = roll_number.split('-', 1)
    else:
        # Fallback: if no dash, use last 4 digits as number
        if len(roll_number) >= 4:
            roll = roll_number[:-4]
            number = roll_number[-4:]
        else:
            roll = roll_number
            number = ""
            print(f"⚠️  WARNING: Could not parse roll number. Using full value as roll.")
    
    print(f"\nParsed roll: {roll}, number: {number}")
    
    # Filter payload to only include category marks (exclude metadata)
    excluded_keys = {'roll_number', 'tenant', 'total_marks_obtained', 'correct_answers', 
                    'incorrect_answers', 'skipped_answers'}
    category_payload = {k: v for k, v in payload.items() if k not in excluded_keys}
    
    # Prepare headers (same format as FetchStudentStage)
    headers = {
        "Content-Type": "application/json",
        "user-tenantid": tenant
    }
    
    # URL encode roll and number for the API endpoint
    encoded_roll = urllib.parse.quote(roll, safe='')
    encoded_number = urllib.parse.quote(number, safe='')
    api_url = f"{BASE_URL}{ENDPOINT}/{encoded_roll}/{encoded_number}"
    
    print(f"\nAPI URL: {api_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Category Payload: {json.dumps(category_payload, indent=2)}")
    print("\n" + "-" * 80)
    
    try:
        # Make PATCH request
        print("Making PATCH request...")
        response = requests.patch(
            api_url,
            json=category_payload,
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Try to parse JSON response
        try:
            response_json = response.json()
            print(f"\nResponse JSON:")
            print(json.dumps(response_json, indent=2))
        except ValueError:
            response_text = response.text
            print(f"\nResponse (non-JSON, first 1000 chars):")
            print(response_text[:1000])
            response_json = {'raw_response': response_text}
        
        # Check if request was successful (2xx status codes)
        if 200 <= response.status_code < 300:
            print("\n" + "=" * 80)
            print("✅ SUCCESS: Upload completed successfully!")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print(f"❌ FAILURE: API returned error status {response.status_code}")
            print("=" * 80)
            return False
            
    except requests.exceptions.Timeout:
        print("\n" + "=" * 80)
        print("❌ ERROR: API request timed out after 30 seconds")
        print("=" * 80)
        return False
    except requests.exceptions.ConnectionError as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: Connection error: {str(e)}")
        print("=" * 80)
        return False
    except requests.exceptions.RequestException as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: Request error: {str(e)}")
        print("=" * 80)
        return False
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ EXCEPTION: Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80)
        return False

def main():
    """Main test function."""
    print("\n" + "=" * 80)
    print("API Upload Test Script")
    print("=" * 80)
    
    # Test case 1: Default dummy data
    print("\n\nTest Case 1: Default Dummy Data")
    dummy_data = create_dummy_answer_validation_result()
    roll_number = dummy_data["roll_number"]
    tenant = dummy_data["tenant"]
    
    success = test_api_upload(roll_number, tenant, dummy_data)
    
    if success:
        print("\n✅ Test Case 1: PASSED")
    else:
        print("\n❌ Test Case 1: FAILED")
    
    # Test case 2: Different roll number and tenant (matching curl example format)
    print("\n\n" + "=" * 80)
    print("Test Case 2: Different Roll Number and Tenant (JGMR2507-0105 format)")
    print("=" * 80)
    dummy_data_2 = {
        "roll_number": "JGMR2507-0105",
        "tenant": "c2023-jgm",
        "ScienceEnvironment": 20,
        "Mathematics": 9,
        "ScienceTechDev": 13,
        "total_marks_obtained": 42,
        "correct_answers": 20,
        "incorrect_answers": 5,
        "skipped_answers": 0
    }
    
    success_2 = test_api_upload(
        dummy_data_2["roll_number"],
        dummy_data_2["tenant"],
        dummy_data_2
    )
    
    if success_2:
        print("\n✅ Test Case 2: PASSED")
    else:
        print("\n❌ Test Case 2: FAILED")
    
    # Test case 3: Minimal payload
    print("\n\n" + "=" * 80)
    print("Test Case 3: Minimal Payload (Only Required Fields)")
    print("=" * 80)
    minimal_data = {
        "roll_number": "TEST2501-0999",
        "tenant": "c2023-jgm",
        "Mathematics": 0,  # At least one category required
        "total_marks_obtained": 0,
        "correct_answers": 0,
        "incorrect_answers": 0,
        "skipped_answers": 0
    }
    
    success_3 = test_api_upload(
        minimal_data["roll_number"],
        minimal_data["tenant"],
        minimal_data
    )
    
    if success_3:
        print("\n✅ Test Case 3: PASSED")
    else:
        print("\n❌ Test Case 3: FAILED")
    
    print("\n" + "=" * 80)
    print("Test Script Complete")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Test Case 1: {'PASSED' if success else 'FAILED'}")
    print(f"  Test Case 2: {'PASSED' if success_2 else 'FAILED'}")
    print(f"  Test Case 3: {'PASSED' if success_3 else 'FAILED'}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

