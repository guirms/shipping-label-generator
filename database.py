import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def fetch_orders() -> list[dict]:
    """
    Lê todos os pedidos da tabela orders e retorna uma lista de dicionários.
    """
    db_server = os.getenv("DB_SERVER")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")

    if not all([db_server, db_name, db_user, db_pass]):
        raise EnvironmentError(
            "DB_SERVER, DB_NAME, DB_USER e DB_PASS devem estar definidos no .env."
        )

    conn = await asyncpg.connect(
        host=db_server,
        port=int(db_port),
        database=db_name,
        user=db_user,
        password=db_pass,
    )
    try:
        # Ajuste o nome da tabela e colunas conforme necessário.
        query = """
            select s."Id" as "order_id",
                u."Name" as "customer_name",
                u."Phone" as "customer_phone",
                u."Email" as "customer_email",
                u."Cpf" as "customer_document",
                a."ZipCode" as "postal_code",
                a."State" as "state",
                a."Street" as "address",
                a."HouseNumber" as "number",
                a."Extra" as "complement",
                a."Neighborhood" as "district",
                a."City" as "city",
                k."Name" as "product_name",
                1 as "product_quantity",
                k."Price" as "product_value"
                from "Subscriptions" s 
                join "Users" u on u."Id" = s."UserId"
                join "Addressess" a on a."Id" = u."AddressId"
                join "Payments" p on p."Id" = s."PaymentId"
                join "Kits" k on k."Id" = s."KitId" 
                where s."CreatedAt" > '2026-03-10' and p."Status"=1
                limit 1;
        """
        records = await conn.fetch(query)
        orders = [dict(record) for record in records]
        return orders
    finally:
        await conn.close()