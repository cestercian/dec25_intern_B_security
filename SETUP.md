# Local Development Setup Guide

This guide will help you run MailShieldAI locally. The project consists of a FastAPI backend, a Next.js frontend, and a background worker.

## Prerequisites

- **Python 3.12+** (Backend & Worker)
- **Node.js 18+** (Frontend)
- **PostgreSQL** (Database - GCP Cloud SQL recommended for production)
- **uv** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **pnpm** (Node package manager): `npm install -g pnpm`

---

## 1. Database Setup

MailShieldAI requires PostgreSQL. For local development, you can use:

### Option A: Local PostgreSQL
```bash
# macOS with Homebrew
brew install postgresql@15
brew services start postgresql@15
createdb mailshieldai
```

### Option B: Docker
```bash
docker run -d --name mailshieldai-db \
  -e POSTGRES_PASSWORD=localdev \
  -e POSTGRES_DB=mailshieldai \
  -p 5432:5432 \
  postgres:15
```

### Option C: GCP Cloud SQL
Use Cloud SQL Proxy to connect to your GCP instance locally.

---

## 2. Backend Setup (`dashboard-backend/`)

1.  **Navigate to the backend directory:**
    ```bash
    cd dashboard-backend
    ```

2.  **Configure Environment Variables:**
    ```bash
    cp ../example.env .env
    ```

3.  **Update `.env`**:
    ```properties
    # PostgreSQL connection (REQUIRED)
    DATABASE_URL=postgresql://postgres:localdev@localhost:5432/mailshieldai
    
    # Google OAuth (get from Google Cloud Console)
    AUTH_GOOGLE_ID=your-google-client-id.apps.googleusercontent.com
    AUTH_GOOGLE_SECRET=your-google-client-secret
    
    # CORS (must match frontend URL)
    CORS_ALLOW_ORIGINS=http://localhost:3000
    
    # Dev mode - set to true for testing without Google OAuth
    DEV_MODE=true
    ```

4.  **Install Dependencies:**
    ```bash
    uv sync
    ```

5.  **Initialize the Database:**
    ```bash
    uv run python seed_db.py
    ```
    This creates the database tables and a dev user for testing.

6.  **Run the Backend Server:**
    ```bash
    uv run fastapi dev main.py
    ```
    The server will start at `http://127.0.0.1:8000`.

---

## 3. Frontend Setup (`dashboard/`)

1.  **Navigate to the dashboard directory:**
    ```bash
    cd dashboard
    ```

2.  **Configure Environment Variables:**
    Create a `.env.local` file:
    ```properties
    NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
    
    # Google OAuth (same as backend)
    AUTH_GOOGLE_ID=your-google-client-id.apps.googleusercontent.com
    AUTH_GOOGLE_SECRET=your-google-client-secret
    
    # NextAuth.js
    NEXTAUTH_URL=http://localhost:3000
    NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32
    ```

3.  **Install Dependencies:**
    ```bash
    pnpm install
    ```

4.  **Run the Frontend:**
    ```bash
    pnpm dev
    ```
    The dashboard will be available at `http://localhost:3000`.

---

## 4. Worker Setup (`agent-backend/`) - Optional

The background worker processes pending emails and assigns risk scores.

1.  **Navigate to the agent directory:**
    ```bash
    cd agent-backend
    ```

2.  **Configure Environment:**
    ```bash
    cp ../example.env .env
    # Ensure DATABASE_URL matches the backend
    ```

3.  **Install Dependencies:**
    ```bash
    uv sync
    ```

4.  **Run the Worker:**
    ```bash
    uv run python -m worker
    ```

---

## Dev Mode Testing

When `DEV_MODE=true` is set in the backend:

1. The backend accepts `dev_anytoken` as a valid bearer token
2. A dev user is automatically created by `seed_db.py`
3. You can test API endpoints without Google OAuth

**Testing with curl:**
```bash
# Get stats
curl -H "Authorization: Bearer dev_anytoken" http://127.0.0.1:8000/api/stats

# List emails
curl -H "Authorization: Bearer dev_anytoken" http://127.0.0.1:8000/api/emails
```

---

## Google OAuth Setup

For production or to test the full login flow:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://your-domain.com/api/auth/callback/google` (production)
4. Enable the Gmail API if you want to sync emails
5. Copy the Client ID and Secret to your `.env` files

---

## Troubleshooting

- **Database Connection Failed**: Check your `DATABASE_URL`. PostgreSQL must be running.
- **CORS Errors**: Ensure `CORS_ALLOW_ORIGINS` matches your frontend URL exactly.
- **Auth Errors**: In dev mode, use `dev_anytoken`. In production, ensure Google OAuth is configured.
- **Port Conflicts**: Ensure ports 8000 (backend) and 3000 (frontend) are free.

---

## Verification

### Backend Verification
```bash
# Health check
curl http://127.0.0.1:8000/health
# Expected: {"status": "ok"}

# API Documentation
open http://127.0.0.1:8000/docs
```

### Frontend Verification
- Open `http://localhost:3000`
- You should see a sign-in page
- Sign in with Google (production) or the frontend will use the dev token (if configured)
