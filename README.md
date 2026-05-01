# Item Catalog

## Server Details (Grader Info)

- **IP Address:** 18.199.172.106
- **SSH Port:** 2200
- **URL:** [http://18.199.172.106.nip.io](http://18.199.172.106.nip.io)
- **SSH Login:** `ssh -i grader_key -p 2200 grader@18.199.172.106`
- **Grader private key:** submitted separately via the Udacity project submission form

---

## Software Installed

- Python 3.12
- Apache 2.4
- mod_wsgi (libapache2-mod-wsgi-py3)
- PostgreSQL 16
- Git
- Python packages: Flask 3.0, SQLAlchemy 2.0, psycopg 3, google-auth, google-auth-oauthlib, requests

---

## Configuration Summary

- SSH port changed from 22 to 2200 (`/etc/ssh/sshd_config`)
- Root login disabled; password authentication disabled — key-based SSH only
- UFW firewall configured: allow 2200/tcp, 80/tcp, 123/udp; deny all else
- Timezone set to UTC
- PostgreSQL user `catalog` and database `catalog` created with limited permissions
- Apache virtual host configured to serve the Flask app via mod_wsgi
- `.git` directory blocked from public access via Apache config

---

## Third-Party Resources

- [Flask documentation](https://flask.palletsprojects.com)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org)
- [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
- [mod_wsgi documentation](https://modwsgi.readthedocs.io)
- [nip.io](https://nip.io) — wildcard DNS for IP-based domains
- [Ubuntu UFW documentation](https://help.ubuntu.com/community/UFW)
- [Amazon Lightsail documentation](https://lightsail.aws.amazon.com/ls/docs)

---

A full-stack web application built with Flask that lets visitors browse a catalog
of sporting-goods items organised by category. Authenticated users — who sign in
via Google OAuth 2.0 — can add new items and edit or delete items they own.

---

## Features

- Browse without an account — anyone can view categories, items, and the JSON API.
- Google Sign-In — no passwords stored; authentication is delegated to Google OAuth 2.0.
- Create items — logged-in users can add items to any existing category.
- Edit / Delete — users can only modify items they created.
- JSON API — the full catalog and individual categories are available as JSON.
- Pre-seeded data — nine categories and twelve sample items loaded by a seed script.

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.11+ |
| Web framework | Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 (Docker) |
| DB driver | psycopg 3 (`psycopg[binary]`) |
| Authentication | Google OAuth 2.0 via `google-auth-oauthlib` |
| Frontend | Jinja2 templates + Bootstrap 5 (CDN) |

---

## Project Structure

```text
python_item_catalog/
│
├── application.py          # Entry point — creates app, registers blueprints
├── database.py             # SQLAlchemy engine and shared db_session
├── models.py               # ORM models: User, Category, Item
├── auth.py                 # auth_bp Blueprint: OAuth routes + login_required
├── views.py                # catalog_bp Blueprint: CRUD routes + JSON API
│
├── lotsofcatalogitems.py   # Seed script — system user, categories, sample items
├── database_setup.py       # Backward-compat shim (imports from database + models)
│
├── docker-compose.yml      # PostgreSQL 16 container definition
├── requirements.txt        # Python dependencies
├── client_secrets.json     # Google OAuth credentials
│
├── templates/
│   ├── base.html           # Shared layout: navbar, flash messages
│   ├── catalog.html        # Homepage — categories + latest items
│   ├── category.html       # Items within a single category
│   ├── item.html           # Individual item detail page
│   ├── newitem.html        # Form to add a new item
│   ├── edititem.html       # Form to edit an existing item
│   ├── deleteitem.html     # Delete confirmation page
│   └── login.html          # Login page with Google Sign-In button
│
└── static/
    └── styles.css          # Custom styles (dark navbar, orange accents)
```

### Key design decisions

- **Flask Blueprints** — `auth.py` defines `auth_bp` and `views.py` defines
  `catalog_bp`. `application.py` registers both. Every import is used explicitly;
  no side-effect imports required.
- **System user** — the seed script creates a `system@catalog.local` user that
  owns all pre-seeded items. Because this email cannot be a real Google account,
  no regular user can log in as the system user and gain edit/delete access to
  the default catalog content.
- **`user_id` is NOT NULL on `Item`** — every item always has an explicit owner;
  there are no nullable foreign keys to reason about.
- **Categories have no owner** — categories are administrator-managed and
  pre-seeded; regular users add items to existing categories only.

---

## Prerequisites

- Python 3.11 or newer
- Docker Desktop running (for PostgreSQL)
- A Google Cloud project with OAuth 2.0 credentials (see Step 4 below)

---

## Setup and Installation

### Step 1 — Navigate to the project directory

```bash
cd python_item_catalog
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Google OAuth credentials

A `client_secrets.json` file is included in the project with credentials
already configured for `http://localhost:8000/gcallback`. No additional
Google Cloud setup is required to run the application.

> **Login access:** The OAuth app must have publishing status set to
> **In production** in Google Auth Platform → Audience so that any Google
> account can sign in. If it is still in Testing mode, only accounts listed
> as test users will be able to log in.

### Step 5 — Start the PostgreSQL database

```bash
docker compose up -d
```

Wait a few seconds for the health check to pass, then verify:

```bash
docker ps
# catalog_db should show status "healthy"
```

### Step 6 — Create the database tables

```bash
python3 models.py
# Database tables created successfully.
```

### Step 7 — Seed the database with sample data (recommended)

```bash
python3 lotsofcatalogitems.py
# System user created (id=1).
# Database seeded successfully.
```

This creates 9 categories and 12 sample items. The script is idempotent —
running it again resets catalog data without affecting user accounts.

> **Note:** The seeded items are read-only — they belong to an internal system
> user so no one can accidentally modify them. To test the full CRUD flow, log
> in, click **Add Item**, and create your own item. Edit and Delete controls
> will appear on any item you own.

### Step 8 — Start the application

```bash
python3 application.py
```

Open your browser and navigate to [http://localhost:8000](http://localhost:8000).

---

## URL Reference

| Method | URL | Description | Auth required |
| --- | --- | --- | --- |
| GET | `/` or `/catalog` | Homepage — categories + latest items | No |
| GET | `/catalog/<category>/items` | All items in a category | No |
| GET | `/catalog/<category>/<item>` | Item detail page | No |
| GET, POST | `/catalog/new` | Add a new item | Yes |
| GET, POST | `/catalog/<id>/edit` | Edit an item (owner only) | Yes |
| GET, POST | `/catalog/<id>/delete` | Delete an item (owner only) | Yes |
| GET | `/catalog.json` | Full catalog as JSON | No |
| GET | `/catalog/<category>/items.json` | Single category as JSON | No |
| GET | `/login` | Login page | No |
| GET | `/gconnect` | Start Google OAuth flow | No |
| GET | `/gcallback` | Google OAuth callback (internal) | No |
| GET | `/logout` | Log out and clear session | No |

---

## JSON API

### Full catalog — `GET /catalog.json`

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Hockey",
      "items": [
        {
          "id": 1,
          "name": "Stick",
          "description": "A hockey stick ...",
          "category": "Hockey"
        }
      ]
    }
  ]
}
```

### Single category — `GET /catalog/Snowboarding/items.json`

```json
{
  "category": "Snowboarding",
  "items": [
    { "id": 2, "name": "Goggles", "description": "...", "category": "Snowboarding" },
    { "id": 3, "name": "Snowboard", "description": "...", "category": "Snowboarding" }
  ]
}
```

---

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://catalog:catalog@localhost:5432/catalog` | Full SQLAlchemy connection string |
| `SECRET_KEY` | `catalog-dev-secret-change-in-prod` | Flask session signing key — change for any deployed instance |
| `OAUTHLIB_INSECURE_TRANSPORT` | `1` (set automatically) | Allows HTTP redirect URIs on localhost. Remove in production (HTTPS required). |

---

## Stopping and Cleaning Up

Stop the Flask server with `Ctrl + C`, then stop the database container:

```bash
# Stop the container but keep the data volume
docker compose down

# Stop the container AND delete all stored data (full reset)
docker compose down -v
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Connection refused` on startup | PostgreSQL container not ready | Wait ~5 s and retry; run `docker ps` to check health |
| `redirect_uri_mismatch` from Google | Redirect URI not registered | Ensure `http://localhost:8000/gcallback` is in Google Cloud Console |
| `FileNotFoundError: client_secrets.json` | Credentials file missing | Re-check Step 4; the file must be in the project root |
| No Edit/Delete links on item page | Logged in as a different user | Log in with the account that created the item |
| Seed script fails with FK violation | Tables not created yet | Run `python models.py` before `python lotsofcatalogitems.py` |
| IDE shows "flask not resolved" | Virtual environment not active | Run `source venv/bin/activate` then `pip install -r requirements.txt` |
