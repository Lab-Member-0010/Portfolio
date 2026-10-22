import os
import tempfile

_tmp = tempfile.mkdtemp()
# Run against Postgres with: TEST_DATABASE_URL=postgresql://user@host:5432/db pytest
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_tmp}/test.db")
os.environ.pop("BLOB_READ_WRITE_TOKEN", None)
os.environ.pop("VERCEL", None)
os.environ["UPLOAD_DIR"] = _tmp
os.environ["ADMIN_EMAIL"] = "admin@test.dev"
os.environ["ADMIN_PASSWORD"] = "secret-pass-1"
os.environ["FRONTEND_DIST"] = f"{_tmp}/nodist"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth(client):
    r = client.post("/api/auth/login", json={"email": "admin@test.dev", "password": "secret-pass-1"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_public_portfolio_seeded(client):
    r = client.get("/api/portfolio")
    assert r.status_code == 200
    data = r.json()
    assert len(data["projects"]) == 5
    assert data["sections"]["hero"]["first_name"] == "Jayesh"


def test_admin_requires_auth(client):
    assert client.get("/api/admin/projects").status_code == 401
    assert client.post("/api/auth/login", json={"email": "admin@test.dev", "password": "nope"}).status_code == 401


def test_project_crud_and_publish(client, auth):
    r = client.post("/api/admin/projects", json={"title": "New Thing", "tags": "A, B"}, headers=auth)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert r.json()["tags"] == ["A", "B"]
    r = client.put(f"/api/admin/projects/{pid}", json={"title": "Hidden", "is_published": False}, headers=auth)
    assert r.json()["is_published"] is False
    titles = [p["title"] for p in client.get("/api/portfolio").json()["projects"]]
    assert "Hidden" not in titles
    assert client.delete(f"/api/admin/projects/{pid}", headers=auth).status_code == 204


def test_reorder(client, auth):
    ids = [p["id"] for p in client.get("/api/admin/skills", headers=auth).json()]
    r = client.post("/api/admin/skills/reorder", json={"ids": ids[::-1]}, headers=auth)
    assert [s["id"] for s in r.json()] == ids[::-1]


def test_section_update(client, auth):
    r = client.put("/api/admin/sections/hero", json={"statement": "Hello *world*", "bogus": 1}, headers=auth)
    assert r.status_code == 200 and r.json()["statement"] == "Hello *world*" and "bogus" not in r.json()
    assert client.get("/api/portfolio").json()["sections"]["hero"]["statement"] == "Hello *world*"


def test_messages_flow(client, auth):
    r = client.post("/api/messages", json={"name": "Ana", "email": "ana@x.io", "body": "Let's build something"})
    assert r.status_code == 201
    msgs = client.get("/api/admin/messages", headers=auth).json()
    assert msgs[0]["name"] == "Ana" and msgs[0]["is_read"] is False
    r = client.patch(f"/api/admin/messages/{msgs[0]['id']}", json={"is_read": True}, headers=auth)
    assert r.json()["is_read"] is True


def test_resume_upload_and_download(client, auth):
    bad = client.post("/api/admin/resume", files={"file": ("x.txt", b"hello", "text/plain")}, headers=auth)
    assert bad.status_code == 400
    ok = client.post("/api/admin/resume", files={"file": ("r.pdf", b"%PDF-1.4 test", "application/pdf")}, headers=auth)
    assert ok.json()["available"] is True
    dl = client.get("/api/resume")
    assert dl.status_code == 200 and dl.content.startswith(b"%PDF")


def test_change_password(client, auth):
    r = client.post("/api/auth/change-password", json={"current_password": "wrong", "new_password": "newpass123"}, headers=auth)
    assert r.status_code == 400


def test_certifications_seeded_and_file_flow(client, auth):
    certs = client.get("/api/portfolio").json()["certifications"]
    titles = [c["title"] for c in certs]
    assert any("Creatio" in t for t in titles) and any("MERN" in t for t in titles)
    assert "file_name" not in certs[0]
    cid = next(c["id"] for c in certs if "MERN" in c["title"])
    assert client.get(f"/api/certifications/{cid}/file").status_code == 404
    r = client.post(f"/api/admin/certifications/{cid}/file", files={"file": ("c.pdf", b"%PDF-1.4 x", "application/pdf")}, headers=auth)
    assert r.status_code == 200 and r.json()["has_file"] is True
    assert client.get(f"/api/certifications/{cid}/file").content.startswith(b"%PDF")
    assert client.delete(f"/api/admin/certifications/{cid}/file", headers=auth).json()["has_file"] is False


def test_portfolio_experience_dates(client):
    data = client.get("/api/portfolio").json()
    assert data["sections"]["experience"]["period"] == "May 2025 — Present"
    assert not any(f["label"] == "Years in the arena" for f in data["facts"])


def test_migration_updates_old_defaults(client):
    from app.db.session import SessionLocal
    from app.models import AppMeta, Fact, SiteSection
    from app.services.migrations import run_migrations

    with SessionLocal() as db:
        db.add(Fact(value="2", suffix="+", label="Years in the arena"))
        row = db.get(SiteSection, "experience") or SiteSection(key="experience", data={})
        row.data = {"period": "May 2024 — Present", "years": "02", "company": "Custom Co"}
        db.merge(row)
        db.get(AppMeta, "content_version").value = "1"
        db.commit()
        run_migrations(db, fresh_install=False)
        exp = db.get(SiteSection, "experience").data
        assert exp["period"] == "May 2025 — Present" and exp["years"] == "1.5" and exp["company"] == "Custom Co"
        assert db.query(Fact).filter_by(label="Years in the arena").count() == 0
        from app.services.migrations import LATEST
        assert db.get(AppMeta, "content_version").value == str(LATEST)


def test_database_url_normalisation():
    from app.core.config import Settings

    neon = "postgresql://u:p@ep-x-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    assert Settings(database_url=neon).resolved_database_url.startswith("postgresql+psycopg://u:p@ep-x-pooler")
    assert Settings(database_url="postgres://u:p@h/db").resolved_database_url == "postgresql+psycopg://u:p@h/db"
    assert Settings(database_url="postgresql+psycopg://u:p@h/db").resolved_database_url == "postgresql+psycopg://u:p@h/db"


def test_message_rate_limit_per_forwarded_ip(client):
    from app.core.config import get_settings

    s = get_settings()
    s.trust_proxy_headers = True
    try:
        msg = {"name": "Bot", "email": "bot@x.io", "body": "hello there"}
        for _ in range(5):
            assert client.post("/api/messages", json=msg, headers={"x-forwarded-for": "203.0.113.7, 10.0.0.1"}).status_code == 201
        assert client.post("/api/messages", json=msg, headers={"x-forwarded-for": "203.0.113.7"}).status_code == 429
        # a different visitor behind the same proxy is unaffected
        assert client.post("/api/messages", json=msg, headers={"x-forwarded-for": "198.51.100.9"}).status_code == 201
    finally:
        s.trust_proxy_headers = False


def test_login_throttle(client):
    from app.core.config import get_settings

    s = get_settings()
    s.trust_proxy_headers = True
    ip = {"x-forwarded-for": "192.0.2.55"}
    try:
        for _ in range(10):
            r = client.post("/api/auth/login", json={"email": "admin@test.dev", "password": "wrong"}, headers=ip)
            assert r.status_code == 401
        r = client.post("/api/auth/login", json={"email": "admin@test.dev", "password": "secret-pass-1"}, headers=ip)
        assert r.status_code == 429
        other = client.post("/api/auth/login", json={"email": "admin@test.dev", "password": "secret-pass-1"},
                            headers={"x-forwarded-for": "192.0.2.56"})
        assert other.status_code == 200
    finally:
        s.trust_proxy_headers = False


def test_blob_storage_flow(client, auth):
    """Uploads go to Vercel Blob (mocked) and public links redirect to the blob URL."""
    import json as _json

    import httpx

    from app.services.storage import BlobStorage, set_storage

    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.method == "PUT":
            path = request.url.params["pathname"]
            return httpx.Response(200, json={
                "url": f"https://storeabc.public.blob.vercel-storage.com/{path[:-4]}-RaNd.pdf",
                "pathname": path,
            })
        if request.url.path.endswith("/delete"):
            return httpx.Response(200, json={})
        return httpx.Response(404)

    set_storage(BlobStorage("vercel_blob_rw_storeabc_secret", transport=httpx.MockTransport(handler)))
    try:
        cid = client.get("/api/admin/certifications", headers=auth).json()[1]["id"]
        r = client.post(f"/api/admin/certifications/{cid}/file",
                        files={"file": ("c.pdf", b"%PDF-1.4 blob", "application/pdf")}, headers=auth)
        assert r.status_code == 200 and r.json()["has_file"]
        put = calls[-1]
        assert put.method == "PUT" and put.url.host == "vercel.com" and put.url.path == "/api/blob/"
        assert put.url.params["pathname"].startswith(f"certificates/{cid}-")
        assert put.headers["authorization"] == "Bearer vercel_blob_rw_storeabc_secret"
        assert put.headers["x-vercel-blob-store-id"] == "storeabc"
        assert put.headers["x-vercel-blob-access"] == "public"
        assert put.content == b"%PDF-1.4 blob"

        redirect = client.get(f"/api/certifications/{cid}/file", follow_redirects=False)
        assert redirect.status_code == 307
        assert redirect.headers["location"].startswith("https://storeabc.public.blob.vercel-storage.com/certificates/")

        r = client.post("/api/admin/resume", files={"file": ("r.pdf", b"%PDF-1.4 cv", "application/pdf")}, headers=auth)
        assert r.json()["available"] is True
        dl = client.get("/api/resume", follow_redirects=False)
        assert dl.status_code == 307 and dl.headers["location"].endswith("?download=1")

        old_url = redirect.headers["location"]
        assert client.delete(f"/api/admin/certifications/{cid}/file", headers=auth).json()["has_file"] is False
        deleted = [c for c in calls if c.url.path.endswith("/delete")]
        assert _json.loads(deleted[-1].content) == {"urls": [old_url]}
    finally:
        set_storage(None)
