import requests
import json
import sys

# URL of your local FastAPI backend
url = "http://localhost:8000/generate-schedule"

try:
    # Open all CSV files from the test_data directory
    files = {
        'students': open('test_data/students.csv', 'rb'),
        'teachers': open('test_data/teachers.csv', 'rb'),
        'slots': open('test_data/slots.csv', 'rb'),
        'busy': open('test_data/busy.csv', 'rb')
    }

    print("Sending request to generate schedule...")
    response = requests.post(url, files=files)
    
    # Close files after request
    for f in files.values():
        f.close()

    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Response Body (Schedule):")
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print("Error Response:")
        print(response.text)

except FileNotFoundError as e:
    print(f"Error: Could not find test data files. {e}")
except Exception as e:
    print(f"An error occurred: {e}")
