import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from infrastructure.database.connection_admin import AsyncAdminSessionLocal
from infrastructure.database.models.admin_auth.admin_profile import AdminProfile

async def create_admin(email: str, google_sub: str):
    print("Inserting admin profile into database...")
    async with AsyncAdminSessionLocal() as db:
        new_profile = AdminProfile(
            email=email,
            google_sub=google_sub,
            role="admin"
        )
        db.add(new_profile)
        await db.commit()
        print(f"Admin profile successfully created for {email}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("--email", required=True, help="Email address of the admin")
    parser.add_argument("--google-sub", required=True, help="Google subject identifier of the admin")
    args = parser.parse_args()

    asyncio.run(create_admin(args.email, args.google_sub))
