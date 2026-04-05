"""Script para poblar la base de datos con datos de prueba."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import get_db_session
from src.infrastructure.database.repositories import UserRepository
from src.domain.entities.user import User, UserRole
from src.shared.logging import get_logger

logger = get_logger("seed_data")


async def create_users():
    """Crea usuarios de prueba."""
    async for session in get_db_session():
        user_repo = UserRepository(session)

        users_data = [
            {
                "email": "admin@example.com",
                "username": "admin",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "first_name": "Admin",
                "last_name": "User",
                "department": "IT",
            },
            {
                "email": "tech1@example.com",
                "username": "tech1",
                "password": "tech123",
                "role": UserRole.TECHNICIAN,
                "first_name": "John",
                "last_name": "Doe",
                "department": "Support",
            },
            {
                "email": "tech2@example.com",
                "username": "tech2",
                "password": "tech123",
                "role": UserRole.TECHNICIAN,
                "first_name": "Jane",
                "last_name": "Smith",
                "department": "Support",
            },
            {
                "email": "user@example.com",
                "username": "user",
                "password": "user123",
                "role": UserRole.USER,
                "first_name": "Bob",
                "last_name": "Wilson",
                "department": "Sales",
            },
        ]

        created_count = 0
        for user_data in users_data:
            existing = await user_repo.get_by_email(user_data["email"])
            if existing:
                logger.info(f"User {user_data['email']} already exists, skipping")
                continue

            user = User()
            user.email = user_data["email"]
            user.username = user_data["username"]
            user.set_password(user_data["password"])
            user.role = user_data["role"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.department = user_data["department"]
            user.is_verified = True

            await user_repo.create(user)
            created_count += 1
            logger.info(f"Created user: {user_data['email']}")

        await session.commit()
        logger.info(f"Seeded {created_count} users")


async def main():
    """Pobla la base de datos."""
    logger.info("Seeding database...")

    try:
        await create_users()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
