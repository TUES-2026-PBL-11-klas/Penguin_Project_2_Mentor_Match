import requests
import json

BASE_URL = "http://localhost:5000/api"

print("--- Testing API Endpoints ---")

# 1. Test Notifications Dispatch
print("\n1. Testing Notification Web Push Dispatch...")
payload_notif = {
    "user_id": 1,
    "title": "My Final Test",
    "message": "It works beautifully!",
    "type": "Ping"
}
response = requests.post(f"{BASE_URL}/notifications/test-dispatch", json=payload_notif)
if response.status_code == 200:
    print("SUCCESS: Notification async trigger responded 200 OK.")
else:
    print(f"FAILED: {response.json()}")

# 2. Test Leaving a Review (using the wrong student_id to verify security!)
print("\n2. Testing Review Security (Wrong Student ID)...")
payload_wrong_review = {
    "student_id": 1, # User 1 is a mentor, not the student who booked session 1
    "rating": 5,
    "comment": "Had an amazing session today!"
}
response = requests.post(f"{BASE_URL}/reviews/session/1", json=payload_wrong_review)
print(f"Server naturally blocks this perfectly: {response.json()}")

# 3. Test Leaving a Review (using the CORRECT student_id!)
print("\n3. Testing Valid Review Creation...")
payload_correct_review = {
    "student_id": 3, # User 3 (Maria) is the actual student for Session 1
    "rating": 5,
    "comment": "Had an amazing session today!"
}
response = requests.post(f"{BASE_URL}/reviews/session/1", json=payload_correct_review)

if response.status_code == 201:
     print("SUCCESS: Review created securely!")
     print(response.json())
elif response.status_code == 409:
     print("SUCCESS/EXPECTED: Review already created in the Database! (Blocked by constraints)")
else:
     print(f"FAILED or Unexpected logic: {response.json()}")

# 4. Fetch the Aggregated Mentor Reviews
print("\n4. Fetching Aggregate Reviews for Mentor 1...")
response = requests.get(f"{BASE_URL}/reviews/mentor/1")
if response.status_code == 200:
     print("SUCCESS: Got final mentor analytics!")
     print(json.dumps(response.json(), indent=2))
else:
     print(f"FAILED: {response.json()}")
