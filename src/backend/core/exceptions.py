from rest_framework import status


class BusinessLogicError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, code: str = "business_error", **kwargs):
        self.code = code
        self.kwargs = kwargs
        super().__init__(code)


class AccessDeniedError(BusinessLogicError):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, code: str = "access_denied", **kwargs):
        super().__init__(code, **kwargs)


class NotFoundError(BusinessLogicError):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, code: str = "not_found", **kwargs):
        super().__init__(code, **kwargs)


class BusinessValidationError(BusinessLogicError):

    def __init__(self, code: str = "validation_error", lang: str = 'uz', **kwargs):
        super().__init__(code, **kwargs)


class AuthError(BusinessLogicError):
    """Raised for all authentication business-logic failures."""

    def __init__(self, code: str, lang: str = 'uz', status_code: int = 400, **format_kwargs):
        self.lang = lang
        self.status_code = status_code

        from src.backend.core.i18n import get_error_message
        self.message = get_error_message(code, lang, **format_kwargs)

        super().__init__(code=code, **format_kwargs)