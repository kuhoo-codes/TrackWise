import httpx
from fastapi import HTTPException, status


async def exchange_github_code(code: str, client_id: str, client_secret: str) -> dict:
    """Handle GitHub OAuth code exchange"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={"client_id": client_id, "client_secret": client_secret, "code": code},
            headers={"Accept": "application/json"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get GitHub access token")
    return response.json()
