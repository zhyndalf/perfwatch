"""Database initialization script with default data."""

import asyncio
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import User, Config, ArchivePolicy
from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def create_default_admin(session: AsyncSession) -> None:
    """Create default admin user if it doesn't exist."""
    result = await session.execute(
        select(User).where(User.username == settings.ADMIN_USERNAME)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        password_hash = hash_password(settings.ADMIN_PASSWORD)
        admin_user = User(
            username=settings.ADMIN_USERNAME,
            password_hash=password_hash,
        )
        session.add(admin_user)
        await session.commit()
        print(f"Created default admin user: {settings.ADMIN_USERNAME}")
    else:
        print(f"Admin user already exists: {settings.ADMIN_USERNAME}")


async def create_default_config(session: AsyncSession) -> None:
    """Create default configuration values if they don't exist."""
    default_configs = [
        {
            "key": "sampling",
            "value": {"interval_seconds": settings.SAMPLING_INTERVAL_SECONDS},
        },
        {
            "key": "retention",
            "value": {
                "days": 30,
                "archive_enabled": True,
                "downsample_after_days": 7,
                "downsample_interval": "1h",
            },
        },
        {
            "key": "features",
            "value": {"perf_events_enabled": True},
        },
    ]

    for cfg in default_configs:
        result = await session.execute(
            select(Config).where(Config.key == cfg["key"])
        )
        existing = result.scalar_one_or_none()

        if existing is None:
            config = Config(key=cfg["key"], value=cfg["value"])
            session.add(config)
            print(f"Created config: {cfg['key']}")
        else:
            print(f"Config already exists: {cfg['key']}")

    await session.commit()


async def create_default_archive_policy(session: AsyncSession) -> None:
    """Create default archive policy if it doesn't exist."""
    result = await session.execute(select(ArchivePolicy))
    existing = result.scalar_one_or_none()

    if existing is None:
        policy = ArchivePolicy(
            retention_days=30,
            archive_enabled=True,
            downsample_after_days=7,
            downsample_interval="1 hour",
        )
        session.add(policy)
        await session.commit()
        print("Created default archive policy")
    else:
        print("Archive policy already exists")


async def init_default_data() -> None:
    """Initialize database with default data."""
    print("Initializing default data...")

    async with AsyncSessionLocal() as session:
        await create_default_admin(session)
        await create_default_config(session)
        await create_default_archive_policy(session)

    print("Default data initialization complete")


if __name__ == "__main__":
    asyncio.run(init_default_data())
