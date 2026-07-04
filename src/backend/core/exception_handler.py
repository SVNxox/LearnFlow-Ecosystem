from rest_framework.views import exception_handler
from rest_framework.response import Response
from .exceptions import BusinessLogicError

from src.backend.core.i18n import get_error_message, get_language_from_request


def custom_exception_handler(exc, context):
    """
    Глобальный обработчик исключений для DRF.
    """
    if isinstance(exc, BusinessLogicError):
        request = context.get('request')
        lang = get_language_from_request(request)

        translated_message = get_error_message(exc.code, lang, **exc.kwargs)

        return Response(
            data={
                "code": exc.code,
                "detail": translated_message
            },
            status=exc.status_code
        )

    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, 'get_codes'):
            response.data = {
                "code": "validation_error",
                "detail": response.data,
                "field_codes": exc.get_codes()
            }
        else:
            if not isinstance(response.data, dict):
                response.data = {"detail": response.data, "code": "api_error"}
            else:
                response.data.setdefault('code', 'api_error')

    return response