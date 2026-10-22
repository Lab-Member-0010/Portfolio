from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import DB
from app.models import Certification, Fact, LifeCard, Message, Project, Skill, TimelineItem
from app.schemas.content import (
    CertificationOut, FactOut, LifeCardOut, PortfolioOut, ProjectOut, SkillOut, TimelineOut,
)
from app.schemas.message import MessageIn
from app.services import ratelimit
from app.services.resume import resume_info, resume_ref
from app.services.sections import get_all_sections
from app.services.storage import storage_for

router = APIRouter(tags=["public"])

MESSAGE_LIMIT, MESSAGE_WINDOW = 5, 600  # 5 messages / 10 min / visitor


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
        resume_available=resume_info(db)["available"],
    )


@router.get("/resume")
def download_resume(db: DB):
    ref = resume_ref(db)
    if not ref:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Résumé not uploaded yet")
    return storage_for(ref).response(ref, "Jayesh-Sharma-Resume.pdf", inline=False)


@router.get("/certifications/{item_id}/file")
def certificate_file(item_id: int, db: DB):
    cert = db.get(Certification, item_id)
    if cert is None or not cert.is_published or not cert.file_name:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate not found")
    filename = cert.file_name.rsplit("/", 1)[-1].split("?")[0]
    return storage_for(cert.file_name).response(cert.file_name, filename, inline=True)


@router.post("/messages", status_code=201)
def send_message(body: MessageIn, request: Request, db: DB):
    if body.website:  # honeypot tripped: pretend success
        return {"ok": True}
    key = f"msg:{ratelimit.client_ip(request)}"
    ratelimit.check(db, key, MESSAGE_LIMIT, MESSAGE_WINDOW, "Too many messages — please try again later")
    ratelimit.record(db, key)
    db.add(Message(name=body.name.strip(), email=body.email, subject=body.subject.strip(), body=body.body.strip()))
    db.commit()
    return {"ok": True}
