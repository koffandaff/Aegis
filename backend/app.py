from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import Auth_Router, User_Router, Admin_Router  
from routers import Auth_Router, User_Router, Admin_Router, Scan_Router

# Load Env Variables
load_dotenv()

app = FastAPI(title='Fsociety API', version='1.0.0')

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(Auth_Router.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(User_Router.router, prefix='/api/user', tags=['User Management'])
app.include_router(Admin_Router.router, prefix='/api/admin', tags=['Admin']) 
app.include_router(Scan_Router.router, prefix='/api/scans', tags=['Scanning']) 

@app.get('/')
async def root():
    return {'message': 'Fsociety API is running!'}

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'auth-service'}