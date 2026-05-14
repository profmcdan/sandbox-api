import logging
import re
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

import httpx
from common.audtilog.contrib import get_client_ip
from core import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


def get_validated_date_range(request, start_key="start", end_key="end", max_days=61):
    """
    Parse and validate start/end dates from query params.

    Args:
        request: DRF request object
        start_key (str): name of start date param
        end_key (str): name of end date param
        max_days (int): max allowed range (default: 61 days)

    Returns:
        (start_date, end_date) as datetime.date objects
    """

    start_date_str = request.query_params.get(start_key)
    end_date_str = request.query_params.get(end_key)

    # Default start = today
    if not start_date_str:
        start_date = date.today()
    else:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

    # Default end = start
    if not end_date_str:
        end_date = start_date
    else:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    # Validation rules
    if end_date < start_date:
        raise ValidationError(
            {"date_order": "End date cannot be earlier than start date."}
        )

    if end_date - start_date > timedelta(days=max_days):
        raise ValidationError(
            {"date_range": f"Date range should not be greater than {max_days} days."}
        )

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def fmt_dt_to_lagos(dt_val, format_string="%d-%b-%Y %H:%M:%S"):
    """Format datetime to Lagos timezone (WAT, UTC+1). Returns '' if dt_val is None."""
    if not dt_val:
        return ""
    nigeria_tz = timezone.get_fixed_timezone(60)
    return dt_val.astimezone(nigeria_tz).strftime(format_string)


def clean_phone_number(phone: str) -> str:
    """
    Clean and validate Nigerian phone numbers.

    Supports formats:
    - 07012345678 (11 digits starting with 0)
    - 2347012345678 (with country code)
    - +2347012345678 (with + prefix)
    - 7012345678 (10 digits, will be prefixed with 0)

    Validates against Nigerian network prefixes:
    - 0701-0709 (MTN)
    - 0802-0809 (Airtel, Glo, 9mobile)
    - 0810-0819 (MTN, Glo, 9mobile)
    - 0901-0909 (Airtel, MTN, 9mobile)
    - 0910-0919 (MTN, Glo)

    Args:
        phone: Phone number string in various formats

    Returns:
        Cleaned phone number in format: 0XXXXXXXXXX (11 digits)

    Raises:
        ValidationError: If phone number is invalid
    """
    phone = str(phone).strip().replace(" ", "")

    if phone.startswith("+"):
        phone = phone[1:]

    pattern = r"^0(70[1-9]|80[2-9]|81[0-9]|90[1-9]|91[0-9]|91[1-9])$"

    if len(phone) == 10 and phone.isdigit():
        phone = "0" + phone

    if phone.startswith("234"):
        phone = "0" + phone[3:]

    if not phone.isdigit() or len(phone) != 11:
        raise ValidationError({"phone": f"Phone number '{phone}' should be 11 digits"})

    first_4_xters = phone[:4]
    if re.match(pattern, first_4_xters) is None:
        raise ValidationError({"phone": f"Phone number '{phone}' is invalid"})

    return phone


def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from]
    )
    msg.attach_alternative(html_alternative, "text/html")
    msg.send()


def get_name(user) -> str:
    """User display name for audit logs."""
    if not user:
        return ""
    return (
        f"{getattr(user, 'firstname', '')} {getattr(user, 'lastname', '')}".strip()
        or getattr(user, "email", "")
        or str(user.id)
    )


def get_location_from_ip(ip: str) -> dict | None:
    """
    Fetch geolocation info for a given public IP via ipinfo.io.
    Returns None for private/empty IPs or on failure.
    """
    if not ip:
        return None

    if settings.DEBUG and ip in ("192.168.65.1", "127.0.0.1", "::1"):
        test_ip = getattr(settings, "DEV_TEST_IP", None)
        if test_ip:
            ip = test_ip

    # Skip private/loopback addresses — ipinfo.io can't resolve them
    private_prefixes = ("127.", "10.", "192.168.", "172.", "::1", "localhost")
    if any(ip.startswith(p) for p in private_prefixes):
        return None

    try:
        r = httpx.get(f"https://ipinfo.io/{ip}/json", timeout=15.0)

        if r.status_code != 200:
            logger.warning(f"ipinfo.io returned non-200: {r.status_code}")
            return None

        data = r.json()
        logger.info(f"ipinfo.io data: {data}")

        if data.get("bogon"):
            logger.info(f"IP {ip} flagged as bogon by ipinfo.io")
            return None

        return {
            "country": data.get("country"),
            "region": data.get("region"),
            "city": data.get("city"),
        }

    except httpx.TimeoutException:
        logger.error(f"Timeout fetching geolocation for IP: {ip}")
        return None
    except Exception as ex:
        logger.error(f"Error fetching geolocation for IP {ip}: {ex}")
        return None


def format_location(location_dict: dict | None) -> str | None:
    """
    Format a location dict into a readable string: "City, Region, Country"
    """
    if not location_dict:
        return None

    parts = [
        location_dict.get("city"),
        location_dict.get("region"),
        location_dict.get("country"),
    ]

    formatted = ", ".join(p for p in parts if p)
    return formatted or None


def sanitize_data(data):
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


def get_user_type(user) -> str:
    return (getattr(user, "role", "") or "").strip() if user else ""


def log_audit(
    request,
    audit_type: str,
    action: str,
    status: str,
    user=None,
    location: str = None,
    log_data: dict = None,
):
    """Log an audit event with IP resolution and geolocation."""
    from config.tasks import submit_audit_log_task

    client_ip = get_client_ip(request)
    first_name = getattr(user, "firstname", "-")
    last_name = getattr(user, "lastname", "-")
    email = getattr(user, "email", "-")
    role = getattr(user, "role", "-")
    user_id = getattr(user, "id", "-")
    user_data = {
        "user_id": user_id,
        "user_name": f"{first_name} {last_name}",
        "user_email": email,
        "user_role": role,
    }
    submit_audit_log_task.delay(
        user_data, action, status, audit_type, client_ip, log_data
    )


def calculate_percentage(value, total):
    if not total:
        return Decimal("0.00")
    return (Decimal(value) / Decimal(total) * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
