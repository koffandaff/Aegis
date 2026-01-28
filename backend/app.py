from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import (
    Auth_Router, User_Router, Admin_Router, 
    Scan_Router, Security_Router, File_Router,
    VPN_Router, Chat_Router, Footprint_Router
)
from datetime import datetime, timezone
import sys
import platform
import os

# Load Env Variables
load_dotenv()

app = FastAPI(
    title='Fsociety Cybersecurity Platform API',
    version='2.0.0',
    description='Advanced cybersecurity scanning and analysis platform',
    docs_url='/docs',
    redoc_url='/redoc'
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    url = str(request.url)
    method = request.method
    
    print(f"\n[>>>] {method} {url}")
    
    # Simple interaction tracking
    if "/api/auth" in url:
        print(f"[AUTH] Interaction detected on {url}")
    elif "/api/scans" in url:
        print(f"[SCAN] Scanner activity on {url}")

    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        print(f"[<<<] {response.status_code} ({process_time:.3f}s)")
        return response
    except Exception as e:
        print(f"[ERR] {method} {url} - Error: {str(e)}")
        raise e

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Startup Event to Create Admin and Seed Data
@app.on_event("startup")
async def startup_event():
    from model.Auth_Model import db
    from service.Auth_Service import AuthService
    import random
    from datetime import timedelta
    
    auth_service = AuthService(db)
    
    # Create default admin
    admin_email = "admin@fsociety.com"
    if not db.get_userby_email(admin_email):
        print(f"Creating default admin user: {admin_email}")
        try:
            admin_data = {
                "email": admin_email,
                "username": "admin",
                "password": "Admin123!",
                "role": "admin",
                "full_name": "System Administrator",
                "bio": "Root access authorized."
            }
            auth_service.register_user(admin_data)
        except Exception as e:
            print(f"Failed to create default admin: {e}")
    
    # Seed demo users for admin dashboard
    demo_users = [
        {"email": "alice@example.com", "username": "alice_sec", "password": "Demo123!", "full_name": "Alice Security", "company": "CyberCorp"},
        {"email": "bob@example.com", "username": "bob_hack", "password": "Demo123!", "full_name": "Bob Hacker", "company": "SecureNet"},
        {"email": "charlie@example.com", "username": "charlie_dev", "password": "Demo123!", "full_name": "Charlie Dev", "company": "TechStart"},
        {"email": "diana@example.com", "username": "diana_ops", "password": "Demo123!", "full_name": "Diana Ops", "company": "CloudSafe"},
        {"email": "eve@example.com", "username": "eve_analyst", "password": "Demo123!", "full_name": "Eve Analyst", "company": "DataGuard"},
    ]
    
    for user_data in demo_users:
        if not db.get_userby_email(user_data["email"]):
            try:
                user_data["role"] = "user"
                auth_service.register_user(user_data)
                print(f"Created demo user: {user_data['email']}")
            except Exception as e:
                print(f"Failed to create {user_data['email']}: {e}")
    
    # Seed demo activities and stats
    actions = ["scan", "chat", "security_audit", "phishing_check", "vpn_generate", "login"]
    
    for user_id, user in db.users.items():
        # Add random stats
        db.update_user_stats(user_id, {
            'total_scans': random.randint(5, 50),
            'phishing_checks': random.randint(2, 20),
            'vpn_configs': random.randint(0, 5),
            'reports_generated': random.randint(1, 10),
            'last_active': datetime.utcnow().isoformat()
        })
        
        # Add random activities
        for _ in range(random.randint(3, 10)):
            action = random.choice(actions)
            activity_time = datetime.utcnow() - timedelta(
                hours=random.randint(0, 72),
                minutes=random.randint(0, 59)
            )
            
            activity_id = str(random.randint(10000, 99999))
            activity = {
                'id': activity_id,
                'user_id': user_id,
                'action': action,
                'details': {'target': f'example-{random.randint(1,100)}.com'},
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'timestamp': activity_time.isoformat()
            }
            
            if user_id not in db.user_activities:
                db.user_activities[user_id] = []
            db.user_activities[user_id].append(activity)
    
    print(f"[SEED] Loaded {len(db.users)} users with activities and stats")

# Include routers
app.include_router(Auth_Router.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(User_Router.router, prefix='/api/user', tags=['User Management'])
app.include_router(Admin_Router.router, prefix='/api/admin', tags=['Admin'])
app.include_router(Scan_Router.router, prefix='/api/scans', tags=['Scanning'])
app.include_router(Security_Router.router, prefix='/api/security', tags=['Security Scanning'])
app.include_router(File_Router.router, prefix='/api/files', tags=['File Analysis'])
app.include_router(VPN_Router.router, prefix='/api/vpn', tags=['VPN Tools'])
app.include_router(Chat_Router.router, prefix='/api/chat', tags=['AI Chatbot'])
app.include_router(Footprint_Router.router, prefix='/api/footprint', tags=['Digital Footprint'])

# Health and root endpoints
@app.get('/')
async def root():
    """Root endpoint with API information"""
    return {
        'message': 'Fsociety Cybersecurity Platform API',
        'version': '2.0.0',
        'status': 'operational',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'endpoints': {
            'auth': '/api/auth',
            'user': '/api/user',
            'admin': '/api/admin',
            'scans': '/api/scans',
            'security': '/api/security',
            'files': '/api/files',
            'vpn': '/api/vpn',
            'docs': '/docs',
            'redoc': '/redoc'
        }
    }

@app.get('/health')
async def health_check():
    """Basic health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'fsociety-api',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

@app.get('/status')
async def status_check():
    """Detailed status check"""
    try:
        import psutil
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        system_stats = {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%",
            'uptime': str(uptime).split('.')[0]
        }
    except ImportError:
        system_stats = {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'error': 'psutil not installed'
        }
    
    # Check Ollama availability
    ai_available = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            ai_available = response.status_code == 200
    except:
        ai_available = False

    return {
        'status': 'operational',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'system': system_stats,
        'ai_available': ai_available,
        'services': {
            'authentication': 'active',
            'scanning': 'active',
            'security_scanning': 'active',
            'file_analysis': 'active',
            'ai_chat': 'active' if ai_available else 'unavailable',
            'database': 'in-memory (active)'
        }
    }