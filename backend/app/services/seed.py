"""Initial content taken from the résumé and the original index.html design."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import AdminUser, Certification, Fact, LifeCard, Project, Skill, TimelineItem

FACTS = [
    {"value": "5", "label": "Major AI products"},
    {"value": "8", "label": "Developers co-led"},
    {"value": "1", "suffix": "+", "label": "Years in production"},
    {"value": "3", "label": "Certifications earned"},
]

PROJECTS = [
    {
        "code": "P/01", "title": "Talenteq", "category": "AI Hiring Platform",
        "summary": "An AI-powered talent marketplace that scores candidates against live roles, manages vendor networks, and runs secure screening rounds.",
        "impact": "Owned far beyond the frontend: database operations, VPS security, containerization, CI/CD, and AI matching.",
        "tags": ["React", "Redux", "Node.js", "MongoDB", "OpenAI", "GitHub Actions"],
    },
    {
        "code": "P/02", "title": "Proctoring Engine", "category": "Secure AI Microservice",
        "summary": "A standalone test generation and proctoring platform that captures encrypted evidence, detects suspicious visual and audio signals, and plugs into other products through APIs.",
        "impact": "Built from scratch, independently—from role-based access to YOLO detection and encrypted S3 evidence.",
        "tags": ["React", "FastAPI", "YOLO", "WebRTC VAD", "Docker", "AWS S3"],
    },
    {
        "code": "P/03", "title": "ReconcileAI", "category": "Fintech / ML",
        "summary": "A multi-tenant financial reconciliation system that maps clinic bookings to payment charges in seconds, sending only ambiguous matches for human review.",
        "impact": "Owned the backend, async data model, auth, ML integration, and production AWS deployment end-to-end.",
        "tags": ["React 19", "FastAPI", "PostgreSQL", "LightGBM", "AWS RDS", "SQLAlchemy"],
    },
    {
        "code": "P/04", "title": "WardenIQ", "category": "Open Source / RAG",
        "summary": "A self-hosted test-intelligence platform that turns requirements into reusable test suites, then maps every code change back to impacted coverage.",
        "impact": "Designed to run fully on-prem with swappable LLMs, hybrid retrieval, versioning, and deep repository analysis.",
        "tags": ["FastAPI", "MongoDB", "RAG", "Ollama", "GitHub API", "Docker Compose"],
    },
    {
        "code": "P/05", "title": "ArchitonX", "category": "Construction SaaS",
        "summary": "An AI-native construction operating system spanning drawings, BIM, contracts, materials, site operations, payments, reporting, and tenant-safe access.",
        "impact": "Led the move toward fine-grained ReBAC while shipping React, Express, PostgreSQL, billing, observability, and Gemini workflows.",
        "tags": ["React", "TypeScript", "Express", "Drizzle", "Gemini", "Clerk", "Stripe"],
    },
]

TIMELINE = [
    {"title": "Owned complete systems", "body": "Independently developed end-to-end services, prototypes, and products—across interface, backend, database, cloud, and delivery."},
    {"title": "Led under pressure", "body": "Co-led a team of eight developers with the backend head and delivered products ahead of aggressive timelines."},
    {"title": "Made infrastructure boring", "body": "Managed VPS security, cloud services, automated deployments, databases, and CI/CD so the team could keep shipping."},
    {"title": "Applied AI where it mattered", "body": "Built onboarding, ATS, proctoring, test automation, RAG, matching, reconciliation, and document-intelligence workflows."},
    {"title": "Learnt in public, delivered in production", "body": "Repeatedly accepted unfamiliar problems, learned the stack on the fly, and turned uncertainty into working software."},
]

SKILLS = [
    {"title": "Frontend", "glyph": "UI", "items": "React · TypeScript · Zustand · Redux · TanStack Query · Tailwind CSS · Vite"},
    {"title": "Backend", "glyph": "API", "items": "Node.js · Express · FastAPI · Python · REST APIs · async architectures"},
    {"title": "Data", "glyph": "DB", "items": "PostgreSQL · MongoDB · MySQL · pgvector · Drizzle · SQLAlchemy"},
    {"title": "AI Systems", "glyph": "AI", "items": "OpenAI · Ollama · Gemini · RAG · embeddings · ML microservices · computer vision"},
    {"title": "Cloud & DevOps", "glyph": "☁", "items": "AWS · VPS · Docker · GitHub Actions · nginx · CI/CD · infrastructure security"},
    {"title": "Integration", "glyph": "↗", "items": "Auth · billing · observability · third-party APIs · Creatio low-code platform · cross-platform services"},
]

LIFE_CARDS = [
    {"variant": "chess", "label": "Officially rated chess player", "title": "Strategy over spectacle.",
     "body": "I like positions that reward patience, pattern recognition, and thinking a few moves past the obvious.", "decor": "♞"},
    {"variant": "travel", "label": "Traveller / observer", "title": "New coordinates, new context.",
     "body": "Travelling keeps my perspective elastic.", "decor": "22°N"},
    {"variant": "japan", "label": "Learning Japanese", "title": "Always a beginner somewhere.",
     "body": "Because the fastest way to stay sharp is to keep choosing things that make you humble.", "decor": "学ぶ"},
]


CERTIFICATIONS = [
    {
        "kind": "certification", "title": "Creatio Software Developer — Advanced", "issuer": "Creatio",
        "issued": "Oct 2026", "credential_id": "00058468",
        "summary": "Advanced-level developer certification for building and customising applications on the Creatio low-code platform.",
        "file_name": "creatio-developer-advanced.pdf",
    },
    {
        "kind": "certification", "title": "AWS Certified Cloud Practitioner", "issuer": "Amazon Web Services",
        "issued": "", "credential_id": "CLF-C02",
        "summary": "Foundational certification covering AWS cloud concepts, core services, security, architecture, and billing.",
    },
    {
        "kind": "training", "title": "MERN Stack Development — 1-Year Training", "issuer": "InfoBeans Foundation",
        "issued": "", "credential_id": "",
        "summary": "A full year of hands-on training in MongoDB, Express.js, React, and Node.js — the foundation everything else was built on.",
    },
]


def _seed_table(db: Session, model, rows: list[dict]) -> None:
    if db.scalar(select(model.id).limit(1)) is not None:
        return
    for i, row in enumerate(rows):
        db.add(model(sort_order=i, **row))


def seed(db: Session) -> None:
    s = get_settings()
    if db.scalar(select(AdminUser.id).limit(1)) is None:
        db.add(AdminUser(email=s.admin_email.lower(), password_hash=hash_password(s.admin_password)))
    _seed_table(db, Fact, FACTS)
    _seed_table(db, Project, PROJECTS)
    _seed_table(db, TimelineItem, TIMELINE)
    _seed_table(db, Skill, SKILLS)
    _seed_table(db, LifeCard, LIFE_CARDS)
    _seed_table(db, Certification, CERTIFICATIONS)
    db.commit()
