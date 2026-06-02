import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from infrastructure.database.connection_admin import AsyncAdminSessionLocal
from infrastructure.database.models.admin_auth.admin_profile import AdminProfile

from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin(email: str, password: str | None):
    print("Checking database for existing profile...")
    
    password_hash = pwd_context.hash(password) if password else None
    
    async with AsyncAdminSessionLocal() as db:
        result = await db.execute(
            select(AdminProfile).where(AdminProfile.email == email)
        )
        existing_profiles = result.scalars().all()

        if len(existing_profiles) == 0:
            print("Inserting new admin profile into database...")
            new_profile = AdminProfile(
                email=email,
                auth_provider="local",
                provider_id=None,
                password_hash=password_hash,
                role="admin"
            )
            db.add(new_profile)
            await db.commit()
            print(f"Admin profile successfully created for {email}!")
            return

        target_profile = None

        if len(existing_profiles) == 1:
            target_profile = existing_profiles[0]
        else:
            print(f"\nZnaleziono {len(existing_profiles)} kont powiązanych z adresem {email}.")
            print("Wybierz, któremu z nich chcesz nadać uprawnienia:")
            for i, p in enumerate(existing_profiles):
                print(f"[{i+1}] Provider: {p.auth_provider}")
            
            while True:
                choice = input("Twój wybór (numer): ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(existing_profiles):
                        target_profile = existing_profiles[idx]
                        break
                    else:
                        print("Nieprawidłowy numer, spróbuj ponownie.")
                except ValueError:
                    print("Podaj poprawny numer.")

        print(f"\nUpdating role to 'admin' for {email} (Provider: {target_profile.auth_provider})...")
        target_profile.role = "admin"
        if password_hash:
            target_profile.password_hash = password_hash
        await db.commit()
        print(f"Admin profile successfully updated for {target_profile.email}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("--email", required=True, help="Email address of the admin")
    parser.add_argument("--password", help="Password (optional: if omitted, user must use Google/GitHub to log in)")
    args = parser.parse_args()
    
    asyncio.run(create_admin(args.email, args.password))
