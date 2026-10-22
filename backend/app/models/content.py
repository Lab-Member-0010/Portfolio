"""Portfolio content tables.

`SiteSection` stores singleton blocks (hero, about, contact...) as JSON so the
admin can edit copy without migrations. Repeating items get real tables.
"""
from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OrderedMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteSection(Base):
    __tablename__ = "site_sections"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class Fact(OrderedMixin, Base):
    __tablename__ = "facts"

    value: Mapped[str] = mapped_column(String(40))
    suffix: Mapped[str] = mapped_column(String(10), default="")
    label: Mapped[str] = mapped_column(String(120))


class Project(OrderedMixin, Base):
    __tablename__ = "projects"

    code: Mapped[str] = mapped_column(String(20), default="")
    title: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(120), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    impact: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    link: Mapped[str] = mapped_column(String(500), default="")


class TimelineItem(OrderedMixin, Base):
    __tablename__ = "timeline_items"

    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, default="")


class Skill(OrderedMixin, Base):
    __tablename__ = "skills"

    title: Mapped[str] = mapped_column(String(80))
    glyph: Mapped[str] = mapped_column(String(10), default="")
    items: Mapped[str] = mapped_column(Text, default="")


class LifeCard(OrderedMixin, Base):
    __tablename__ = "life_cards"

    # variant drives the decoration: chess | travel | japan | plain
    variant: Mapped[str] = mapped_column(String(20), default="plain")
    label: Mapped[str] = mapped_column(String(120), default="")
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, default="")
    decor: Mapped[str] = mapped_column(String(40), default="")


class Certification(OrderedMixin, Base):
    """A certification or completed training programme, optionally with its certificate PDF."""

    __tablename__ = "certifications"

    kind: Mapped[str] = mapped_column(String(20), default="certification")  # certification | training
    title: Mapped[str] = mapped_column(String(160))
    issuer: Mapped[str] = mapped_column(String(120), default="")
    issued: Mapped[str] = mapped_column(String(60), default="")  # free text: "Oct 2026", "2024 — 2025"
    credential_id: Mapped[str] = mapped_column(String(80), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String(500), default="")
    # storage reference: a path under uploads/ (local) or a Vercel Blob URL
    file_name: Mapped[str] = mapped_column(String(500), default="")


class AppMeta(Base):
    """Tiny key/value table, used to track which content migrations have run."""

    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
