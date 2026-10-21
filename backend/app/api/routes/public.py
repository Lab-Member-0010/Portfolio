import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.api.deps import DB
from app.models import Certification, Fact, LifeCard, Message, Project, Skill, TimelineItem
from app.schemas.content import (
    CertificationOut, FactOut, LifeCardOut, PortfolioOut, ProjectOut, SkillOut, TimelineOut,
)
from app.schemas.message import MessageIn
from app.services.files import certificates_dir
from app.services.resume import resume_info, resume_path
from app.services.sections import get_all_sections

router = APIRouter(tags=["public"])

_RATE: dict[str, deque] = defaultdict(deque)
_RATE_LIMIT, _RATE_WINDOW = 5, 600  # 5 messages / 10 min / IP


def _published(db, model):
    stmt = select(model).where(model.is_published.is_(True)).order_by(model.sort_order, model.id)
    return db.scalars(stmt).all()


@router.get("/portfolio", response_model=PortfolioOut)
def portfolio(db: DB):
    return PortfolioOut(
        sections=get_all_sections(db),
        facts=[FactOut.model_validate(x) for x in _published(db, Fact)],
        projects=[ProjectOut.model_validate(x) for x in _published(db, Project)],
        timeline=[TimelineOut.model_validate(x) for x in _published(db, TimelineItem)],
        skills=[SkillOut.model_validate(x) for x in _published(db, Skill)],
        life_cards=[LifeCardOut.model_validate(x) for x in _published(db, LifeCard)],
        certifications=[CertificationOut.model_validate(x) for x in _published(db, Certification)],
        resume_available=resume_info()["available"],
    )


@router.get("/resume")
def download_resume():
    path = resume_path()
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Résumé not uploaded yet")
    return FileResponse(path, media_type="application/pdf", filename="Jayesh-Sharma-Resume.pdf")


@router.get("/certifications/{item_id}/file")
def certificate_file(item_id: int, db: DB):
    cert = db.get(Certification, item_id)
    if cert is None or not cert.is_published or not cert.file_name:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate not found")
    path = certificates_dir() / cert.file_name
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate file missing")
    return FileResponse(path, media_type="application/pdf", content_disposition_type="inline", filename=cert.file_name)


@router.post("/messages", status_code=201)
def send_message(body: MessageIn, request: Request, db: DB):
    if body.website:  # honeypot tripped: pretend success
        return {"ok": True}
    ip = request.client.host if request.client else "unknown"
    now, q = time.time(), _RATE[ip]
    while q and now - q[0] > _RATE_WINDOW:
        q.popleft()
    if len(q) >= _RATE_LIMIT:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many messages — please try again later")
    q.append(now)
    db.add(Message(name=body.name.strip(), email=body.email, subject=body.subject.strip(), body=body.body.strip()))
    db.commit()
    return {"ok": True}
