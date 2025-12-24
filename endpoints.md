Excellent! Let's test all endpoints systematically. Here's a complete testing guide:

## 📋 **COMPLETE ENDPOINT TESTING GUIDE**

### **Prerequisites:**
1. Server running: `uvicorn app:app --host 0.0.0.0 --port 8000 --reload`
2. Postman or curl ready
3. We'll test in this order: Health → Auth → User → Scans → Admin

---

## ✅ **1. HEALTH ENDPOINTS**

### **1.1 Root Endpoint**
```
GET http://localhost:8000/
```
**Input:** None
**Expected Output (200):**
```json
{
    "message": "Fsociety API is running!",
    "version": "1.0.0",
    "endpoints": {
        "auth": "/api/auth",
        "user": "/api/user",
        "admin": "/api/admin",
        "scans": "/api/scans",
        "docs": "/docs",
        "health": "/health"
    }
}
```

### **1.2 Health Check**
```
GET http://localhost:8000/health
```
**Input:** None
**Expected Output (200):**
```json
{
    "status": "healthy",
    "services": {
        "auth": "operational",
        "database": "operational",
        "scanning": "operational"
    }
}
```

---

## 🔐 **2. AUTHENTICATION ENDPOINTS**

### **2.1 Create Regular User**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
    "email": "testuser@example.com",
    "password": "password123",
    "username": "testuser",
    "full_name": "Test User",
    "phone": "+1234567890",
    "company": "Test Corp"
}
```
**Expected Output (201):**
```json
{
    "id": "uuid-here",
    "email": "testuser@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "phone": "+1234567890",
    "company": "Test Corp",
    "role": "user",
    "created_at": "2024-01-15T10:30:00"
}
```
**Save:** User ID for later tests

### **2.2 Create Admin User**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
    "email": "admin@fsociety.com",
    "password": "admin123",
    "username": "admin",
    "role": "admin"
}
```
**Expected Output (201):** Similar to above with `"role": "admin"`

### **2.3 Login Regular User**
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
    "email": "testuser@example.com",
    "password": "password123"
}
```
**Expected Output (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": "same-uuid",
        "email": "testuser@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "phone": "+1234567890",
        "company": "Test Corp",
        "role": "user"
    }
}
```
**Save:** `ACCESS_TOKEN_USER` and `REFRESH_TOKEN_USER`

### **2.4 Login Admin User**
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
    "email": "admin@fsociety.com",
    "password": "admin123"
}
```
**Expected Output (200):** Similar with `"role": "admin"`
**Save:** `ACCESS_TOKEN_ADMIN` and `REFRESH_TOKEN_ADMIN`

### **2.5 Get Current User Profile**
```
GET http://localhost:8000/api/auth/me
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):** User profile data

### **2.6 Refresh Token**
```
POST http://localhost:8000/api/auth/refresh
Content-Type: application/json

{
    "refresh_token": "REFRESH_TOKEN_USER"
}
```
**Expected Output (200):**
```json
{
    "access_token": "new_token_here",
    "token_type": "bearer"
}
```

### **2.7 Invalid Login (Negative Test)**
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
    "email": "nonexistent@example.com",
    "password": "wrongpassword"
}
```
**Expected Output (401):**
```json
{"detail": "Invalid Credentials"}
```

---

## 👤 **3. USER MANAGEMENT ENDPOINTS**

### **3.1 Update User Profile**
```
PUT http://localhost:8000/api/user/profile
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "full_name": "Updated Name",
    "bio": "Security enthusiast and developer",
    "company": "New Security Corp"
}
```
**Expected Output (200):** Updated profile

### **3.2 Change Password**
```
PUT http://localhost:8000/api/user/password
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "current_password": "password123",
    "new_password": "newpassword456"
}
```
**Expected Output (200):**
```json
{"message": "Password changed successfully"}
```

### **3.3 Get User Activities**
```
GET http://localhost:8000/api/user/activities?limit=10&page=1
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):**
```json
{
    "activities": [],
    "total": 0,
    "page": 1,
    "limit": 10
}
```
*Initially empty, will populate after actions*

### **3.4 Get User Statistics**
```
GET http://localhost:8000/api/user/stats
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):**
```json
{
    "stats": {
        "total_scans": 0,
        "phishing_checks": 0,
        "vpn_configs": 0,
        "reports_generated": 0,
        "last_active": "2024-01-15T10:30:00"
    }
}
```

### **3.5 Try Admin Endpoint as User (Negative Test)**
```
GET http://localhost:8000/api/admin/users
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (403):**
```json
{"detail": "Admin access required"}
```

---

## 🔍 **4. SCANNING ENDPOINTS**

### **4.1 DNS Lookup**
```
POST http://localhost:8000/api/scans/dns
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "google.com"
}
```
**Expected Output (200):**
```json
{
    "id": "scan-uuid",
    "user_id": "user-uuid",
    "scan_type": "dns",
    "target": "google.com",
    "status": "completed",
    "results": {
        "a_records": ["142.250.185.78", ...],
        "aaaa_records": ["2607:f8b0:4004:c15::8a", ...],
        "mx_records": ["smtp.google.com", ...],
        "ns_records": ["ns1.google.com", ...],
        "txt_records": ["v=spf1 ...", ...],
        "cname_records": [],
        "soa_record": "ns1.google.com ..."
    },
    "error": null,
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:30:05",
    "duration_ms": 5000
}
```

### **4.2 WHOIS Lookup**
```
POST http://localhost:8000/api/scans/whois
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "github.com"
}
```
**Expected Output (200):** Domain registration information

### **4.3 IP Information**
```
POST http://localhost:8000/api/scans/ip
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "ip": "8.8.8.8"
}
```
**Expected Output (200):** IP geolocation and information

### **4.4 Port Scanning (Safe Test)**
```
POST http://localhost:8000/api/scans/ports
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "target": "scanme.nmap.org",
    "ports": [80, 443],
    "timeout": 2
}
```
**Expected Output (200):** Port scan results

### **4.5 Subdomain Discovery**
```
POST http://localhost:8000/api/scans/subdomains
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "github.com"
}
```
**Expected Output (200):** Subdomain list

### **4.6 Full Domain Scan**
```
POST http://localhost:8000/api/scans/domain
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "example.com"
}
```
**Expected Output (200):** Comprehensive scan results

### **4.7 Get Scan Result by ID**
```
GET http://localhost:8000/api/scans/{SCAN_ID_FROM_ABOVE}
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):** Same scan result

### **4.8 Get User Scan History**
```
GET http://localhost:8000/api/scans/user/history?limit=5&page=1
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):** List of user's scans

### **4.9 SSRF Protection Test (Negative)**
```
POST http://localhost:8000/api/scans/dns
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "localhost"
}
```
**Expected Output (400):**
```json
{"detail": "Domain scanning not allowed for security reasons"}
```

### **4.10 Rate Limit Test**
**Make 6 DNS requests in 1 minute:**
```
POST http://localhost:8000/api/scans/dns
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "domain": "test1.com"
}
```
**Expected Output (429) on 6th request:**
```json
{"detail": "Rate limit exceeded. Maximum 5 DNS lookups per minute."}
```

---

## 👑 **5. ADMIN ENDPOINTS**

### **5.1 Get All Users**
```
GET http://localhost:8000/api/admin/users
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):** List of all users

### **5.2 Update User Role**
```
PUT http://localhost:8000/api/admin/users/{USER_ID_FROM_TESTUSER}
Authorization: Bearer ACCESS_TOKEN_ADMIN
Content-Type: application/json

{
    "role": "admin",
    "is_active": true
}
```
**Expected Output (200):** Updated user

### **5.3 Get Platform Statistics**
```
GET http://localhost:8000/api/admin/stats
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):** Platform-wide statistics

### **5.4 Search All Activities**
```
GET http://localhost:8000/api/admin/activities
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):** All user activities

### **5.5 Get All Scans**
```
GET http://localhost:8000/api/admin/scans
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):** All platform scans

### **5.6 Delete Any Scan (Admin)**
```
DELETE http://localhost:8000/api/admin/scans/{SCAN_ID}
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):**
```json
{"message": "Scan deleted successfully"}
```

### **5.7 Delete User (Admin)**
```
DELETE http://localhost:8000/api/admin/users/{USER_ID_FROM_TESTUSER}
Authorization: Bearer ACCESS_TOKEN_ADMIN
```
**Expected Output (200):**
```json
{"message": "User deleted successfully"}
```

---

## 🧹 **6. CLEANUP TESTS**

### **6.1 Delete Own Scan**
```
DELETE http://localhost:8000/api/scans/{YOUR_SCAN_ID}
Authorization: Bearer ACCESS_TOKEN_USER
```
**Expected Output (200):**
```json
{"message": "Scan deleted successfully"}
```

### **6.2 Delete Own Account**
```
DELETE http://localhost:8000/api/user/account
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "password": "newpassword456"  # Current password
}
```
**Expected Output (200):**
```json
{"message": "Account deleted successfully"}
```

### **6.3 Logout**
```
POST http://localhost:8000/api/auth/logout
Authorization: Bearer ACCESS_TOKEN_USER
Content-Type: application/json

{
    "refresh_token": "REFRESH_TOKEN_USER"
}
```
**Expected Output (200):**
```json
{"message": "Successfully logged out"}
```

---

## 🚀 **QUICK TESTING SCRIPT**

**test_all.py:**
```python
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
```

---

## 🎯 **TESTING ORDER:**

1. **First:** Health endpoints (no auth needed)
2. **Then:** Auth endpoints (signup, login)
3. **Next:** Scanning endpoints (DNS, WHOIS, IP)
4. **Then:** User management (profile, activities, stats)
5. **Finally:** Cleanup (delete scans, logout)

## ⚠️ **Important Notes:**

1. **Start with fresh server** - Restart to clear database
2. **Save tokens** - You'll need them for subsequent requests
3. **Watch rate limits** - Don't spam scanning endpoints
4. **Test SSRF protection** - Try scanning `localhost`, `127.0.0.1`
5. **Test admin access** - Regular users should get 403

## 🚨 **Expected Issues to Debug:**

1. **Import errors** - Missing packages (install with pip)
2. **Rate limiting** - 429 errors (wait 1 minute)
3. **SSRF blocking** - 400 errors for internal targets (this is GOOD!)
4. **Permission errors** - 403 for wrong roles

Let's start testing! Which endpoint do you want to test first? I recommend starting with the health check to make sure the server is running.