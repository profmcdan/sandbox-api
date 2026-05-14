from datetime import date, datetime, time

from cuid2 import Cuid
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import make_aware
from uuid6 import uuid7

CUID_GENERATOR: Cuid = Cuid(length=24)


def generate_unique_id() -> str:
    return CUID_GENERATOR.generate()


def generate_wallet_code(length=8) -> str:
    generator: Cuid = Cuid(length=length)
    return generator.generate().upper()


def generate_reference_code(length=14, prefix=None) -> str:
    generator: Cuid = Cuid(length=length)
    code = generator.generate().upper()
    if prefix:
        return f"{prefix}{code}"
    return code


def generate_uuid() -> str:
    return str(uuid7()).upper().replace("-", "").lower()


def format_money(amount):
    """Convert amount from kobo to naira and format it with commas and 2 decimal places."""
    if amount is None or not amount:
        return "₦0.00"
    if isinstance(amount, str):
        amount = amount.strip()
        if amount.lower() in ("null", "none", "undefined", "nan", "inf", ""):
            return "₦0.00"

    naira_value = float(amount)
    # Format with commas and two decimal places
    return f"{naira_value:,.2f}"


def safe_float(value):
    """Safely convert a value to float, handling invalid strings like 'Null'."""
    if not value:
        return 0.0
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ("null", "none", "undefined", "nan", "inf", ""):
            return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def normalize_to_aware_datetime(value, is_end=False):
    if isinstance(value, str):
        parsed = parse_date(value) or parse_datetime(value)
        if parsed:
            if isinstance(parsed, datetime):
                return make_aware(parsed)
            return make_aware(
                datetime.combine(parsed, time.max if is_end else time.min)
            )
    return value


def generate_12_digit_reference():
    """
    1. Generate UUIDv7
    2. Convert to integer
    3. Reduce to 12-digit numeric reference
    """
    # u = uuid7()
    # i = u.int
    # ref = str(i % 10**12).zfill(12)
    return str(uuid7().int % 10**12).zfill(12)


def parse_bool_or_none(value, field_name="field"):
    if value in [None, ""]:
        return None

    if isinstance(value, str):
        value = value.lower()

    if value == "true":
        return True
    if value == "false":
        return False
    if value is True:
        return True

    if value is False:
        return False

    return None


def schedule_task(
    instance,
    task_func,
    expires_at,
):
    # Convert date → datetime (end of day)

    if isinstance(expires_at, date) and not isinstance(expires_at, datetime):
        expires_at = datetime.combine(expires_at, time(23, 59, 59))
    # Ensure timezone-aware (Django standard)
    if timezone.is_naive(expires_at):
        expires_at = timezone.make_aware(expires_at)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    # Prevent scheduling in the past
    if expires_at <= timezone.now():
        return None

    # Guard: don't schedule if ETA is already in the past
    task = task_func.apply_async(args=[instance.id], eta=expires_at)
    instance.task_id = task.id
    instance.save(update_fields=["task_id"])
    return task.id


def virtualAccountProvider(bank_code=None):
    if bank_code and bank_code in ["103"]:
        return "globus"
    return None
