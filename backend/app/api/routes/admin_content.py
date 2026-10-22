"""Admin CRUD for every repeatable content collection, built from one factory."""
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import func, select

from app.api.deps import DB, CurrentAdmin, get_current_admin
from app.models import Certification, Fact, LifeCard, Project, Skill, TimelineItem
from app.schemas.content import (
    CertificationIn, CertificationOut, FactIn, FactOut, LifeCardIn, LifeCardOut, ProjectIn, ProjectOut,
    ReorderRequest, SkillIn, SkillOut, TimelineIn, TimelineOut,
)
from app.services.files import certificate_key, read_pdf_upload
from app.services.storage import get_storage, storage_for
from app.services.sections import SECTION_KEYS, get_section, save_section

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


# ---- Singleton sections -----------------------------------------------------
@router.get("/sections")
def list_sections(db: DB) -> dict[str, dict[str, Any]]:
    return {k: get_section(db, k) for k in SECTION_KEYS}


@router.get("/sections/{key}")
def read_section(key: str, db: DB) -> dict[str, Any]:
    if key not in SECTION_KEYS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown section")
    return get_section(db, key)


@router.put("/sections/{key}")
def update_section(key: str, data: dict[str, Any], db: DB, _: CurrentAdmin) -> dict[str, Any]:
    if key not in SECTION_KEYS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown section")
    return save_section(db, key, data)


# ---- Collections ------------------------------------------------------------
def register_collection(
    name: str, model, schema_in: type[BaseModel], schema_out: type[BaseModel], on_delete=None
) -> None:
    def _get(db, item_id: int):
        obj = db.get(model, item_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{name} item not found")
        return obj

    @router.get(f"/{name}", response_model=list[schema_out], name=f"list_{name}")
    def list_items(db: DB):
        return db.scalars(select(model).order_by(model.sort_order, model.id)).all()

    @router.post(f"/{name}", response_model=schema_out, status_code=201, name=f"create_{name}")
    def create_item(body: schema_in, db: DB):  # type: ignore[valid-type]
        data = body.model_dump()
        if "sort_order" not in body.model_fields_set:
            data["sort_order"] = (db.scalar(select(func.max(model.sort_order))) or 0) + 1
        obj = model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @router.put(f"/{name}/{{item_id}}", response_model=schema_out, name=f"update_{name}")
    def update_item(item_id: int, body: schema_in, db: DB):  # type: ignore[valid-type]
        obj = _get(db, item_id)
        for k, v in body.model_dump().items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @router.delete(f"/{name}/{{item_id}}", status_code=204, name=f"delete_{name}")
    def delete_item(item_id: int, db: DB):
        obj = _get(db, item_id)
        if on_delete:
            on_delete(obj)
        db.delete(obj)
        db.commit()

    @router.post(f"/{name}/reorder", response_model=list[schema_out], name=f"reorder_{name}")
    def reorder(body: ReorderRequest, db: DB):
        items = {o.id: o for o in db.scalars(select(model)).all()}
        for i, item_id in enumerate(body.ids):
            if item_id in items:
                items[item_id].sort_order = i
        db.commit()
        return db.scalars(select(model).order_by(model.sort_order, model.id)).all()


register_collection("facts", Fact, FactIn, FactOut)
register_collection("projects", Project, ProjectIn, ProjectOut)
register_collection("timeline", TimelineItem, TimelineIn, TimelineOut)
register_collection("skills", Skill, SkillIn, SkillOut)
register_collection("life-cards", LifeCard, LifeCardIn, LifeCardOut)


def _remove_cert_file(cert: Certification) -> None:
    if cert.file_name:
        storage_for(cert.file_name).delete(cert.file_name)


register_collection("certifications", Certification, CertificationIn, CertificationOut, on_delete=_remove_cert_file)


@router.post("/certifications/{item_id}/file", response_model=CertificationOut)
async def upload_certificate_file(item_id: int, db: DB, file: UploadFile = File(...)):
    cert = db.get(Certification, item_id)
    if cert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "certifications item not found")
    data = await read_pdf_upload(file)
    new_ref = get_storage().save(certificate_key(cert.id, cert.title), data)
    if cert.file_name and cert.file_name != new_ref:
        _remove_cert_file(cert)
    cert.file_name = new_ref
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/certifications/{item_id}/file", response_model=CertificationOut)
def delete_certificate_file(item_id: int, db: DB):
    cert = db.get(Certification, item_id)
    if cert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "certifications item not found")
    _remove_cert_file(cert)
    cert.file_name = ""
    db.commit()
    db.refresh(cert)
    return cert
