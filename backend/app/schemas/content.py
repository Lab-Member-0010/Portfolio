from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class _Base(BaseModel):
    sort_order: int = 0
    is_published: bool = True


class _Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sort_order: int
    is_published: bool


# ---- Facts ---------------------------------------------------------------
class FactIn(_Base):
    value: str = Field(min_length=1, max_length=40)
    suffix: str = Field(default="", max_length=10)
    label: str = Field(min_length=1, max_length=120)


class FactOut(_Read, FactIn):
    pass


# ---- Projects ------------------------------------------------------------
class ProjectIn(_Base):
    code: str = Field(default="", max_length=20)
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(default="", max_length=120)
    summary: str = ""
    impact: str = ""
    tags: list[str] = []
    link: str = Field(default="", max_length=500)

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.split(",")
        return [str(t).strip() for t in (v or []) if str(t).strip()]


class ProjectOut(_Read, ProjectIn):
    pass


# ---- Timeline ------------------------------------------------------------
class TimelineIn(_Base):
    title: str = Field(min_length=1, max_length=160)
    body: str = ""


class TimelineOut(_Read, TimelineIn):
    pass


# ---- Skills --------------------------------------------------------------
class SkillIn(_Base):
    title: str = Field(min_length=1, max_length=80)
    glyph: str = Field(default="", max_length=10)
    items: str = ""


class SkillOut(_Read, SkillIn):
    pass


# ---- Life cards ----------------------------------------------------------
class LifeCardIn(_Base):
    variant: str = Field(default="plain", pattern="^(chess|travel|japan|plain)$")
    label: str = Field(default="", max_length=120)
    title: str = Field(min_length=1, max_length=160)
    body: str = ""
    decor: str = Field(default="", max_length=40)


class LifeCardOut(_Read, LifeCardIn):
    pass


# ---- Certifications & training ------------------------------------------
class CertificationIn(_Base):
    kind: str = Field(default="certification", pattern="^(certification|training)$")
    title: str = Field(min_length=1, max_length=160)
    issuer: str = Field(default="", max_length=120)
    issued: str = Field(default="", max_length=60)
    credential_id: str = Field(default="", max_length=80)
    summary: str = ""
    link: str = Field(default="", max_length=500)


class CertificationOut(_Read, CertificationIn):
    file_name: str = Field(default="", exclude=True)

    @computed_field
    @property
    def has_file(self) -> bool:
        return bool(self.file_name)


class ReorderRequest(BaseModel):
    ids: list[int]


# ---- Aggregated public payload -------------------------------------------
class PortfolioOut(BaseModel):
    sections: dict[str, dict[str, Any]]
    facts: list[FactOut]
    projects: list[ProjectOut]
    timeline: list[TimelineOut]
    skills: list[SkillOut]
    life_cards: list[LifeCardOut]
    certifications: list[CertificationOut]
    resume_available: bool
