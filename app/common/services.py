import json

import requests
from django.conf import settings


def get_auth_token(request=None):
    if request is None:
        return {}
    if isinstance(request, dict):
        auth_token = request["headers"]["Authorization"]
    else:
        auth_token = request.headers.get("Authorization")
    auth_token = (
        auth_token.split()[1] if auth_token and "Bearer" in auth_token else auth_token
    )
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


def validate_kms_key(request, kms_key):
    kms_base_api = settings.ATHENA_KMS_BASE_API
    payload = {
        "project_id": "0a9314b8-62d3-4b86-bef3-027e9f930350",
        "ip_address": "102.89.33.63",
        "key": kms_key,
    }
    # headers = get_auth_token(request)
    response = requests.post(
        f"{kms_base_api}/projects/validate-key/", data=json.dumps(payload, indent=4)
    )
    if response.status_code == 200:
        return True
    return False
