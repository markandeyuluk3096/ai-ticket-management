# AI Ticket Management System

Django REST Framework backend for a customer support ticket system.

## Backend setup (Windows PowerShell)

1. Open a terminal in `backend`.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set your private database password and Django secret key. Never commit `.env`.
5. Create the MySQL database and ensure the configured database user has privileges on it.
6. Apply migrations and create an administrator:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## API endpoints

- `POST /api/accounts/register/` — customer registration
- `POST /api/accounts/login/` — obtain JWT access and refresh tokens
- `POST /api/token/refresh/` — refresh an access token
- `POST /api/accounts/logout/` — blacklist a refresh token
- `GET/PATCH /api/accounts/profile/` — current user's profile
- `GET /api/categories/` — active categories (authenticated)
- `GET/POST /api/tickets/` — list the caller's tickets or create a ticket
- `GET /api/tickets/<id>/` — retrieve an accessible ticket
- `GET/PATCH /api/tickets/<id>/` — staff update status, priority, and assignment
- `GET/POST /api/tickets/<id>/messages/` — ticket conversation

Ticket conversations accept optional attachments up to 5 MB with `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, and `.docx` extensions. Configure private object storage and malware scanning before production deployment.

Create categories in Django Admin before customers submit tickets. Category codes must be unique, short identifiers such as `TECH` or `BILL`.

Ticket numbers are generated under a database transaction and category row lock, in the format `CODE-YEAR-0001`. For databases that do not support effective row-level locking, verify concurrency behavior before production use.

## Security notes

- JWT authentication is required for API endpoints except registration and login.
- Customer ticket lists are scoped to the authenticated customer; agents see assigned tickets; admins see all tickets.
- Do not commit `.env`, credentials, tokens, or uploaded customer data.
- Configure HTTPS, production `DEBUG=False`, `ALLOWED_HOSTS`, secure cookies, upload storage/scanning, and rate limits before deployment.
