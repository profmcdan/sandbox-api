import requests
from common.kgs import generate_unique_id
from django.conf import settings
from wallet.models import SMSUsage


def clean_phone(phone: str):
    if phone.startswith("+"):
        return phone[1:]
    return phone


def send_vanso_sms(recipient, message, purpose=None, user=None):
    url = "https://sms.vanso.com/rest/sms/submit"
    reference_id = generate_unique_id()
    payload = {
        "account": {
            "password": settings.VANSO_PASSWORD,
            "systemId": settings.VANSO_SYSID,
        },
        "sms": {
            "dest": clean_phone(recipient),
            "referenceId": reference_id,
            "src": settings.VANSO_SENDER,
            "text": message,
            "unicode": False,
        },
    }
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        log_sms(recipient, message, reference_id, purpose, user)

    return response


def log_sms(recipient, message, reference_id, purpose, user):
    url = "https://sms.vanso.com/rest/sms/dlr"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "password": settings.VANSO_PASSWORD,
        "referenceId": reference_id,
        "systemId": settings.VANSO_SYSID,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response_data = response.json()

        if "dlrs" in response_data:
            sms_data = {
                "user_id": user,
                "phone_number": recipient,
                "message": message,
                "purpose": purpose if purpose else "Transaction",
                "delivery_status": response_data["dlrs"][0]["status"].capitalize(),
                "reference": reference_id,
            }
            SMSUsage.objects.create(**sms_data)

    return response
