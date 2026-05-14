from common.kgs import generate_uuid


def generate_transaction_reference() -> str:
    uuid_part = generate_uuid()[:13]
    reference = f"ER|{uuid_part}"

    return reference
