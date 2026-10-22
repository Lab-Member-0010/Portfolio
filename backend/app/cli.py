"""Command line helpers.

    python -m app.cli init      create tables, seed content, upload bundled PDFs
    python -m app.cli check     print which database and storage the current settings point to
"""
import sys

from app.core.config import get_settings


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    s = get_settings()
    db_url = s.resolved_database_url
    safe_db = db_url.split("@")[-1] if "@" in db_url else db_url
    storage = "Vercel Blob" if s.use_blob_storage else f"local disk ({s.upload_path})"
    if cmd == "check":
        print(f"database: {safe_db}\nstorage:  {storage}")
        return 0
    if cmd == "init":
        from app.services.bootstrap import init_data

        print(f"Initialising {safe_db} with {storage} …")
        init_data()
        print("Done ✓  tables created, content seeded, bundled PDFs in place.")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
