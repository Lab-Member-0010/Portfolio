"""One-off content migrations for databases created by an earlier version.

Seeding only fills empty tables, so corrections to seeded copy must be applied here.
Each step only touches values that still equal the old defaults, so anything edited
in the admin is left alone. Applied steps are recorded in `app_meta`.
"""
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AppMeta, Certification, Fact, SiteSection, Skill

VERSION_KEY = "content_version"


def _replace_in_section(db: Session, key: str, old_to_new: dict[str, tuple[object, object]]) -> None:
    row = db.get(SiteSection, key)
    if not row or not row.data:
        return  # untouched sections fall back to the (already corrected) defaults
    data = dict(row.data)
    for field, (old, new) in old_to_new.items():
        if data.get(field) == old:
            data[field] = new
    row.data = data


def _v2_experience_and_credentials(db: Session) -> None:
    """Start date May 2025, credentials section, Creatio certification."""
    for fact in db.scalars(select(Fact)).all():
        if fact.value == "2" and fact.suffix == "+" and fact.label == "Years in the arena":
            fact.value, fact.suffix, fact.label = "1", "+", "Years in production"
        elif fact.value == "AWS" and fact.label == "Cloud Practitioner":
            fact.value, fact.suffix, fact.label = "3", "", "Certifications earned"

    _replace_in_section(db, "experience", {
        "period": ("May 2024 — Present", "May 2025 — Present"),
        "years": ("02", "1.5"),
    })
    _replace_in_section(db, "offscreen", {"index": ("05 / BEYOND THE SCREEN", "06 / BEYOND THE SCREEN")})
    _replace_in_section(db, "contact", {"index": ("06 / NEXT MOVE", "07 / NEXT MOVE")})

    old_marquee = ["React", "TypeScript", "FastAPI", "Node.js", "AI Systems", "AWS", "PostgreSQL", "Docker", "Learn fast. Ship faster."]
    site = db.get(SiteSection, "site")
    if site and site.data and site.data.get("marquee") == old_marquee:
        site.data = {**site.data, "marquee": old_marquee[:-1] + ["Creatio", old_marquee[-1]]}

    old_items = "Auth · billing · observability · third-party APIs · cross-platform services"
    for skill in db.scalars(select(Skill).where(Skill.items == old_items)).all():
        skill.items = "Auth · billing · observability · third-party APIs · Creatio low-code platform · cross-platform services"


def _v3_storage_refs(db: Session) -> None:
    """Certificate files are now referenced by their path under uploads/ (or a Blob URL)."""
    for cert in db.scalars(select(Certification).where(Certification.file_name != "")).all():
        name = cert.file_name
        if "/" not in name and not name.startswith("http"):
            cert.file_name = f"certificates/{name}"


MIGRATIONS: list[tuple[int, Callable[[Session], None]]] = [
    (2, _v2_experience_and_credentials),
    (3, _v3_storage_refs),
]
LATEST = max(v for v, _ in MIGRATIONS)


def run_migrations(db: Session, fresh_install: bool) -> None:
    meta = db.get(AppMeta, VERSION_KEY)
    if meta is None:
        meta = AppMeta(key=VERSION_KEY, value=str(LATEST if fresh_install else 1))
        db.add(meta)
        db.commit()
    current = int(meta.value or 1)
    for version, step in MIGRATIONS:
        if version > current:
            step(db)
            meta.value = str(version)
            db.commit()
