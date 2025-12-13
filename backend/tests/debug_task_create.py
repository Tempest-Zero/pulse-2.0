"""
Debug script to identify the issue with test_create_task
Run this to see the actual validation error
"""

from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from fastapi import status

client = TestClient(app)

# Try the exact payload that's failing
test_payload = {
    "title": "Test Task",
    "duration": 1.0,
    "difficulty": "easy"
}

print("Testing task creation with payload:")
print(test_payload)
print("\n" + "="*60 + "\n")

response = client.post("/tasks", json=test_payload)

print(f"Status Code: {response.status_code}")
print(f"Expected: {status.HTTP_201_CREATED}")
print(f"\nResponse Body:")
import json
print(json.dumps(response.json(), indent=2))

if response.status_code == 422:
    print("\n" + "="*60)
    print("VALIDATION ERROR DETAILS:")
    print("="*60)
    error_detail = response.json().get("detail", [])
    if isinstance(error_detail, list):
        for i, error in enumerate(error_detail, 1):
            print(f"\nError {i}:")
            print(f"  Location: {error.get('loc', 'unknown')}")
            print(f"  Message: {error.get('msg', 'unknown')}")
            print(f"  Type: {error.get('type', 'unknown')}")
            if 'input' in error:
                print(f"  Input: {error.get('input')}")
    else:
        print(f"  {error_detail}")