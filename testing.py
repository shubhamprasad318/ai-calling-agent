import requests

# Replace with the phone number you want to call
target_number = "+1234456677"  # Format: +1 for US, +91 for India, etc.

# Your ngrok URL
base_url = "https://27a4-125-63-120-158.ngrok-free.app"

# Make the API call
try:
    response = requests.post(
        f"{base_url}/make-call",
        json={"to_number": target_number}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Call initiated successfully!")
        print(f"Call SID: {result['call_sid']}")
        print(f"Status: {result['status']}")
        print(f"To: {result['to']}")
        print(f"From: {result['from']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error making request: {e}")