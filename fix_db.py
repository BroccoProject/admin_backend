import asyncio
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from infrastructure.database.models.admin_auth.admin_profile import AdminProfile

async def main():
    engine = create_async_engine(settings.DATABASE_URL_ADMIN)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find all emails
        result = await session.execute(select(AdminProfile.email).distinct())
        emails = result.scalars().all()
        
        for email in emails:
            # Get profiles for this email
            result = await session.execute(
                select(AdminProfile).where(AdminProfile.email == email).order_by(AdminProfile.created_at.desc())
            )
            profiles = result.scalars().all()
            
            if len(profiles) > 1:
                print(f"Found duplicates for {email}")
                # We want to keep the one with the highest role (admin > editor > viewer)
                role_priority = {"admin": 3, "editor": 2, "viewer": 1}
                profiles.sort(key=lambda p: role_priority.get(p.role, 0), reverse=True)
                
                keeper = profiles[0]
                google_sub = next((p.google_sub for p in profiles if p.google_sub), None)
                
                for p in profiles:
                    p.google_sub = None
                
                await session.flush()
                
                # Assign google sub to keeper
                if google_sub:
                    keeper.google_sub = google_sub
                    
                session.add(keeper)
                
                # Delete others
                for p in profiles[1:]:
                    await session.delete(p)
                    
        await session.commit()
        print("Database cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())
