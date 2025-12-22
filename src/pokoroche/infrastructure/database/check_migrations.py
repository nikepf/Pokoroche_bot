import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    load_dotenv(root / ".env")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    env = dict(os.environ)
    env["DATABASE_URL"] = database_url

    config_path = root / "alembic.ini"

    subprocess.run(["alembic", "-c", str(config_path), "upgrade", "head"], check=True, cwd=str(root), env=env)
    subprocess.run(["alembic", "-c", str(config_path), "downgrade", "base"], check=True, cwd=str(root), env=env)
    subprocess.run(["alembic", "-c", str(config_path), "upgrade", "head"], check=True, cwd=str(root), env=env)

    print("Migrations OK")


if __name__ == "__main__":
    main()
