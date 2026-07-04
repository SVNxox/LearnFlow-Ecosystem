from drf_spectacular.extensions import OpenApiAuthenticationExtension

class CustomJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'src.backend.identity.authentication.JWTAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }