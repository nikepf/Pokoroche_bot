import argparse
import asyncio
import os
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from src.pokoroche.domain.models.user import UserEntity
from src.pokoroche.domain.models.message import MessageEntity
from src.pokoroche.infrastructure.database.database import Database
from src.pokoroche.infrastructure.database.repositories.user_repository import UserRepository
from src.pokoroche.infrastructure.database.repositories.message_repository import MessageRepository
from src.pokoroche.infrastructure.database.repositories.digest_repository import DigestRepository


async def _run(database_url: str, users: int, messages_per_user: int) -> None:
    db = Database(database_url)
    await db.connect()

    async with db.get_session() as session:
        user_repo = UserRepository(session)
        message_repo = MessageRepository(session)
        digest_repo = DigestRepository(session)

        created_users = []
        for i in range(users):
            u = UserEntity(
                telegram_id=10_000_000 + i,
                username=f"test_user_{i}",
                first_name=f"Test{i}",
                last_name="User",
            )
            created_users.append(await user_repo.insert(u))

        now = datetime.utcnow()
        topic_pool = ["study", "crypto", "hse", "math", "life"]

        msg_id = 1_000_000
        for u in created_users:
            for _ in range(messages_per_user):
                topics = random.sample(topic_pool, k=random.randint(0, min(3, len(topic_pool))))
                score = round(random.random(), 3)
                m = MessageEntity(
                    telegram_message_id=msg_id,
                    chat_id=100_000 + int(u.telegram_id),
                    user_id=int(u.id),
                    text=f"seed message {msg_id}",
                    importance_score=score,
                    topics=topics,
                    metadata={"seed": True},
                    created_at=now - timedelta(minutes=random.randint(0, 60 * 24)),
                )
                await message_repo.save(m)
                msg_id += 1

        await session.commit()

        user = await user_repo.find_by_telegram_id(10_000_000)
        if user is None:
            raise RuntimeError("Seed failed: user not found")

        recent = await message_repo.get_recent_messages(int(user.id), limit=5)
        important = await message_repo.get_important_messages(int(user.id), threshold=0.7)

        items = await digest_repo.get_important_items(
            telegram_id=int(user.telegram_id),
            from_time=now - timedelta(hours=24),
            topics=["study"],
        )

        print(f"Seed OK: users={len(created_users)}")
        print(f"Repo OK: recent={len(recent)} important(>=0.7)={len(important)} digest_items(study,24h)={len(items)}")

    await db.disconnect()


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    load_dotenv(root / ".env")

    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--messages-per-user", type=int, default=20)
    parser.add_argument("--migrate", action="store_true")
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    if args.migrate:
        env = dict(os.environ)
        env["DATABASE_URL"] = database_url
        config_path = root / "alembic.ini"
        subprocess.run(["alembic", "-c", str(config_path), "upgrade", "head"], check=True, cwd=str(root), env=env)

    asyncio.run(_run(database_url, args.users, args.messages_per_user))


if __name__ == "__main__":
    main()
