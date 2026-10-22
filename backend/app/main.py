from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.api.routes import admin_content, admin_misc, auth, public
from app.core.config import get_settings
from app.services.bootstrap import ensure_initialized

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_in_threadpool(ensure_initialized)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def lazy_init(request: Request, call_next):
    # Serverless runtimes don't always send lifespan events; make sure the DB is ready.
    if request.url.path.startswith("/api") and request.url.path != "/api/health":
        await run_in_threadpool(ensure_initialized)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (public.router, auth.router, admin_content.router, admin_misc.router):
    app.include_router(r, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}


# Serve the production React build (npm run build) when it exists, with SPA fallback.
_dist = settings.frontend_dist_path
if (_dist / "index.html").exists():
    if (_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = (_dist / full_path).resolve()
        if full_path and candidate.is_file() and _dist in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(_dist / "index.html")
