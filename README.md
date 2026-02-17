# Fsociety - Cybersecurity Platform

<div align="center">

![Fsociety Logo](https://img.shields.io/badge/Fsociety-Cybersecurity-00ff9d?style=for-the-badge&logo=security&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-f7df1e?style=for-the-badge&logo=javascript&logoColor=black)

**Enterprise-Grade Cybersecurity Scanning & Analysis Platform**

[Features](#-features) • [Tech Stack](#-technology-stack) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Creators](#-creators)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
  - [Backend Libraries](#backend-libraries)
  - [Frontend Libraries](#frontend-libraries)
- [System Architecture](#-system-architecture)
- [Installation Guide](#-installation-guide)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Documentation](#-documentation)
- [Creators](#-creators)
- [License](#-license)

---

## Overview

**Fsociety** is a comprehensive cybersecurity platform designed for security professionals, penetration testers, and IT administrators. It provides a suite of tools for network scanning, security auditing, phishing detection, digital footprint analysis, and more—all wrapped in a sleek, modern interface.

The platform features:

- **AI-Powered Security Assistant** using local LLM integration (Ollama)
- **Real-time Network Scanning** with port detection and OS fingerprinting
- **Security Audits** including SSL/TLS analysis and header checks
- **VPN Configuration Generator** with real PKI certificates
- **Phishing Detection Engine** for URL and email analysis
- **Digital Footprint Scanner** for OSINT reconnaissance
- **Admin Dashboard** with user management and SQL console

---

## Features

| Feature                     | Description                                                |
| --------------------------- | ---------------------------------------------------------- |
| **AI Security Chat**  | Local AI assistant powered by Ollama for security guidance |
| **Network Scanner**   | Port scanning, service detection, OS fingerprinting        |
| **Security Audit**    | SSL/TLS analysis, security headers, vulnerability checks   |
| **Phishing Detector** | AI-powered URL and email phishing analysis                 |
| **Digital Footprint** | OSINT reconnaissance and data exposure detection           |
| **VPN Generator**     | OpenVPN configuration with PKI certificate generation      |
| **File Analysis**     | Malware detection and file hash verification               |
| **Admin Panel**       | User management, activity logs, SQL console, PDF exports   |
| **Secure Auth**       | JWT tokens, bcrypt hashing, OTP recovery, rate limiting    |

---

## 🛠 Technology Stack

### Backend Libraries

| Library                 | Purpose                              |
| ----------------------- | ------------------------------------ |
| **FastAPI**       | High-performance async API framework |
| **SQLAlchemy**    | ORM for database operations          |
| **SQLite**        | Lightweight relational database      |
| **Pydantic**      | Data validation and serialization    |
| **python-jose**   | JWT token generation and validation  |
| **bcrypt**        | Password hashing (Blowfish cipher)   |
| **python-dotenv** | Environment variable management      |
| **httpx**         | Async HTTP client for external APIs  |
| **psutil**        | System monitoring and health checks  |
| **slowapi**       | Rate limiting middleware             |
| **cryptography**  | PKI certificate generation for VPN   |
| **dnspython**     | DNS resolution for security scans    |
| **whois**         | Domain WHOIS lookups                 |
| **python-nmap**   | Network scanner integration          |
| **yara-python**   | Malware signature detection          |
| **python-magic**  | File type detection                  |

### Frontend Libraries

| Library                               | Purpose                           |
| ------------------------------------- | --------------------------------- |
| **Vanilla JavaScript (ES6+)**   | Core application logic            |
| **CSS3 with Custom Properties** | Modern styling with theming       |
| **jsPDF**                       | PDF generation for reports        |
| **jsPDF-AutoTable**             | Table rendering in PDFs           |
| **Marked.js**                   | Markdown parsing for AI responses |
| **Material Symbols**            | Icon library                      |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Port 5500)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │   Views     │ │  Router     │ │    API      │ │   Utils    │ │
│  │ (dashboard, │ │ (hash-based)│ │ (axios-like)│ │ (helpers)  │ │
│  │  admin...)  │ │             │ │             │ │            │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Port 8000)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │   Routers   │ │  Services   │ │ Repositories│ │   Utils    │ │
│  │ (endpoints) │ │ (business)  │ │   (data)    │ │  (tools)   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    ▼                   ▼                        │
│              ┌──────────┐       ┌──────────┐                    │
│              │ SQLite   │       │  Ollama  │                    │
│              │ Database │       │   LLM    │                    │
│              └──────────┘       └──────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation Guide

### Prerequisites

- **Python 3.11+**
- **Node.js** (optional, for development tools)
- **Ollama** (optional, for AI chat feature)
- **Nmap** (optional, for advanced network scanning)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/koffandaff/Aegis.git
   cd Aegis
   ```
2. **Create and activate virtual environment**

   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**

   ```bash
   # Create .env file in backend folder
   cd backend
   cp .env.example .env
   # Edit .env with your secret keys
   ```
5. **Start the backend server**

   ```bash
   cd backend
   fastapi dev
   # Server runs on http://localhost:8000
   ```

### Frontend Setup

1. **Navigate to frontend folder**

   ```bash
   cd frontend
   ```
2. **Start the development server**

   ```bash
   python -m http.server 5500
   # Frontend runs on http://localhost:5500
   ```
3. **Open in browser**

   ```
   http://localhost:5500
   ```

---

## Usage

### Default Credentials

| Role  | Email                    | Password          |
| ----- | ------------------------ | ----------------- |
| Admin | `admin@fsociety.com`   | `Admin123!`     |
| Admin | `dhruvil@fsociety.com` | `Fsociety2026!` |
| User  | `mrrobot@fsociety.com` | `Elliot123!`    |

### Quick Start Workflow

1. **Login** with provided credentials or create a new account
2. **Dashboard** - View security overview and recent activity
3. **Network Scan** - Enter target IP/domain for port scanning
4. **Security Audit** - Analyze SSL certificates and headers
5. **AI Chat** - Get security recommendations from the AI assistant
6. **Admin Panel** - (Admin only) Manage users and view logs

---

## API Endpoints

All endpoints are prefixed with `/api`. Protected endpoints require a valid JWT token.

### Authentication (`/api/auth`)

| Method | Endpoint             | Description                                 | Auth |
| ------ | -------------------- | ------------------------------------------- | ---- |
| POST   | `/signup`          | Register new user                           | ❌   |
| POST   | `/login`           | Login and get tokens                        | ❌   |
| POST   | `/logout`          | Logout and invalidate refresh token         | ✅   |
| POST   | `/refresh`         | Refresh access token (uses HttpOnly cookie) | ❌   |
| GET    | `/me`              | Get current user info                       | ✅   |
| POST   | `/forgot-password` | Request OTP for password reset              | ❌   |
| POST   | `/verify-otp`      | Verify OTP code                             | ❌   |
| POST   | `/reset-password`  | Reset password with OTP                     | ❌   |

---

### User (`/api/user`)

| Method | Endpoint        | Description              | Auth |
| ------ | --------------- | ------------------------ | ---- |
| GET    | `/profile`    | Get current user profile | ✅   |
| PUT    | `/profile`    | Update user profile      | ✅   |
| PUT    | `/password`   | Change user password     | ✅   |
| DELETE | `/account`    | Delete user account      | ✅   |
| GET    | `/activities` | Get user activity logs   | ✅   |
| GET    | `/stats`      | Get user statistics      | ✅   |

---

### Admin (`/api/admin`)

| Method | Endpoint             | Description                        | Auth     |
| ------ | -------------------- | ---------------------------------- | -------- |
| GET    | `/users`           | Get all users (with search/filter) | 🔒 Admin |
| PUT    | `/users/{user_id}` | Update any user                    | 🔒 Admin |
| DELETE | `/users/{user_id}` | Delete any user                    | 🔒 Admin |
| GET    | `/stats`           | Get platform statistics            | 🔒 Admin |
| GET    | `/activities`      | Search activities across all users | 🔒 Admin |
| POST   | `/sql`             | Execute SQL query (SQL Console)    | 🔒 Admin |

---

### Network Scans (`/api/scans`)

| Method | Endpoint             | Description                  | Auth     |
| ------ | -------------------- | ---------------------------- | -------- |
| POST   | `/domain`          | Comprehensive domain scan    | ✅       |
| POST   | `/whois`           | WHOIS lookup                 | ✅       |
| POST   | `/dns`             | DNS records lookup           | ✅       |
| POST   | `/subdomains`      | Subdomain discovery          | ✅       |
| POST   | `/ip`              | IP information lookup        | ✅       |
| POST   | `/ports`           | Port scanning                | ✅       |
| GET    | `/{scan_id}`       | Get scan result by ID        | ✅       |
| GET    | `/history`         | Get user's scan history      | ✅       |
| DELETE | `/{scan_id}`       | Delete a scan                | ✅       |
| GET    | `/all`             | Get all scans (admin only)   | 🔒 Admin |
| DELETE | `/admin/{scan_id}` | Delete any scan (admin only) | 🔒 Admin |

---

### Security Audit (`/api/security`)

| Method | Endpoint           | Description                          | Auth     |
| ------ | ------------------ | ------------------------------------ | -------- |
| POST   | `/ssl`           | SSL/TLS certificate scan             | ✅       |
| POST   | `/headers`       | HTTP headers analysis                | ✅       |
| POST   | `/phishing`      | Check URL for phishing               | ✅       |
| POST   | `/tech-stack`    | Detect technology stack              | ✅       |
| POST   | `/http-security` | Comprehensive HTTP security analysis | ✅       |
| GET    | `/cache/stats`   | Get cache statistics                 | 🔒 Admin |
| POST   | `/cache/clear`   | Clear cache                          | 🔒 Admin |
| GET    | `/cache/entries` | Inspect cache entries                | 🔒 Admin |
| GET    | `/health`        | Detailed system health               | ❌       |
| GET    | `/rate-limits`   | Get current rate limits              | ✅       |

---

### AI Chat (`/api/chat`)

| Method | Endpoint                         | Description                    | Auth |
| ------ | -------------------------------- | ------------------------------ | ---- |
| GET    | `/sessions`                    | Get all chat sessions          | ✅   |
| POST   | `/sessions`                    | Create new chat session        | ✅   |
| GET    | `/sessions/{session_id}`       | Get session with messages      | ✅   |
| DELETE | `/sessions/{session_id}`       | Delete chat session            | ✅   |
| PUT    | `/sessions/{session_id}/title` | Update session title           | ✅   |
| POST   | `/send`                        | Send message (SSE streaming)   | ✅   |
| GET    | `/health`                      | Check Ollama connection status | ❌   |

---

### VPN (`/api/vpn`)

| Method | Endpoint          | Description               | Auth     |
| ------ | ----------------- | ------------------------- | -------- |
| GET    | `/servers`      | Get available VPN servers | ✅       |
| POST   | `/openvpn`      | Generate OpenVPN config   | ✅       |
| POST   | `/wireguard`    | Generate WireGuard config | ✅       |
| GET    | `/configs`      | List user's VPN configs   | ✅       |
| GET    | `/server-setup` | Get server PKI files      | 🔒 Admin |

---

### 📁 File Analysis (`/api/files`)

| Method | Endpoint                     | Description                   | Auth     |
| ------ | ---------------------------- | ----------------------------- | -------- |
| POST   | `/hash/check`              | Check hash against malware DB | ✅       |
| POST   | `/hash/batch`              | Batch hash checking           | ✅       |
| POST   | `/upload/analyze`          | Upload and analyze file       | ✅       |
| POST   | `/virustotal/check`        | Check hash on VirusTotal      | ✅       |
| GET    | `/malware/database`        | Get malware DB info           | 🔒 Admin |
| POST   | `/malware/database/update` | Update malware database       | 🔒 Admin |
| GET    | `/supported/hash-types`    | Get supported hash types      | ❌       |
| GET    | `/supported/file-types`    | Get supported file types      | ❌       |

---

### Digital Footprint (`/api/footprint`)

| Method | Endpoint            | Description              | Auth |
| ------ | ------------------- | ------------------------ | ---- |
| POST   | `/scan`           | Start footprint scan     | ✅   |
| GET    | `/scan/{scan_id}` | Get scan status/results  | ✅   |
| GET    | `/history`        | Get scan history         | ✅   |
| DELETE | `/scan/{scan_id}` | Delete scan from history | ✅   |
| GET    | `/platforms`      | Get supported platforms  | ❌   |

---

### Health & Utility

| Method | Endpoint    | Description           | Auth |
| ------ | ----------- | --------------------- | ---- |
| GET    | `/health` | Basic health check    | ❌   |
| GET    | `/docs`   | Swagger documentation | ❌   |
| GET    | `/redoc`  | ReDoc documentation   | ❌   |

---

> **Legend**: ✅ = Requires authentication | 🔒 Admin = Admin role required | ❌ = Public
>
> **Full API Documentation**: Visit `/docs` or `/redoc` when the backend is running.

---

## Documentation

Detailed documentation is available in the `docs/` folder:

```
docs/
├── backend/
│   ├── Auth/           # Authentication system
│   ├── Database/       # Database schema and ORM
│   ├── Caching_RateLimiting/  # Caching and rate limiting
│   └── [Feature]/      # Each feature module
├── frontend/
│   ├── Auth/           # Frontend authentication
│   ├── Routing/        # Hash-based routing
│   └── Components/     # UI components
└── viva_prep/
    ├── backend_questions.md    # 100+ backend interview questions
    └── frontend_questions.md   # 100+ frontend interview questions
```

---

## Creators

<div align="center">

| `<img src="https://via.placeholder.com/100" width="100" style="border-radius: 50%">` | `<img src="https://via.placeholder.com/100" width="100" style="border-radius: 50%">` | `<img src="https://via.placeholder.com/100" width="100" style="border-radius: 50%">` |
| :------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------: |
|                                **Dhruvil Adroja**                                |                                  **Vraj Patel**                                  |                                 **Krisha Patel**                                 |
|                               Lead Full Stack Developer                               |                                  Full Stack Developer                                  |                                  Full Stack Developer                                  |
|                             Linux & Recon Engine Architect                             |                                 UI/UX & Visualizations                                 |                                  Backend Infrastructure                                |

</div>

---

## 📄 License

This project is developed for educational purposes as part of academic coursework.

---

<div align="center">

**Built with ❤️ by the Fsociety Team**

[⬆ Back to Top](#-fsociety---cybersecurity-platform)

</div>
