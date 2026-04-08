import os
import asyncio
import logging
from api_client import SuperfreteClient
from order_processor import process_all_orders
from orders_data import ORDERS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

API_TOKEN = "Bearer " + os.getenv("SUPERFRETE_API_TOKEN")
BASE_URL = "https://api.superfrete.com/api/v0"

async def main():
    logger.info(f"Starting Superfrete automation for {len(ORDERS)} orders...")

    async with SuperfreteClient(API_TOKEN, BASE_URL) as client:
        results = await process_all_orders(client, ORDERS)

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    logger.info(f"Done. {len(successful)} orders placed, {len(failed)} failed.")

    if failed:
        logger.warning("Failed orders:")
        for f in failed:
            logger.warning(f"  Order {f['order_id']}: {f['error']}")


if __name__ == "__main__":
    asyncio.run(main())
