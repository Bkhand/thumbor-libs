# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
import base64
import hashlib
import hmac
from thumbor.url_signers import BaseUrlSigner
#from thumbor.utils import deprecated, logger


class UrlSigner(BaseUrlSigner):

    def signature(self, url):
        oas= base64.urlsafe_b64encode(
            hmac.new(
                self.security_key, str(url).encode('utf-8'), hashlib.sha1
            ).digest()
        )
        oad = oas.decode('utf8').replace('=', '').encode()
        return oad
