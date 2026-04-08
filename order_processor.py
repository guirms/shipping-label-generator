import asyncio
import logging
import json
from api_client import SuperfreteClient

logger = logging.getLogger(__name__)

ORIGIN_POSTAL_CODE = "88804600"
RESPONSES_FILE = "superfrete_responses.txt"
_file_write_lock = asyncio.Lock()

PACKAGE = {
    "height": 5,
    "width": 20,
    "length": 30,
    "weight": 0.3,
}

# Max concurrent requests to avoid rate limiting
CONCURRENCY_LIMIT = 5

def build_order_payload(order: dict, service: dict) -> dict:
    return {
        "service": service["id"],
        "from": {
            "name": "Endura Run",
            "address": "Rua Imigrante de Lucca, 855",
            "complement": "Casa",
            "number": "855",
            "district": "Pinheirinho",
            "city": "Criciúma",
            "state_abbr": "SC",
            "postal_code": ORIGIN_POSTAL_CODE,
        },
        "to": {
            "name": order["recipient_name"],
            "phone": order["recipient_phone"],
            "email": order["recipient_email"],
            "document": order["recipient_document"],
            "address": order["address"],
            "complement": order.get("complement", ""),
            "number": order["number"],
            "district": order["district"],
            "city": order["city"],
            "state_abbr": order["state"],
            "postal_code": order["postal_code"],
            "country_id": "BR",
        },
        "products": [
            {
                "name": order.get("product_name", "Produto"),
                "quantity": order.get("product_quantity", 1),
                "unitary_value": order.get("product_value", 1.00),
            }
        ],
        "volumes": PACKAGE,
        "options": {
            "own_hand": False,
            "receipt": False,
            "insurance_value": order.get("product_value", 1.00),
            "non_commercial": True
        },
        "platform": "Endura Run"
    }


async def process_order(client: SuperfreteClient, order: dict, semaphore: asyncio.Semaphore) -> dict:
    order_id = order["order_id"]

    async with semaphore:
        try:
            logger.info(f"[{order_id}] Fetching shipping rates for CEP {order['postal_code']}...")
            services = await client.get_shipping_rates(
                from_postal=ORIGIN_POSTAL_CODE,
                to_postal=order["postal_code"],
                package=PACKAGE,
            )

            if not services:
                raise RuntimeError("No available services returned from calculator.")

            cheapest = min(services, key=lambda s: float(s["price"]))
            logger.info(
                f"[{order_id}] Cheapest service: {cheapest.get('name', cheapest['id'])} "
                f"@ R${cheapest['price']}"
            )

            order_payload = build_order_payload(order, cheapest)
            result = await client.create_order(order_payload)

            logger.info(f"[{order_id}] Order created successfully. Response ID: {result.get('id', '?')}")
            
            formatted = json.dumps(result, ensure_ascii=False, indent=2)
            separator = "\n" + "=" * 40 + "\n"
            async with _file_write_lock:
                with open(RESPONSES_FILE, "a", encoding="utf-8") as f:
                    f.write(formatted)
                    f.write(separator)
                    
            return {"order_id": order_id, "status": "success", "result": result}

        except Exception as e:
            logger.error(f"[{order_id}] Error: {e}")
            return {"order_id": order_id, "status": "error", "error": str(e)}


async def process_all_orders(client: SuperfreteClient, orders: list[dict]) -> list[dict]:
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = [process_order(client, order, semaphore) for order in orders]
    return await asyncio.gather(*tasks)
