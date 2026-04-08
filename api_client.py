import asyncio
import json
import logging
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Rate limit: conservative delay between requests (seconds)
REQUEST_DELAY = 0.4

# Service IDs to exclude (mini-envios = service 4)
EXCLUDED_SERVICE_IDS = [4]

class SuperfreteClient:
    def __init__(self, token: str, base_url: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SuperfreteIntegration " + os.getenv("SUPERFRETE_EMAIL")
        }
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def get_shipping_rates(self, from_postal: str, to_postal: str, package: dict) -> list[dict]:
        """
        Calls the calculator endpoint and returns available services,
        excluding mini-envios.
        """
        # Omitting "services" key entirely requests all available services from the API
        #1 (PAC), 2 (SEDEX), 17 (Mini Envios), 3 (Jadlog), 31 (Loggi).
        payload = {
            "from": {"postal_code": from_postal},
            "to": {"postal_code": to_postal},
            "package": package,
            "services": "1, 2, 3, 31",
            "options": {
                "own_hand": False,
                "receipt": False,
                "insurance_value": 79
            }
        }

        await asyncio.sleep(REQUEST_DELAY)

        url = f"{self.base_url}/calculator"
        logger.info(f"POST {url}")
        logger.info(f"Body: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.info(f"Headers: {json.dumps(self.headers, indent=2, ensure_ascii=False)}")

        async with self._session.post(url, json=payload) as resp:
            if resp.status != 200:
                error_body = await _parse_error(resp)
                logger.error(f"Calculator error ({resp.status}):\n{error_body}")
                raise RuntimeError(f"Calculator failed ({resp.status}): {error_body}")

            data = await resp.json()

        services = data if isinstance(data, list) else data.get("data", [])

        return [
            s for s in services
            if s.get("id") not in EXCLUDED_SERVICE_IDS and s.get("price") is not None
        ]

    async def create_order(self, order_payload: dict) -> dict:
        """
        Creates a shipping order (without payment).
        """
        await asyncio.sleep(REQUEST_DELAY)

        url = f"{self.base_url}/cart"
        logger.info(f"POST {url}")
        logger.info(f"Body: {json.dumps(order_payload, indent=2, ensure_ascii=False)}")

        async with self._session.post(url, json=order_payload) as resp:
            if resp.status not in (200, 201):
                error_body = await _parse_error(resp)
                logger.error(f"Order creation error ({resp.status}):\n{error_body}")
                raise RuntimeError(f"Order creation failed ({resp.status}): {error_body}")

            return await resp.json()


async def _parse_error(resp: aiohttp.ClientResponse) -> str:
    """Returns the error body as a formatted JSON string if possible, otherwise raw text."""
    try:
        data = await resp.json(content_type=None)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        text = await resp.text()
        if text.strip().startswith("<"):
            return f"<HTML response — status {resp.status}>"
        return text