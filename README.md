<div align="center">

<img src="docs/banner.svg" alt="Jayesh Sharma — Full Stack Engineer" width="100%" />

<h3>A bold, editorial developer portfolio — with its own admin portal.</h3>

<p>
  <img alt="React" src="https://img.shields.io/badge/React-19-0b0c0c?style=for-the-badge&logo=react&logoColor=c8ff2e" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-strict-0b0c0c?style=for-the-badge&logo=typescript&logoColor=c8ff2e" />
  <img alt="Vite" src="https://img.shields.io/badge/Vite-8-0b0c0c?style=for-the-badge&logo=vite&logoColor=c8ff2e" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-async-0b0c0c?style=for-the-badge&logo=fastapi&logoColor=c8ff2e" />
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-0b0c0c?style=for-the-badge&logo=sqlalchemy&logoColor=c8ff2e" />
  <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-0b0c0c?style=for-the-badge&logo=jsonwebtokens&logoColor=c8ff2e" />
</p>

<p>
  <a href="#-quickstart"><b>Quickstart</b></a> ·
  <a href="#-whats-inside"><b>Features</b></a> ·
  <a href="#-a-look-around"><b>Screenshots</b></a> ·
  <a href="#-how-it-works"><b>Architecture</b></a> ·
  <a href="#-the-admin-portal"><b>Admin</b></a> ·
  <a href="#-api-reference"><b>API</b></a> ·
  <a href="#-deploying"><b>Deploy</b></a>
</p>

</div>

---

## ✦ What's inside

<table>
<tr>
<td width="50%" valign="top">

### 🖥️ The portfolio
- Oversized editorial typography, outlined name, rotating stamp, scrolling marquee
- **Live network canvas** that reacts to your cursor
- Expandable project rows, count-up stats, scroll-progress bar, reveal-on-scroll
- Credentials with **viewable certificate PDFs**
- Working **contact form** (honeypot + rate limit)
- Fully responsive, respects `prefers-reduced-motion`

</td>
<td width="50%" valign="top">

### 🔐 The admin portal — `/admin`
- JWT login, password change
- Edit **every word** on the site, no redeploy
- Create · edit · hide · delete · **reorder** projects, facts, timeline, skills, certifications, life cards
- Upload résumé and certificate PDFs
- Inbox for contact-form messages
- Lazy-loaded — zero cost to public visitors

</td>
</tr>
</table>

---

## 📸 A look around

<table>
<tr>
<td width="60%"><img src="docs/screenshots/hero.jpg" alt="Hero" /></td>
<td width="40%" rowspan="2" align="center"><img src="docs/screenshots/mobile.jpg" alt="Mobile" width="260" /><br/><sub><b>Mobile</b></sub></td>
</tr>
<tr>
<td><img src="docs/screenshots/projects.jpg" alt="Projects" /></td>
</tr>
</table>

<details>
<summary><b>🔎 More of the public site</b> — credentials, beyond the screen</summary>
<br/>

| Credentials | Beyond the screen |
| :---: | :---: |
| <img src="docs/screenshots/credentials.jpg" alt="Credentials" /> | <img src="docs/screenshots/beyond.jpg" alt="Beyond the screen" /> |

</details>

<details>
<summary><b>🛠️ Peek inside the admin portal</b> — login, dashboard, lists, editor</summary>
<br/>

| Login | Dashboard |
| :---: | :---: |
| <img src="docs/screenshots/admin-login.jpg" alt="Admin login" /> | <img src="docs/screenshots/admin-dashboard.jpg" alt="Admin dashboard" /> |
| **Collections** | **Editor** |
| <img src="docs/screenshots/admin-projects.jpg" alt="Admin projects list" /> | <img src="docs/screenshots/admin-edit.jpg" alt="Admin edit modal" /> |

</details>

---

## ⚡ Quickstart

> **You need:** Python 3.10+ and Node 20+.

**1 · Start the API**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ← change JWT_SECRET and ADMIN_PASSWORD
uvicorn app.main:app --reload --port 8000
```

**2 · Start the site** (new terminal)

```bash
cd frontend
npm install
npm run dev
```

**3 · Open it**

| | URL |
| --- | --- |
| 🌐 Portfolio | http://localhost:5173 |
| 🔐 Admin | http://localhost:5173/admin — `admin@example.com` / `ChangeMe123!` (from `.env`) |
| 📚 API docs (Swagger) | http://localhost:8000/docs |

<details>
<summary><b>🪟 On Windows?</b></summary>

```powershell
cd backend
py -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

</details>

<details>
<summary><b>🤔 What happens on first start?</b></summary>

1. `portfolio.db` (SQLite) is created next to the backend.
2. All content is **seeded from the résumé** — projects, experience, skills, certifications, life cards.
3. An admin user is created from `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
4. Upgrading an older database? Restart and `services/migrations.py` applies content fixes — **only to values you haven't edited** in the admin.

</details>

---

## 🧭 How it works

```mermaid
flowchart LR
    V([👤 Visitor]) -->|"/"| R
    A([🔐 You]) -->|"/admin"| R
    subgraph FE["frontend · React + Vite"]
        R[React Router] --> P[Portfolio page]
        R -.lazy.-> AD[Admin app]
    end
    P -->|GET /api/portfolio| API
    P -->|POST /api/messages| API
    AD -->|Bearer JWT| API
    subgraph BE["backend · FastAPI"]
        API[Routers] --> S[Services]
        S --> DB[(SQLite / Postgres)]
        S --> F[/uploads · PDFs/]
    end
```

<details>
<summary><b>🔁 What happens when you hit “Save” in the admin?</b></summary>

```mermaid
sequenceDiagram
    autonumber
    actor You
    participant Admin as Admin UI
    participant API as FastAPI
    participant DB as Database
    actor Visitor
    You->>Admin: Edit project → Save
    Admin->>API: PUT /api/admin/projects/3 (Bearer token)
    API->>API: Verify JWT · validate with Pydantic
    API->>DB: UPDATE projects
    API-->>Admin: 200 + updated project
    Admin-->>You: ✅ toast “Project saved”
    Visitor->>API: GET /api/portfolio
    API->>DB: published items, ordered
    API-->>Visitor: fresh content — no redeploy
```

</details>

<details>
<summary><b>🗃️ Content model</b></summary>

```mermaid
erDiagram
    SITE_SECTIONS {
        string key PK "hero, about, contact..."
        json data "editable copy"
    }
    PROJECTS {
        int id PK
        string title
        string category
        text summary
        json tags
    }
    FACTS {
        int id PK
        string value
        string suffix
        string label
    }
    TIMELINE_ITEMS {
        int id PK
        string title
        text body
    }
    SKILLS {
        int id PK
        string title
        string glyph
        text items
    }
    CERTIFICATIONS {
        int id PK
        string kind "certification or training"
        string title
        string issuer
        string credential_id
        string file_name
    }
    LIFE_CARDS {
        int id PK
        string variant "chess, travel, japan, plain"
        string title
    }
    MESSAGES {
        int id PK
        string name
        string email
        text body
        bool is_read
    }
    ADMIN_USERS {
        int id PK
        string email
        string password_hash
    }
```

Every list table also has `sort_order` and `is_published`.

</details>

<details>
<summary><b>📁 Project structure</b></summary>

```text
Portfolio/
├── backend/                          FastAPI
│   ├── app/
│   │   ├── main.py                   app, CORS, routers, serves frontend/dist in prod
│   │   ├── core/                     settings (.env) · bcrypt + JWT
│   │   ├── db/session.py             engine · session · Base
│   │   ├── models/                   SQLAlchemy tables
│   │   ├── schemas/                  Pydantic request/response models
│   │   ├── services/                 defaults · seed · migrations · file helpers
│   │   └── api/routes/               public · auth · admin_content · admin_misc
│   ├── tests/test_api.py             pytest, end-to-end through the API
│   ├── uploads/                      résumé + certificate PDFs
│   └── requirements.txt
├── frontend/                         React + Vite + TypeScript
│   └── src/
│       ├── api/                      typed fetch client + types
│       ├── components/portfolio/     Hero · Projects · Experience · Arsenal · Credentials · Contact …
│       ├── components/admin/         generic field renderer + field configs
│       ├── pages/                    PortfolioPage · admin/*
│       ├── context/ hooks/ lib/      auth · toasts · in-view · scroll progress · *rich text*
│       └── styles/                   portfolio.css · admin.css
├── docs/                             banner + screenshots for this README
└── index.html                        original static design (reference)
```

</details>

---

## 🔐 The admin portal

| Page | What you can do |
| --- | --- |
| **Dashboard** | Counts at a glance — projects, certifications, unread messages, résumé status |
| **Page copy** | Hero, section headings, manifesto, experience header, contact text, marquee, social links, SEO |
| **Projects · Quick facts · Experience · Skills · Certifications · Beyond code** | Add, edit, delete, hide/publish, reorder with ↑ ↓ |
| **Certifications** | Plus *Upload PDF* per item → visitors get a “View certificate” button |
| **Messages** | Contact-form inbox — read/unread, reply by email, delete |
| **Résumé** | Drag-and-drop the PDF behind every “Download résumé” button |
| **Account** | Change your password |

> [!TIP]
> In any title or statement, wrap words in `*asterisks*` to get the signature lime/serif highlight.
> `Wide enough to ship. *Deep enough to own.*` → Wide enough to ship. ***Deep enough to own.***

---

## 📡 API reference

**50 endpoints.** Nothing runs on a timer — every call is triggered by a visitor or by you in the admin.
Full interactive docs live at **`/docs`** once the backend is running.

<details>
<summary><b>🌍 Public — 5 endpoints</b> (no login)</summary>

| Method | Endpoint | Triggered when… |
| --- | --- | --- |
| `GET` | `/api/portfolio` | anyone opens the homepage — all published content in one payload |
| `GET` | `/api/resume` | a visitor clicks **Download résumé** |
| `GET` | `/api/certifications/{id}/file` | a visitor clicks **View certificate** |
| `POST` | `/api/messages` | a visitor submits the contact form (5 per 10 min per IP + honeypot) |
| `GET` | `/api/health` | uptime checks / load balancers |

</details>

<details>
<summary><b>🔑 Auth — 3 endpoints</b></summary>

| Method | Endpoint | Triggered when… |
| --- | --- | --- |
| `POST` | `/api/auth/login` | you sign in at `/admin/login` |
| `GET` | `/api/auth/me` | any admin page loads (validates the saved token) |
| `POST` | `/api/auth/change-password` | you submit the Account page |

</details>

<details>
<summary><b>🛠️ Admin — 42 endpoints</b> (Bearer token)</summary>

**Page copy**

| Method | Endpoint | Triggered when… |
| --- | --- | --- |
| `GET` | `/api/admin/sections` | Page copy screen opens |
| `GET` | `/api/admin/sections/{key}` | reading a single block |
| `PUT` | `/api/admin/sections/{key}` | **Save** on a block |

**Collections** — the same 5 endpoints for each of `projects`, `facts`, `timeline`, `skills`, `life-cards`, `certifications` (= 30)

| Method | Endpoint | Triggered when… |
| --- | --- | --- |
| `GET` | `/api/admin/{collection}` | the list page opens |
| `POST` | `/api/admin/{collection}` | **+ Add** → Save |
| `PUT` | `/api/admin/{collection}/{id}` | **Edit** → Save, or the Published/Hidden toggle |
| `DELETE` | `/api/admin/{collection}/{id}` | **Delete** → Confirm |
| `POST` | `/api/admin/{collection}/reorder` | the ↑ / ↓ arrows |

**Files, messages, stats**

| Method | Endpoint | Triggered when… |
| --- | --- | --- |
| `POST` | `/api/admin/certifications/{id}/file` | **Upload / Replace PDF** on a certification |
| `DELETE` | `/api/admin/certifications/{id}/file` | **✕ PDF** |
| `GET` | `/api/admin/messages` | inbox opens |
| `PATCH` | `/api/admin/messages/{id}` | a message is opened, or Mark read/unread |
| `DELETE` | `/api/admin/messages/{id}` | Delete on a message |
| `GET` | `/api/admin/resume` | Résumé page opens |
| `POST` | `/api/admin/resume` | a PDF is dropped/chosen |
| `DELETE` | `/api/admin/resume` | Delete → Confirm |
| `GET` | `/api/admin/stats` | Dashboard opens |

</details>

---

## ⚙️ Configuration

<details open>
<summary><b><code>backend/.env</code></b></summary>

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./portfolio.db` | Any SQLAlchemy URL — e.g. `postgresql+psycopg://user:pass@host/db` |
| `JWT_SECRET` | `change-me…` | **Change this.** Signs admin tokens |
| `JWT_EXPIRE_MINUTES` | `720` | Admin session length |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `admin@example.com` / `ChangeMe123!` | First admin user (created once) |
| `CORS_ORIGINS` | `http://localhost:5173,…` | Comma-separated allowed origins |
| `UPLOAD_DIR` | `./uploads` | Where PDFs are stored |
| `FRONTEND_DIST` | `../frontend/dist` | Built React app to serve in production |

</details>

<details>
<summary><b><code>frontend/.env</code></b></summary>

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | *(empty)* | Leave empty for same-origin `/api`; set when the API is on another domain |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Where the dev server proxies `/api` |

</details>

---

## 🚀 Deploying

**One server, one process** — FastAPI serves the API *and* the built site (with SPA fallback for `/admin/*`):

```bash
cd frontend && npm ci && npm run build      # → frontend/dist
cd ../backend && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

<details>
<summary><b>🌐 nginx + HTTPS in front</b></summary>

```nginx
server {
    server_name jayesh.dev;                     # your domain
    client_max_body_size 12m;                   # PDF uploads

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
# then: sudo certbot --nginx -d jayesh.dev
```

</details>

<details>
<summary><b>🐘 Switching to PostgreSQL</b></summary>

```bash
pip install "psycopg[binary]"
# backend/.env
DATABASE_URL=postgresql+psycopg://portfolio:secret@localhost:5432/portfolio
```

Tables are created and seeded automatically on the next start.

</details>

<details>
<summary><b>✅ Pre-launch checklist</b></summary>

- [ ] Set a long random `JWT_SECRET`
- [ ] Change `ADMIN_EMAIL` / `ADMIN_PASSWORD` (or change the password in Admin → Account)
- [ ] Set `CORS_ORIGINS` to your real domain
- [ ] Upload the latest résumé and certificate PDFs
- [ ] Fill in email / LinkedIn / GitHub under Admin → Page copy → Site
- [ ] Put HTTPS in front (nginx + certbot)
- [ ] Back up `portfolio.db` and `backend/uploads/`

</details>

---

## 🧪 Testing

```bash
cd backend && source .venv/bin/activate
pytest -q        # auth, CRUD, publish/hide, reorder, messages, uploads, migrations
```

```bash
cd frontend
npx tsc -b && npm run build     # type-check + production build
```

---

## 🛡️ Security notes

- Passwords hashed with **bcrypt**; admin routes require a signed **JWT**
- Every request body validated by **Pydantic**; unknown section keys are dropped
- Uploads must be real PDFs (magic-byte check) and are size-limited
- Contact form: hidden **honeypot** field + **per-IP rate limit**
- `.env`, databases and uploaded files are git-ignored

---

<div align="center">

**Designed for curiosity · Engineered for impact**

<sub>Built with React, FastAPI and a lot of lime. © 2026 Jayesh Sharma</sub>

</div>
