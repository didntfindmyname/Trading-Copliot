from __future__ import annotations

import asyncio
from io import BytesIO

from fastapi import UploadFile

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService


RUNBOOK = """
# Market Data Ingestion Runbook

If a market data ingestion job fails, first check Redis queue depth and the exchange gateway heartbeat.
Restart the affected Celery worker only after confirming the upstream feed is healthy. Reprocess from the
last committed sequence number and verify downstream feature stores have caught up before releasing alerts.

Escalate to the operations lead if quote gaps exceed two minutes during active trading hours.
"""


async def main() -> None:
    async with AsyncSessionLocal() as session:
        users = UserRepository(session)
        admin = await users.get_by_email("admin@athena.local")
        if admin is None:
            admin = User(
                email="admin@athena.local",
                full_name="Athena Admin",
                hashed_password=get_password_hash("AthenaAdmin123!"),
                role="admin",
            )
            session.add(admin)
        researcher = await users.get_by_email("researcher@athena.local")
        if researcher is None:
            researcher = User(
                email="researcher@athena.local",
                full_name="Research User",
                hashed_password=get_password_hash("AthenaResearch123!"),
                role="researcher",
            )
            session.add(researcher)
        await session.commit()
        file = UploadFile(
            filename="market-data-runbook.md",
            file=BytesIO(RUNBOOK.encode("utf-8")),
            headers={"content-type": "text/markdown"},
        )
        document = await DocumentService(session).upload(
            user=researcher,
            file=file,
            title="Market Data Ingestion Runbook",
        )
        await DocumentService(session).index(document.id)
        print("Seeded admin, researcher, and market data runbook")


if __name__ == "__main__":
    asyncio.run(main())
