import httpx
from fastapi import HTTPException
from urllib.parse import urlencode

from core.config import settings

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_USEREMAILS_URL = "https://api.github.com/user/emails"

def get_github_auth_url() -> str:
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email",
    }
    return f"{GITHUB_AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str) -> dict:
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(GITHUB_TOKEN_URL, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code for token")
        return response.json()

async def get_github_user_info(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(GITHUB_USERINFO_URL, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from GitHub")
        
        user_info = response.json()
        github_id = str(user_info.get("id"))
        email = user_info.get("email")

        # If email is not public, we need to fetch it from the emails endpoint
        if not email:
            emails_response = await client.get(GITHUB_USEREMAILS_URL, headers=headers)
            if emails_response.status_code == 200:
                emails_data = emails_response.json()
                # Find the primary, verified email
                for email_record in emails_data:
                    if email_record.get("primary") and email_record.get("verified"):
                        email = email_record.get("email")
                        break
        
        if not email:
            raise HTTPException(status_code=400, detail="No verified primary email found on GitHub account")
            
        return {"id": github_id, "email": email}
