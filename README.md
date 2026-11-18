# AI Ticket Management System

A customer-support platform built with **Django REST Framework, React, Tailwind CSS v4, and MySQL**. It provides customer ticket management, staff ticket handling, FAQ search, AI support chat, ticket triage, notifications, and administrator reporting.

## Current features

- Customer registration, username/password login, Google sign-in, profile and JWT refresh/logout
- Role-based access for customers, support agents, and administrators
- Category-based ticket numbers (for example, `TECH-2026-0001`)
- Customer ticket creation, ticket history, and ticket conversations
- Agent ticket queue, status and priority updates, SLA tracking
- Ticket attachments with extension, size, and content validation
- Published FAQ search and an OpenAI-powered FAQ assistant
- OpenAI ticket triage suggestions for support staff
- Automatic ticket notifications and customer feedback
- Administrator ticket and feedback reports

## Requirements

- Python 3.12+
- Node.js 24+
- MySQL 8+
- A Google OAuth 2.0 Web client ID (optional until Google sign-in is enabled)
- An OpenAI API key (optional; AI endpoints return a clear configuration error when absent)

## Backend setup (Windows PowerShell)

From the repository root:

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your own values:

- `DJANGO_SECRET_KEY`: a long random secret
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: your MySQL database connection
- `OPENAI_API_KEY`: your OpenAI API key to enable AI chat and ticket analysis
- `GOOGLE_CLIENT_ID`: the OAuth 2.0 Web client ID used by the frontend

Create the MySQL database and grant the configured user access. Then run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend API: `http://127.0.0.1:8000/api/`

## Frontend setup (second terminal)

From the repository root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/
VITE_GOOGLE_CLIENT_ID=your-google-oauth-web-client-id
```

The Google client ID must match `GOOGLE_CLIENT_ID` in `backend/.env`. In Google Cloud Console, create an OAuth 2.0 Client ID of type **Web application** and add these Authorized JavaScript origins for local development:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

Restart Vite after changing frontend environment variables.

Frontend: `http://localhost:5173/`

## Initial administrator setup

1. Sign in to Django Admin at `http://127.0.0.1:8000/admin/` using the superuser.
2. Create ticket categories and assign each a unique short code (such as `TECH`, `BILL`, or `GEN`).
3. Add published FAQ entries.
4. Create support-agent accounts and set their application role to `agent`.
5. Assign tickets to agents from the admin interface when needed.

Customers can register from the React application. Google sign-in creates a customer account on first verified sign-in; existing accounts with the same verified email are linked to that Google identity.

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/accounts/register/` | Customer registration |
| POST | `/api/accounts/login/` | Username/password JWT login |
| POST | `/api/accounts/google/` | Verify Google credential and issue JWT |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/accounts/logout/` | Blacklist refresh token |
| GET/PATCH | `/api/accounts/profile/` | Current user profile |
| GET | `/api/categories/` | Active ticket categories |
| GET/POST | `/api/tickets/` | Role-scoped ticket list / customer ticket creation |
| GET/PATCH | `/api/tickets/<id>/` | Ticket details / staff updates |
| GET/POST | `/api/tickets/<id>/messages/` | Ticket conversation |
| GET | `/api/faqs/?search=<term>` | Published FAQ search |
| POST | `/api/ai/chat/` | AI FAQ assistant |
| POST | `/api/ai/tickets/<id>/analyze/` | AI ticket triage |
| GET | `/api/notifications/` | Current user's notifications |
| POST | `/api/feedback/tickets/<id>/` | Customer feedback after resolution |
| GET | `/api/reports/dashboard/` | Administrator reports |

## Checks

```powershell
# Backend (from backend, with venv activated)
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test

# Frontend (from frontend)
npm run build
```

GitHub Actions runs the backend checks against MySQL and builds the frontend. It also verifies that representative Tailwind utility classes are present in the generated production CSS.

## Security and production notes

- Never commit `.env`, API keys, passwords, tokens, or customer uploads.
- JWT authentication and role-scoped querysets protect API resources.
- Google ID tokens are verified server-side against the configured client ID and must contain a verified email.
- Configure HTTPS, production `DEBUG=False`, secure allowed hosts/origins, email delivery, private object storage, malware scanning, backups, and monitoring before production use.
- The current local media configuration is for development. Do not expose customer attachments from a public media directory in production.
