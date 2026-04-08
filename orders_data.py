"""
Hardcoded orders for testing. Replace this list with a DB query when ready.

Each order must contain:
  - order_id         (str)  : unique identifier
  - recipient_name   (str)
  - recipient_phone  (str)
  - recipient_email  (str)
  - recipient_document (str): CPF or CNPJ
  - postal_code      (str)
  - address          (str)
  - number           (str)
  - complement       (str, optional)
  - district         (str)
  - city             (str)
  - state            (str)  : 2-letter abbreviation e.g. "SP"
  - product_name     (str)
  - product_quantity (int)
  - product_value    (float): declared value for insurance
  - invoice_key      (str, optional)
"""

ORDERS = [
    {
        "order_id": "ORD-001",
        "recipient_name": "Deu2 bom da Silva",
        "recipient_phone": "11999990001",
        "recipient_email": "joao.silva@email.com",
        "recipient_document": "12345678901",
        "postal_code": "01310100",
        "address": "Avenida Paulista",
        "number": "1578",
        "complement": "Apto 42",
        "district": "Bela Vista",
        "city": "São Paulo",
        "state": "SP",
        "product_name": "Produto A",
        "product_quantity": 1,
        "product_value": 50.00,
    }
    # {
    #     "order_id": "ORD-002",
    #     "recipient_name": "Maria Souza",
    #     "recipient_phone": "21988880002",
    #     "recipient_email": "maria.souza@email.com",
    #     "recipient_document": "98765432100",
    #     "postal_code": "20040020",
    #     "address": "Rua da Assembleia",
    #     "number": "10",
    #     "complement": "",
    #     "district": "Centro",
    #     "city": "Rio de Janeiro",
    #     "state": "RJ",
    #     "product_name": "Produto B",
    #     "product_quantity": 2,
    #     "product_value": 80.00,
    # },
    # {
    #     "order_id": "ORD-003",
    #     "recipient_name": "Carlos Oliveira",
    #     "recipient_phone": "31977770003",
    #     "recipient_email": "carlos.oliveira@email.com",
    #     "recipient_document": "11122233344",
    #     "postal_code": "30112010",
    #     "address": "Avenida Afonso Pena",
    #     "number": "1500",
    #     "complement": "Sala 301",
    #     "district": "Centro",
    #     "city": "Belo Horizonte",
    #     "state": "MG",
    #     "product_name": "Produto C",
    #     "product_quantity": 1,
    #     "product_value": 120.00,
    # },
    # ─── Add remaining orders below (up to 77 total) ───────────────────────────
]
