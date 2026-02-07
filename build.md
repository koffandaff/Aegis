# Fsociety Deployment Guide

## Frontend (Vercel - Static HTML/CSS/JS)

### Prerequisites
```bash
npm install -g vercel
```

### Deploy
```bash
cd e:\Fsociety\frontend

# Update config.js with production API URL first
# Edit js/config.js:
# API_URL: 'https://your-backend.onrender.com/api'

vercel --prod
```

### Vercel Settings
- **Framework**: Other (static)
- **Build Command**: (leave empty)
- **Output Directory**: `.` (root)

---

## Backend (Render / Railway)

### Local Build Test
```bash
cd e:\Fsociety\backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Environment Variables (Set in Dashboard)
```env
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
SECRET_KEY=your-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=2
REFRESH_TOKEN_EXPIRE_DAYS=7
OLLAMA_URL=https://your-ollama-ngrok-url
COOKIE_SECURE=true
VPN_SERVER_SECRET=your-vpn-secret
```

### Render Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Python Version**: 3.11+

### Railway Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## CORS Configuration

Update `app.py` with your Vercel domain:
```python
origins = [
    "https://your-app.vercel.app",
    "https://your-custom-domain.com",
]
```

---

## Quick Deploy Checklist

### Before Deploy
- [ ] Update `frontend/js/config.js` with backend URL
- [ ] Set `COOKIE_SECURE=true` in backend env
- [ ] Update CORS origins in `app.py`
- [ ] Set secure `SECRET_KEY` (not default)

### After Deploy
- [ ] Test login/logout flow
- [ ] Verify token refresh works
- [ ] Check VPN config generation
- [ ] Test admin panel access
