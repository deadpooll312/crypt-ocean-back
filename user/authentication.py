from rest_framework.authentication import TokenAuthentication as AbstractTokenAuthentication
from rest_framework import exceptions
from .models import AccessToken


class TokenAuthentication(AbstractTokenAuthentication):

    model = AccessToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User is not active')

        return token.user, token
