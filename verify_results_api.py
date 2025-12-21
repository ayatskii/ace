import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_step(step):
    print(f"\n{'='*20} {step} {'='*20}")

def verify_api():
    # 1. Register a new user
    print_step("Registering User")
    email = f"verify_{int(time.time())}@example.com"
    password = "password123"
    
    payload = {
        "email": email,
        "password": password,
        "full_name": "Verification User",
        "role": "student"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if resp.status_code == 201:
            print("✅ Registration successful")
        else:
            print(f"❌ Registration failed: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Login
    print_step("Logging In")
    login_data = {
        "username": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # 3. Get Test Templates
    print_step("Fetching Templates")
    resp = requests.get(f"{BASE_URL}/tests/templates", headers=headers)
    templates = resp.json()
    if not templates:
        print("❌ No test templates found")
        return
    
    test_id = templates[0]["id"]
    print(f"✅ Found test template: {test_id}")

    # 4. Start Attempt
    print_step("Starting Attempt")
    resp = requests.post(f"{BASE_URL}/tests/attempts", json={"test_template_id": test_id}, headers=headers)
    if resp.status_code != 201:
        print(f"❌ Start attempt failed: {resp.text}")
        return
    
    attempt = resp.json()
    attempt_id = attempt["id"]
    print(f"✅ Started attempt: {attempt_id}")

    # 5. Submit Attempt (with CORRECT answers)
    print_step("Submitting Attempt")
    
    resp = requests.get(f"{BASE_URL}/tests/attempts/{attempt_id}", headers=headers)
    structure = resp.json().get("test_structure", {})
    
    listening_answers = []
    if structure.get("listening_questions"):
        for q in structure["listening_questions"]:
            ans = "A"
            q_type = str(q.get("question_type", "")).lower()
            if "map" in q_type:
                ans = "Library"
            elif "blank" in q_type:
                ans = "technology"
            
            listening_answers.append({"question_id": q["id"], "user_answer": ans})

    reading_answers = []
    if structure.get("reading_questions"):
        for q in structure["reading_questions"]:
            ans = "A"
            q_type = str(q.get("question_type", "")).lower()
            if "true" in q_type:
                ans = "TRUE"
            elif "heading" in q_type:
                ans = "i"
            elif "completion" in q_type:
                ans = "universe"
            
            reading_answers.append({"question_id": q["id"], "user_answer": ans})

    submission_payload = {
        "listening_answers": listening_answers,
        "reading_answers": reading_answers,
        "writing_answers": []
    }
    
    resp = requests.put(f"{BASE_URL}/tests/attempts/{attempt_id}/submit", json=submission_payload, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Submission failed: {resp.text}")
        return
    print("✅ Submission successful")

    # 6. Check Results API
    print_step("Checking Results API")
    resp = requests.get(f"{BASE_URL}/tests/attempts/me", headers=headers)
    attempts = resp.json()
    
    latest_attempt = attempts[0]
    print(json.dumps(latest_attempt, indent=2))
    
    if "result" in latest_attempt and latest_attempt["result"] is not None:
        result = latest_attempt["result"]
        print(f"\n✅ Result found: Listening={result.get('listening_score')}, Reading={result.get('reading_score')}")
        
        if result.get('listening_score', 0) > 0 and result.get('reading_score', 0) > 0:
             print("✅ SUCCESS: Scores are greater than 0!")
        else:
             print("❌ FAILURE: Scores are 0. Grading might be broken.")
    else:
        print("\n❌ FAILURE: 'result' field is missing or null.")

    if "test_template" in latest_attempt and latest_attempt["test_template"] is not None:
        print("✅ SUCCESS: 'test_template' field is present and populated!")
    else:
        print("❌ FAILURE: 'test_template' field is missing or null.")

if __name__ == "__main__":
    verify_api()
