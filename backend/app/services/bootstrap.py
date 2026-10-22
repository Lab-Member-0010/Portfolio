"""Create tables, seed content, run content migrations and make sure bundled PDFs are in storage.

Safe to call repeatedly: it runs from the app lifespan, lazily on the first request (serverless
runtimes may skip lifespan events), and from `python -m app.cli init`.
"""
import logging
import threading

from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.models import AppMeta, Certification
from app.services import resume as resume_svc
from app.services.migrations import run_migrations
from app.services.seed import seed
from app.services.storage import LocalStorage, get_storage, is_url

log = logging.getLogger("portfolio.bootstrap")
_lock = threading.Lock()
_done = False

RESUME_SEEDED_KEY = "resume_seeded"


def _sync_bundled_files(db: Session) -> None:
    storage = get_storage()
    bundle = LocalStorage(get_settings().upload_path)

    # Résumé: adopt the bundled PDF once (a later delete in the admin is respected).
    if db.get(AppMeta, RESUME_SEEDED_KEY) is None:
        if not resume_svc.resume_ref(db) and bundle.exists(resume_svc.DEFAULT_LOCAL_REF):
            if isinstance(storage, LocalStorage):
                resume_svc._set(db, resume_svc.REF_KEY, resume_svc.DEFAULT_LOCAL_REF)
                db.commit()
            else:
                data = (bundle.root / resume_svc.DEFAULT_LOCAL_REF).read_bytes()
                resume_svc.save_resume(db, data)
        db.add(AppMeta(key=RESUME_SEEDED_KEY, value="1"))
        db.commit()

    # Certificates: when Blob is active, upload any PDF still referenced as a bundled local path.
    if not isinstance(storage, LocalStorage):
        for cert in db.scalars(select(Certification).where(Certification.file_name != "")).all():
            if not is_url(cert.file_name) and bundle.exists(cert.file_name):
                cert.file_name = storage.save(cert.file_name, (bundle.root / cert.file_name).read_bytes())
                db.commit()


def init_data() -> None:
    fresh_install = not inspect(engine).has_table("admin_users")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            seed(db)
            run_migrations(db, fresh_install)
            _sync_bundled_files(db)
        except IntegrityError:
            # another instance initialised at the same moment — its work stands
            db.rollback()


def ensure_initialized() -> None:
    global _done
    if _done:
        return
    with _lock:
        if not _done:
            init_data()
            _done = True
