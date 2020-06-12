import datetime
import hashlib
import hmac

from BefreeBingo import settings


class BitchangeUtilsMixin:
    shop_id = settings.BITCHANGE_CONFIG.get('SHOP_ID', 'BlqWarhVLHmqA8DdPoZNK00xebYNDf')
    shop_secret = settings.BITCHANGE_CONFIG.get('SHOP_SECRET', 'KSvP4AwZG5tYWf1wWuw0meL3QAdJOp')

    def get_bitchange_auth_headers(self):
        nonce = datetime.datetime.now().microsecond

        sign_str = f'{nonce}|{self.shop_id}|{self.shop_secret}'
        sign = hmac.new(self.shop_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

        return {
            'C-Request-Nonce': f'{nonce}',
            'C-Request-Signature': sign,
            'C-Shop-Id': self.shop_id,
        }
