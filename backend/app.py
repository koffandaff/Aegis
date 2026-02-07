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
    allow_origins=[
        "https://reconauto.vercel.app",
        "https://reconauto-backend.vercel.app",
        "https://fsociety-web-service.vercel.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_origin_regex=r"https://reconauto-.*\.vercel\.app",  # Support Vercel previews
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Startup Event to Initialize Database and Seed Data
# Default Credentials:
# Admin: admin@fsociety.com / Admin123!
# Admin: dhruvil@fsociety.com / Fsociety2026!
# User:  mrrobot@fsociety.com / Elliot123!
@app.on_event("startup")
async def startup_event():
    from database.engine import init_db, get_db_context
    from database.seed import seed_database
    
    # Initialize database (create tables)
    init_db()
    
    # Seed with initial data
    with get_db_context() as db:
        seed_database(db)
    
    print("[STARTUP] Database initialized and seeded")

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
    except Exception:
        system_stats = {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'error': 'System stats unavailable'
        }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are present even on 500 errors"""
    from fastapi.responses import JSONResponse
    import traceback
    
    error_detail = str(exc)
    print(f"[CRITICAL ERROR] {error_detail}\n{traceback.format_exc()}")
    
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": error_detail}
    )
    
    # Manually add CORS headers since middleware might be skipped on exception
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
    return response
    
    # Check Ollama availability
    ai_available = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            response = await client.get(f"{ollama_url}/api/tags")
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
            'database': f"{os.getenv('DATABASE_URL', 'sqlite').split('://')[0].upper()} (active)"
        }
    }