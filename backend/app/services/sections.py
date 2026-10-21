"""Default copy for every singleton section. Also defines which keys are editable."""
from copy import deepcopy
from typing import Any

from sqlalchemy.orm import Session

from app.models import SiteSection

# Text wrapped in *asterisks* is rendered as the highlighted/italic accent on the site.
DEFAULT_SECTIONS: dict[str, dict[str, Any]] = {
    "site": {
        "nav_mark": "JS / 2026",
        "nav_cta": "Start a conversation ↗",
        "meta_title": "Jayesh Sharma — Full Stack Engineer",
        "meta_description": "Jayesh Sharma — Full Stack Engineer building ambitious AI-native products.",
        "email": "",
        "linkedin": "",
        "github": "",
        "marquee": ["React", "TypeScript", "FastAPI", "Node.js", "AI Systems", "AWS", "PostgreSQL", "Docker", "Creatio", "Learn fast. Ship faster."],
        "footer_left": "Jayesh Sharma © 2026",
        "footer_right": "Designed for curiosity · Engineered for impact",
    },
    "hero": {
        "eyebrow": "Available for ambitious builds",
        "available": True,
        "coordinates": "22.7196° N / 75.8577° E\nINDORE — INDIA",
        "first_name": "Jayesh",
        "last_name": "Sharma",
        "accent_letter": "m",
        "stamp_kanji": "構築",
        "stamp_text": "BUILD / LEARN\nREPEAT",
        "statement": "Full-stack engineer building *AI-native systems* from first sketch to production.",
        "primary_cta": "Explore selected work ↓",
        "resume_cta": "Download résumé",
    },
    "about": {
        "index": "01 / OPERATING SYSTEM",
        "title": "I turn unknowns into *working software.*",
        "manifesto": "Put me where product, infrastructure, and AI collide. I learn what I need, own the outcome, and keep moving until the system is *real, useful, and shipped.*",
    },
    "work": {
        "index": "02 / SELECTED SYSTEMS",
        "title": "Not case studies. *Proof of work.*",
    },
    "experience": {
        "index": "03 / FIELD EXPERIENCE",
        "title": "Built inside the *beautiful chaos* of a startup.",
        "period": "May 2025 — Present",
        "company": "AdlerQA Technologies",
        "role": "Full Stack Engineer · Indore, India",
        "years": "1.5",
        "years_caption": "Years of accelerated growth",
    },
    "arsenal": {
        "index": "04 / TECHNICAL ARSENAL",
        "title": "Wide enough to ship. *Deep enough to own.*",
    },
    "credentials": {
        "index": "05 / CREDENTIALS",
        "title": "Certified. Trained. *Still learning.*",
    },
    "offscreen": {
        "index": "06 / BEYOND THE SCREEN",
        "title": "The person behind *the pull requests.*",
    },
    "contact": {
        "index": "07 / NEXT MOVE",
        "tagline": "Open to bold products & difficult problems",
        "title": "Have a hard problem? *Good.*",
        "body": "Bring the messy brief, the ambitious timeline, or the product nobody has figured out yet.",
        "form_enabled": True,
    },
}

SECTION_KEYS = tuple(DEFAULT_SECTIONS.keys())


def get_section(db: Session, key: str) -> dict[str, Any]:
    row = db.get(SiteSection, key)
    merged = deepcopy(DEFAULT_SECTIONS.get(key, {}))
    if row and row.data:
        merged.update(row.data)
    return merged


def get_all_sections(db: Session) -> dict[str, dict[str, Any]]:
    return {key: get_section(db, key) for key in SECTION_KEYS}


def save_section(db: Session, key: str, data: dict[str, Any]) -> dict[str, Any]:
    allowed = DEFAULT_SECTIONS[key]
    clean: dict[str, Any] = {}
    for field, default in allowed.items():
        if field not in data:
            continue
        value = data[field]
        if isinstance(default, bool):
            clean[field] = bool(value)
        elif isinstance(default, list):
            if isinstance(value, str):
                value = value.split("\n")
            clean[field] = [str(v).strip() for v in value if str(v).strip()]
        else:
            clean[field] = "" if value is None else str(value)
    row = db.get(SiteSection, key)
    if row is None:
        row = SiteSection(key=key, data={})
        db.add(row)
    row.data = {**(row.data or {}), **clean}
    db.commit()
    return get_section(db, key)
