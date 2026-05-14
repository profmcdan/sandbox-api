from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Fully flat error response:
    - errorField/errorMessage for the first error
    - responseBody for all errors flattened
    """
    # Get default DRF response first
    response = exception_handler(exc, context)

    if response is not None:
        # Initialize flat_errors dict
        flat_errors = {}

        # DRF ValidationError can be nested dicts or lists
        if isinstance(response.data, dict):

            def flatten(d, parent_key=""):
                items = {}
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.update(flatten(v, new_key))
                    elif isinstance(v, list):
                        items[new_key] = v[0]  # pick first error
                    else:
                        items[new_key] = str(v)
                return items

            flat_errors = flatten(response.data)
        else:
            flat_errors = {"error": str(response.data)}

        # Pick first error
        first_field, first_message = next(iter(flat_errors.items()))

        # Return fully flat Response
        return Response(
            {
                "responseCode": "07",
                "errorField": first_field,
                "responseMessage": first_message,
                "responseBody": flat_errors,
            },
            status=response.status_code,
        )

    # fallback
    return response
