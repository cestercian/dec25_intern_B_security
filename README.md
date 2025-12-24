<h1 align="center">MailShieldAI</h1>

<p align="center">
  <strong>AI-Powered Email Security Platform</strong><br/>
  <em>Detect and neutralize phishing threats in real-time using a multi-agent architecture</em>
</p>

<p align="center">
  <a href="https://mailshield.vercel.app">Live Demo</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#api-reference">API</a> •
  <a href="#deployment">Deployment</a>
</p>

<p align="center">
  <a href="https://mailshield.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-Visit%20Site-00C853?style=for-the-badge" alt="Live Demo" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js%2016-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React%2019-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/LangGraph-FF6B6B?style=flat-square" alt="LangGraph" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Gemini%20AI-8E75B2?style=flat-square&logo=google&logoColor=white" alt="Gemini" />
</p>

<p align="center">
  <a href="https://deepwiki.com/atf-inc/dec25_intern_B_security/1-overview">
    <img src="https://img.shields.io/badge/Documentation-4A90D9?style=flat-square&logo=readthedocs&logoColor=white" alt="DeepWiki Documentation" />
  </a>
</p>


---

<h2 align="center">Overview</h2>

<p align="center">
MailShieldAI is an enterprise-grade email security platform that processes incoming emails<br/>
through a sophisticated pipeline of specialized AI agents. Each email is analyzed for phishing attempts,<br/>
malware, social engineering, and other threats, with automatic Gmail labeling based on risk assessment.
</p>

<h3 align="center">Key Capabilities</h3>

<div align="center">

| Feature | Description |
|---------|-------------|
| **Multi-Agent Pipeline** | 5 specialized workers: Ingest → Intent → Sandbox → Aggregator → Action |
| **LangGraph AI Analysis** | Advanced intent classification with 16 threat categories via Gemini AI |
| **Real-Time Processing** | Gmail Pub/Sub integration for instant email analysis |
| **Automated Labeling** | Auto-applies `MailShield/SAFE`, `CAUTIOUS`, or `MALICIOUS` labels |
| **Risk Scoring** | Intelligent 0-100 scoring with confidence-weighted adjustments |
| **Secure by Design** | OAuth 2.0, CORS validation, PII masking, rate limiting |

</div>

---

<h2 align="center">Architecture</h2>

<h3 align="center">System Overview</h3>

<div align="center">

```
                                    ┌─────────────────────────────────────┐
                                    │           USER INTERFACE            │
                                    │  ┌───────────────────────────────┐  │
                                    │  │   Next.js Dashboard (:3000)   │  │
                                    │  │   • Email monitoring          │  │
                                    │  │   • Threat visualization      │  │
                                    │  │   • Risk analytics            │  │
                                    │  └───────────────┬───────────────┘  │
                                    └─────────────────│─────────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    API LAYER                                            │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI Backend (:8000)                                   │  │
│  │         OAuth • REST Endpoints • Email Ingestion • Statistics                     │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              │                               │                               │
              ▼                               ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│      DATA LAYER         │    │     MESSAGE BROKER      │    │    EXTERNAL SERVICES    │
│  ┌───────────────────┐  │    │  ┌───────────────────┐  │    │  ┌───────────────────┐  │
│  │    PostgreSQL     │  │    │  │   Redis Streams   │  │    │  │    Gmail API      │  │
│  │  • Email records  │  │    │  │  • Control Queue  │  │    │  │  • Pub/Sub events │  │
│  │  • User accounts  │  │    │  │  • Intent Done    │  │    │  │  • Label mgmt     │  │
│  │  • Analysis logs  │  │    │  │  • Analysis Done  │  │    │  │  • Email fetch    │  │
│  └───────────────────┘  │    │  │  • Final Report   │  │    │  └───────────────────┘  │
└─────────────────────────┘    │  └───────────────────┘  │    │  ┌───────────────────┐  │
                               └────────────┬────────────┘    │  │    Gemini AI      │  │
                                            │                 │  │  • Intent analysis│  │
                    ┌───────────────────────┼─────────────────│──│  • URL scanning   │  │
                    │                       │                 │  └───────────────────┘  │
                    ▼                       ▼                 └─────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI WORKER PIPELINE                                        │
│                                                                                         │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌────────┐  │
│    │  INGEST  │ ───▶ │  INTENT  │ ───▶ │ SANDBOX  │ ───▶ │AGGREGATOR│ ───▶ │ ACTION │  │
│    │  :8001   │      │  :8002   │      │  :8004   │      │  :8005   │      │ :8003  │  │
│    └──────────┘      └──────────┘      └──────────┘      └──────────┘      └────────┘  │
│         │                 │                 │                  │                │      │
│    Pub/Sub ───▶    LangGraph ───▶    URL/File ───▶     Combine  ───▶    Gmail   │      │
│    Handler        Classification      Analysis         Results        Labeling  │      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

</div>

<h3 align="center">Processing Flow</h3>

<div align="center">

```
 EMAIL ARRIVES          ANALYSIS PIPELINE              VERDICT                ACTION
      │                       │                          │                      │
      ▼                       ▼                          ▼                      ▼
┌───────────┐  ──▶  ┌───────────────────┐  ──▶  ┌────────────────┐  ──▶  ┌───────────┐
│  Gmail    │       │  Intent + Sandbox │       │  Risk Scoring  │       │  Apply    │
│  Pub/Sub  │       │  AI Analysis      │       │  0-100 Score   │       │  Labels   │
└───────────┘       └───────────────────┘       └────────────────┘       └───────────┘
                                                        │
                          ┌─────────────────────────────┼─────────────────────────────┐
                          │                             │                             │
                          ▼                             ▼                             ▼
                    ┌───────────┐               ┌───────────┐               ┌───────────┐
                    │   SAFE    │               │ CAUTIOUS  │               │  THREAT   │
                    │   0-29    │               │   30-79   │               │  80-100   │
                    └───────────┘               └───────────┘               └───────────┘
```

</div>

<h3 align="center">Worker Pipeline Details</h3>

<div align="center">

| Worker | Port | Technology | Function |
|--------|------|------------|----------|
| **API** | 8000 | FastAPI, SQLModel | REST endpoints, OAuth, orchestration |
| **Dashboard** | 3000 | Next.js 16, React 19 | Real-time monitoring UI |
| **Ingest** | 8001 | FastAPI, httpx | Pub/Sub webhook, email fetching |
| **Intent** | 8002 | LangGraph, Gemini | AI intent classification |
| **Action** | 8003 | Gmail API | Label application, spam handling |
| **Sandbox** | 8004 | LangChain, OpenAI | URL/attachment threat analysis |
| **Aggregator** | 8005 | Redis, asyncpg | Result consolidation |

</div>

---

<h2 align="center">AI-Powered Intent Classification</h2>

<p align="center">
The Intent Worker uses LangGraph with Gemini AI to classify emails into <strong>16 distinct categories</strong>
</p>

<h3 align="center">Threat Categories (High Risk: 75-98)</h3>

<div align="center">

| Intent | Risk Score | Description |
|--------|------------|-------------|
| `MALWARE` | 98 | Malicious attachment/download links |
| `PHISHING` | 95 | Credential harvesting attempts |
| `BEC_FRAUD` | 95 | Business Email Compromise scams |
| `SOCIAL_ENGINEERING` | 90 | Manipulation/impersonation tactics |
| `RECONNAISSANCE` | 75 | Information gathering probes |
| `SPAM` | 60 | Unsolicited bulk messages |

</div>

<h3 align="center">Business Categories (Medium Risk: 30-50)</h3>

<div align="center">

| Intent | Risk Score | Description |
|--------|------------|-------------|
| `PAYMENT` | 45 | Payment requests/confirmations |
| `INVOICE` | 40 | Invoice-related communications |
| `SALES` | 30 | Sales/marketing outreach |

</div>

<h3 align="center">Legitimate Categories (Low Risk: 10-25)</h3>

<div align="center">

| Intent | Risk Score | Description |
|--------|------------|-------------|
| `NEWSLETTER` | 25 | Subscribed newsletters |
| `SUPPORT` | 20 | Customer support threads |
| `MEETING_REQUEST` | 15 | Calendar invitations |
| `TASK_REQUEST` | 15 | Work assignments |
| `PERSONAL` | 10 | Personal correspondence |
| `FOLLOW_UP` | 10 | Thread continuations |

</div>

<h3 align="center">Risk Classification Tiers</h3>

<div align="center">

| Score Range | Tier | Gmail Label | Action |
|-------------|------|-------------|--------|
| 0-29 | **SAFE** | `MailShield/SAFE` | No action needed |
| 30-79 | **CAUTIOUS** | `MailShield/CAUTIOUS` | Manual review suggested |
| 80-100 | **THREAT** | `MailShield/MALICIOUS` | Auto-move to spam (optional) |

</div>

---

<h2 align="center">Quick Start</h2>

<h3 align="center">Prerequisites</h3>

<p align="center">
<strong>Python 3.12+</strong> with <a href="https://github.com/astral-sh/uv">uv</a> package manager<br/>
<strong>Node.js 18+</strong> with <a href="https://pnpm.io/">pnpm</a><br/>
<strong>PostgreSQL 15+</strong> and <strong>Redis 7+</strong><br/>
<strong>Google Cloud</strong> project with Gmail API & OAuth configured
</p>

<h3 align="center">1. Clone & Install</h3>

```bash
# Clone repository
git clone https://github.com/atf-inc/dec25_intern_B_security.git
cd dec25_intern_B_security

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pnpm
npm install -g pnpm

# Install all dependencies
uv sync                    # Python dependencies
npm run install:all        # Node dependencies
```

<h3 align="center">2. Configure Environment</h3>

```bash
cp example.env .env
```

<p align="center">Edit <code>.env</code> with your credentials:</p>

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/mailshieldai

# Redis
REDIS_URL=redis://localhost:6379

# Google OAuth (from Google Cloud Console)
AUTH_GOOGLE_ID=your-client-id.apps.googleusercontent.com
AUTH_GOOGLE_SECRET=your-client-secret

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32

# AI
GEMINI_API_KEY=your-gemini-api-key

# CORS
CORS_ALLOW_ORIGINS=http://localhost:3000
```

<h3 align="center">3. Start Services</h3>

```bash
# Terminal 1: Start PostgreSQL & Redis (via Docker)
docker run --name mailshield-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mailshieldai -p 5432:5432 -d postgres:16
docker run --name mailshield-redis -p 6379:6379 -d redis:7-alpine

# Terminal 2: Initialize database
npm run db:init

# Terminal 3: Start all services
npm run dev:all
```

<h3 align="center">4. Access the Application</h3>

<div align="center">

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

</div>

---

<h2 align="center">API Reference</h2>

<h3 align="center">Authentication</h3>

<div align="center">

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/me` | `GET` | Get current user info |

</div>

<h3 align="center">Email Operations</h3>

<div align="center">

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/emails` | `GET` | List analyzed emails with pagination |
| `/api/emails/ingest` | `POST` | Manual email ingestion trigger |
| `/api/emails/sync/background` | `POST` | Pub/Sub webhook endpoint |

</div>

<h3 align="center">Statistics</h3>

<div align="center">

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | `GET` | Email statistics & threat counts |

</div>

<h3 align="center">System</h3>

<div align="center">

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | `GET` | API health check |
| `/` | `GET` | Worker health (ports 8001-8005) |

</div>

<p align="center">
<strong>Full API documentation</strong>: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>
</p>

---

<h2 align="center">Development</h2>

<h3 align="center">Available Scripts</h3>

```bash
# Development
npm run dev              # API + Dashboard
npm run dev:all          # All 7 services
npm run dev:api          # FastAPI only
npm run dev:web          # Next.js only
npm run dev:intent       # Intent worker only
npm run dev:action       # Action worker only

# Database
npm run db:init          # Initialize/seed database
npm run db:seed          # Re-seed with sample data

# Production
npm run build:web        # Build Next.js
npm run start:all        # Start all services (PM2 compatible)

# Code Quality
npm run lint:web         # ESLint for frontend
```

<h3 align="center">Development Mode</h3>

<p align="center">
Enable <code>DEV_MODE</code> in <code>.env</code> to bypass strict authentication:
</p>

```env
DEV_MODE=true
```

<p align="center">
Use <code>dev_anytoken</code> as the bearer token for API testing.
</p>

---

<h2 align="center">Project Structure</h2>

```
MailShieldAI/
├── apps/
│   ├── api/                       # FastAPI Backend
│   │   ├── main.py               # App entry, CORS config
│   │   ├── routers/              # API route handlers
│   │   │   ├── auth.py           # Google OAuth endpoints
│   │   │   ├── emails.py         # Email CRUD operations
│   │   │   └── stats.py          # Dashboard statistics
│   │   └── services/             # Business logic layer
│   │
│   ├── web/                       # Next.js Dashboard
│   │   ├── app/                  # App Router pages
│   │   ├── components/           # 28 React components
│   │   ├── lib/                  # Utilities & API client
│   │   └── auth.ts               # NextAuth configuration
│   │
│   └── worker/                    # Microservices
│       ├── ingest/               # Pub/Sub message handler
│       ├── intent/               # LangGraph AI classifier
│       │   ├── graph.py          # LangGraph workflow
│       │   ├── taxonomy.py       # 16 intent categories
│       │   └── prompts.py        # Gemini prompts
│       ├── action/               # Gmail labeler
│       │   ├── main.py           # Worker entry
│       │   └── gmail_labels.py   # Label management
│       ├── analyses/             # Sandbox analyzer
│       └── aggregator/           # Result consolidator
│
├── packages/
│   └── shared/                    # Shared Python Modules
│       ├── database.py           # Async PostgreSQL
│       ├── models.py             # SQLModel schemas
│       ├── queue.py              # Redis Streams client
│       ├── types.py              # Pydantic types
│       ├── logger.py             # Structured logging
│       └── constants.py          # Enums & constants
│
├── scripts/
│   └── seed_db.py                # Database seeding
│
├── .github/workflows/
│   └── main.yml                  # CI/CD deployment
│
├── pyproject.toml                # Python dependencies (uv)
├── package.json                  # NPM scripts & Node deps
└── example.env                   # Environment template
```

---

<h2 align="center">Security Features</h2>

<div align="center">

| Feature | Implementation |
|---------|----------------|
| **Multi-Layer Analysis** | Intent + Sandbox + Aggregation pipeline |
| **OAuth 2.0** | Google authentication with token refresh |
| **CORS Protection** | Strict origin validation (no wildcards with credentials) |
| **Rate Limiting** | Gmail API semaphore (5 concurrent requests) |
| **PII Masking** | Email addresses anonymized in logs |
| **Idempotency** | In-memory deduplication for processed messages |
| **Email Auth Checks** | SPF, DKIM, DMARC validation |

</div>

---

<h2 align="center">Environment Variables</h2>

<h3 align="center">Required Variables</h3>

<div align="center">

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `AUTH_GOOGLE_ID` | Google OAuth Client ID |
| `AUTH_GOOGLE_SECRET` | Google OAuth Client Secret |
| `NEXTAUTH_SECRET` | NextAuth.js session secret |
| `GEMINI_API_KEY` | Google Gemini API key |
| `CORS_ALLOW_ORIGINS` | Allowed frontend origins |

</div>

<h3 align="center">Optional Variables</h3>

<div align="center">

| Variable | Default | Description |
|----------|---------|-------------|
| `DEV_MODE` | `false` | Enable development mode |
| `POLL_INTERVAL_SECONDS` | `5` | Worker polling interval |
| `MOVE_MALICIOUS_TO_SPAM` | `true` | Auto-move threats to spam |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API URL for frontend |

</div>

---

<h2 align="center">Deployment</h2>

<h3 align="center">GitHub Actions CI/CD</h3>

<p align="center">
The repository includes automated deployment via GitHub Actions
</p>

```yaml
# .github/workflows/main.yml
# Deploys to VM on push to main branch
# Uses PM2 for process management
```

<p align="center"><strong>Required Secrets:</strong></p>

<div align="center">

| Secret | Description |
|--------|-------------|
| `SSH_PRIVATE_KEY` | Deployment key |
| `SSH_HOST` | Target VM hostname |
| `SSH_USER` | SSH username |

</div>

<h3 align="center">Production Checklist</h3>

<div align="center">

- [x] Set `DEV_MODE=false`
- [x] Configure production `DATABASE_URL` with SSL
- [x] Use Cloud Redis (e.g., Memorystore)
- [x] Set up Google Cloud Pub/Sub for real-time sync
- [x] Configure proper `CORS_ALLOW_ORIGINS`
- [x] Enable Cloud Logging integration

</div>

---

<h2 align="center">Contributing</h2>

<p align="center">
1. Fork the repository<br/>
2. Create a feature branch (<code>git checkout -b feature/amazing-feature</code>)<br/>
3. Commit changes (<code>git commit -m 'Add amazing feature'</code>)<br/>
4. Push to branch (<code>git push origin feature/amazing-feature</code>)<br/>
5. Open a Pull Request
</p>

---

<h2 align="center">Support</h2>

<p align="center">
For questions or support, please <a href="https://github.com/atf-inc/dec25_intern_B_security/issues">open an issue on GitHub</a>.
</p>

---

<h2 align="center">License</h2>

<p align="center">
This project is proprietary. No open-source license is currently applied.
</p>

---

<p align="center">
<strong>Built by the MailShieldAI Team</strong>
</p>

<p align="center">
<a href="https://github.com/atf-inc/dec25_intern_B_security">GitHub</a> •
<a href="https://mailshield.vercel.app">Live Demo</a>
</p>
