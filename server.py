import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Monumen Pin Manager")

PINTEREST_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
BASE_URL = "https://pinterest.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {PINTEREST_TOKEN}",
        "Content-Type": "application/json",
    }


@mcp.tool()
async def get_account_info() -> dict:
    """Get authenticated user profile details."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/user_account", headers=_headers())
        res.raise_for_status()
        return res.json()


@mcp.tool()
async def list_boards() -> dict:
    """List all boards in the account."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/boards", headers=_headers())
        res.raise_for_status()
        return res.json()


@mcp.tool()
async def create_board(name: str, description: str = "", privacy: str = "PUBLIC") -> dict:
    """Create a new board. Privacy can be PUBLIC, PROTECTED, or SECRET."""
    payload = {"name": name, "description": description, "privacy": privacy}
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/boards", headers=_headers(), json=payload)
        res.raise_for_status()
        return res.json()


@mcp.tool()
async def list_pins(board_id: str = "") -> dict:
    """List pins across the account, or inside a specific board if board_id is given."""
    url = f"{BASE_URL}/boards/{board_id}/pins" if board_id else f"{BASE_URL}/pins"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=_headers())
        res.raise_for_status()
        return res.json()


@mcp.tool()
async def create_pin(
    board_id: str,
    title: str,
    description: str,
    image_url: str,
    link: str = "",
    alt_text: str = "",
) -> dict:
    """Publish a new Pin to a board using a public image URL."""
    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "media_source": {"source_type": "image_url", "url": image_url},
    }
    if link:
        payload["link"] = link
    if alt_text:
        payload["alt_text"] = alt_text

    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/pins", headers=_headers(), json=payload)
        res.raise_for_status()
        return res.json()


@mcp.tool()
async def delete_pin(pin_id: str) -> dict:
    """Delete a pin by its ID."""
    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{BASE_URL}/pins/{pin_id}", headers=_headers())
        res.raise_for_status()
        return {"status": "deleted", "pin_id": pin_id}


@mcp.tool()
async def custom_api_call(method: str, endpoint: str, body: dict = None) -> dict:
    """Execute any Pinterest API v5 endpoint (e.g., GET /boards/{id}, PATCH /pins/{id})."""
    async with httpx.AsyncClient() as client:
        res = await client.request(
            method.upper(),
            f"{BASE_URL}/{endpoint.lstrip('/')}",
            headers=_headers(),
            json=body,
        )
        res.raise_for_status()
        return res.json() if res.content else {"status": "success"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
