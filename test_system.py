import requests
import json

# Test ticket generation
ticket_id = "TEST123"
response = requests.post(f"http://localhost:8000/generate-ticket/{ticket_id}")
print("\nGenerated Ticket Response:")
print(json.dumps(response.json(), indent=2))

# Test ticket verification
ticket_data = response.json()["ticket_data"]
verify_response = requests.post("http://localhost:8000/verify-ticket/", 
                              json={"encoded_data": ticket_data})
print("\nVerification Response:")
print(json.dumps(verify_response.json(), indent=2))

# Test duplicate verification (should fail)
verify_response2 = requests.post("http://localhost:8000/verify-ticket/", 
                               json={"encoded_data": ticket_data})
print("\nDuplicate Verification Response:")
print("Status Code:", verify_response2.status_code)
print(json.dumps(verify_response2.json(), indent=2))
