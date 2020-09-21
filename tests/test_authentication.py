from unittest import TestCase
from certbot.compat import os
from certbot.plugins.dns_test_common import BaseAuthenticatorTest
from certbot_dns_lightsail.authentication import Authenticator

import sys
if sys.version_info[:2] >= (3, 3):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock


class AuthenticatorTest(TestCase, BaseAuthenticatorTest):
    def setUp(self):
        os.environ['AWS_DEFAULT_REGION'] = 'dummy'
        config = MagicMock()
        self.auth = Authenticator(config, 'dns-lightsail')
        self.auth._client = MagicMock()

    def test_perform(self):
        self.auth.perform([self.achall])
        self.auth._client.create_txt_record.assert_called_once()

    def test_cleanup(self):
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])
        self.auth._client.delete_txt_record.assert_called_once()
