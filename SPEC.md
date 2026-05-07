# OmniAnalyse - AI Functional Test Agent

## Project Overview
- **Project Name**: omnianalyse
- **Type**: Full Stack Web Application (Angular + Python FastAPI)
- **Core Functionality**: AI-powered functional test scenario generator
- **Target Users**: QA engineers, developers, testers

## Tech Stack
- **Frontend**: Angular 19 (standalone components)
- **Backend**: Python FastAPI
- **Running Ports**:
  - Frontend: 4200
  - Backend: 8001

## Architecture

```
omnianalyse/
├── SPEC.md
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── core/
│   │   │   ├── config.py   # Settings
│   │   │   └── security.py # JWT auth
│   │   ├── models/
│   │   │   └── schemas.py  # Pydantic models
│   │   └── routers/
│   │       ├── auth.py      # Login/logout
│   │       ├── users.py    # User endpoints
│   │       └── scenarios.py # Test scenarios
│   └── requirements.txt
└── frontend/
    └── omnianalyse-frontend/
        └── src/
            └── app/
                ├── app.ts          # Root component
                ├── app.routes.ts # Routing config
                └── components/
                    ├── login/        # Login page
                    └── dashboard/   # Dashboard page
```

## Features

### Backend
- JWT Authentication
- Login endpoint (/auth/login)
- Test scenario CRUD (/scenarios)

### Frontend
- Login form with validation
- Dashboard with features display
- Token-based authentication
- Responsive design

## Default Credentials
- Username: admin
- Password: admin123

## Acceptance Criteria
1. Backend runs on port 8001 ✓
2. Frontend runs on port 4200 ✓
3. API responds to health check ✓
4. Basic authentication works ✓
5. Frontend loads without errors ✓