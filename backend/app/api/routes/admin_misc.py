from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select

from app.api.deps import DB, get_current_admin
from app.services.files import read_pdf_upload
from app.models import Certification, Message, Project, Skill
from app.schemas.message import MessageOut, MessageUpdate
from app.services.resume import resume_info, resume_path

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/stats")
def stats(db: DB):
    return {
        "projects": db.scalar(select(func.count(Project.id))),
        "skills": db.scalar(select(func.count(Skill.id))),
        "certifications": db.scalar(select(func.count(Certification.id))),
        "messages": db.scalar(select(func.count(Message.id))),
        "unread_messages": db.scalar(select(func.count(Message.id)).where(Message.is_read.is_(False))),
        "resume": resume_info(),
    }


# ---- Messages -----------------------------------------------------------------
@router.get("/messages", response_model=list[MessageOut])
def list_messages(db: DB, unread_only: bool = False):
    stmt = select(Message).order_by(Message.created_at.desc())
    if unread_only:
        stmt = stmt.where(Message.is_read.is_(False))
    return db.scalars(stmt).all()


@router.patch("/messages/{message_id}", response_model=MessageOut)
def update_message(message_id: int, body: MessageUpdate, db: DB):
    msg = db.get(Message, message_id)
    if msg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    msg.is_read = body.is_read
    db.commit()
    db.refresh(msg)
    return msg


@router.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int, db: DB):
    msg = db.get(Message, message_id)
    if msg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    db.delete(msg)
    db.commit()


# ---- Résumé -------------------------------------------------------------------
@router.get("/resume")
def get_resume_info():
    return resume_info()


@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    data = await read_pdf_upload(file)
    tmp = resume_path().with_suffix(".tmp")
    tmp.write_bytes(data)
    tmp.replace(resume_path())
    return resume_info()


@router.delete("/resume", status_code=204)
def delete_resume():
    resume_path().unlink(missing_ok=True)
