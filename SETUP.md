# Local Development Setup Guide

This guide will help you run the PhishGuard project locally. The project consists of a FastAPI backend and a Next.js frontend.

## Prerequisites

- **Python 3.12+** (Backend)
- **Node.js 18+** (Frontend)
- **PostgreSQL** (Database)
- **uv** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **pnpm** (Node package manager): `npm install -g pnpm`

---

## 1. Database Setup

Ensure you have a PostgreSQL database running locally.

1.  **Create a database named `phishguard`**:
    ```bash
    createdb phishguard
    ```
    *(Or use your preferred database tool like pgAdmin/TablePlus)*

---

## 2. Backend Setup (`dashboard-backend/`)

1.  **Navigate to the backend directory:**
    ```bash
    cd dashboard-backend
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file from the root:
    ```bash
    cp ../example.env .env
    ```

3.  **Update `.env`**:
    Open `.env` and adjust the configuration:
    - **DATABASE_URL**: Update with your local credentials.
      ```properties
      # Example for local usage
      DATABASE_URL=postgresql://your_user:your_password@localhost:5432/phishguard
      ```
    - **DEV_MODE**: Set to `true` to bypass Google Auth requirements for local testing.
      ```properties
      DEV_MODE=true
      ```
    - **AUTH_GOOGLE_ID**: Can be left blank if `DEV_MODE=true`.

4.  **Install Dependencies:**
    ```bash
    uv sync
    ```

5.  **Run the Backend Server:**
    ```bash
    uv run fastapi dev main.py
    ```
    - The server will start at `http://127.0.0.1:8000`.
    - It will automatically create necessary database tables on first run.

---

## 3. Frontend Setup (`dashboard/`)

1.  **Open a new terminal and navigate to the dashboard directory:**
    ```bash
    cd dashboard
    ```

2.  **Configure Environment Variables:**
    Create a `.env.local` file:
    ```bash
    touch .env.local
    ```
    Add the backend URL to it:
    ```properties
    NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
    ```

3.  **Install Dependencies:**
    ```bash
    pnpm install
    ```

4.  **Run the Frontend Development Server:**
    ```bash
    pnpm dev
    ```
    - The dashboard will be available at `http://localhost:3000`.

---

## Troubleshooting

- **Database Connection Failed**: Double-check your `DATABASE_URL` in `dashboard-backend/.env`. Ensure the Postgres service is running.
- **Authentication Errors**: If you see auth errors, ensure `DEV_MODE=true` is set in the backend `.env` and restart the backend server.
- **Port Conflicts**: Ensure ports 8000 (backend) and 3000 (frontend) are free.

---

## Verification

How to verify that everything is working properly:

### 1. Backend Verification
- Open your browser or use `curl` to check the health endpoint:
  - **URL**: `http://127.0.0.1:8000/health`
  - **Expected Output**: `{"status": "ok"}`
- Visit the API Documentation:
  - **URL**: `http://127.0.0.1:8000/docs`
  - **Success Check**: You should see the interactive Swagger UI with a list of endpoints.

### 2. Frontend Verification
- Open your browser and visit `http://localhost:3000`.
- **Success Check**:
  - You should see a "Sign in" page (if not logged in).
  - If `DEV_MODE=true` is set, you might still see "Sign in" because the frontend middleware enforces auth.
  - To fully verify the dashboard, you would need to complete the Google Sign-in flow (requires `DEV_MODE=false` and valid credentials) OR temporarily disable middleware.
