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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def _resolve(self, value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def upload_path(self) -> Path:
        path = self._resolve(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def frontend_dist_path(self) -> Path:
        return self._resolve(self.frontend_dist)

    @property
    def resolved_database_url(self) -> str:
        # make relative sqlite paths relative to backend/ rather than CWD
        prefix = "sqlite:///./"
        if self.database_url.startswith(prefix):
            return f"sqlite:///{BASE_DIR / self.database_url[len(prefix):]}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
