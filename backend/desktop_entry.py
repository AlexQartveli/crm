"""Точка входа для Windows desktop (PyInstaller)."""
import os
import sys
from pathlib import Path


def _prepare_runtime() -> None:
    if getattr(sys, "frozen", False):
        os.chdir(Path(sys.executable).parent)

    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    db_path = Path(appdata) / "Kinetix" / "kinetix.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("KINETIX_DB_PATH", str(db_path))


def main() -> None:
    _prepare_runtime()
    import uvicorn
    from app.main import app

    port = int(os.environ.get("KINETIX_PORT", "8765"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
