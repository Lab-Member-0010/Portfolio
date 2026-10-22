from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_name: str = "Jayesh Sharma Portfolio API"
    database_url: str = f"sqlite:///{BASE_DIR / 'portfolio.db'}"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "./uploads"
    frontend_dist: str = "../frontend/dist"
    max_resume_mb: int = 10
    # Vercel Blob: set automatically when a Blob store is connected to the project.
    blob_read_write_token: str = ""
    # Vercel sets VERCEL=1 at runtime; used to trust its x-forwarded-for header.
    vercel: str = ""
    trust_proxy_headers: bool = False

    @property
    def on_vercel(self) -> bool:
        return bool(self.vercel)

    @property
    def use_blob_storage(self) -> bool:
        return bool(self.blob_read_write_token)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def _resolve(self, value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def upload_path(self) -> Path:
        path = self._resolve(self.upload_dir)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:  # read-only filesystem (e.g. serverless) — reads still work
            pass
        return path

    @property
    def frontend_dist_path(self) -> Path:
        return self._resolve(self.frontend_dist)

    @property
    def resolved_database_url(self) -> str:
        # make relative sqlite paths relative to backend/ rather than CWD
        url = self.database_url.strip()
        prefix = "sqlite:///./"
        if url.startswith(prefix):
            return f"sqlite:///{BASE_DIR / url[len(prefix):]}"
        # Neon/Vercel hand out postgres:// or postgresql:// — use the psycopg 3 driver.
        for scheme in ("postgres://", "postgresql://"):
            if url.startswith(scheme):
                return "postgresql+psycopg://" + url[len(scheme):]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
