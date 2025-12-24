import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_DATA = {}

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print(f"{'='*60}")

def test_health():
    print_step(1, "Health Checks")
    
    # Test root
    response = requests.get(f"{BASE_URL}/")
    print(f"GET / - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Test health
    response = requests.get(f"{BASE_URL}/health")
    print(f"GET /health - Status: {response.status_code}")
    assert response.status_code == 200
    
    print("✅ Health checks passed")

def test_auth():
    print_step(2, "Authentication")
    
    # Create test user
    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "username": "testuser"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"POST /signup - Status: {response.status_code}")
    assert response.status_code == 201
    TEST_DATA['user_id'] = response.json().get('id')
    
    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user_data['email'], "password": user_data['password']},
        headers={"Content-Type": "application/json"}
    )
    print(f"POST /login - Status: {response.status_code}")
    assert response.status_code == 200
    TEST_DATA['user_token'] = response.json().get('access_token')
    TEST_DATA['user_refresh'] = response.json().get('refresh_token')
    
    # Get profile
    headers = {"Authorization": f"Bearer {TEST_DATA['user_token']}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"GET /me - Status: {response.status_code}")
    assert response.status_code == 200
    
    print("✅ Authentication tests passed")

def test_scanning():
    print_step(3, "Scanning Endpoints")
    
    headers = {"Authorization": f"Bearer {TEST_DATA['user_token']}", 
               "Content-Type": "application/json"}
    
    # Test DNS scan
    dns_data = {"domain": "google.com"}
    response = requests.post(
        f"{BASE_URL}/api/scans/dns",
        json=dns_data,
        headers=headers
    )
    print(f"POST /scans/dns - Status: {response.status_code}")
    assert response.status_code == 200
    TEST_DATA['scan_id'] = response.json().get('id')
    
    # Wait for scan to complete
    time.sleep(2)
    
    # Get scan result
    response = requests.get(
        f"{BASE_URL}/api/scans/{TEST_DATA['scan_id']}",
        headers=headers
    )
    print(f"GET /scans/{{id}} - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Test WHOIS
    whois_data = {"domain": "github.com"}
    response = requests.post(
        f"{BASE_URL}/api/scans/whois",
        json=whois_data,
        headers=headers
    )
    print(f"POST /scans/whois - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Test IP scan
    ip_data = {"ip": "8.8.8.8"}
    response = requests.post(
        f"{BASE_URL}/api/scans/ip",
        json=ip_data,
        headers=headers
    )
    print(f"POST /scans/ip - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Get scan history
    response = requests.get(
        f"{BASE_URL}/api/scans/user/history?limit=5",
        headers=headers
    )
    print(f"GET /scans/user/history - Status: {response.status_code}")
    assert response.status_code == 200
    
    print("✅ Scanning tests passed")

def test_user_management():
    print_step(4, "User Management")
    
    headers = {"Authorization": f"Bearer {TEST_DATA['user_token']}", 
               "Content-Type": "application/json"}
    
    # Update profile
    profile_data = {"full_name": "Updated Test User", "bio": "Testing Fsociety"}
    response = requests.put(
        f"{BASE_URL}/api/user/profile",
        json=profile_data,
        headers=headers
    )
    print(f"PUT /user/profile - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Get activities
    response = requests.get(
        f"{BASE_URL}/api/user/activities",
        headers=headers
    )
    print(f"GET /user/activities - Status: {response.status_code}")
    assert response.status_code == 200
    
    # Get stats
    response = requests.get(
        f"{BASE_URL}/api/user/stats",
        headers=headers
    )
    print(f"GET /user/stats - Status: {response.status_code}")
    assert response.status_code == 200
    
    print("✅ User management tests passed")

def test_cleanup():
    print_step(5, "Cleanup")
    
    headers = {"Authorization": f"Bearer {TEST_DATA['user_token']}", 
               "Content-Type": "application/json"}
    
    # Delete scan
    response = requests.delete(
        f"{BASE_URL}/api/scans/{TEST_DATA['scan_id']}",
        headers=headers
    )
    print(f"DELETE /scans/{{id}} - Status: {response.status_code}")
    
    # Logout
    logout_data = {"refresh_token": TEST_DATA['user_refresh']}
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        json=logout_data,
        headers=headers
    )
    print(f"POST /logout - Status: {response.status_code}")
    
    print("✅ Cleanup tests passed")

def run_all_tests():
    try:
        test_health()
        test_auth()
        test_scanning()
        test_user_management()
        test_cleanup()
        
        print(f"\n{'='*60}")
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()