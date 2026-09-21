import unittest
from unittest import mock

from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.tests import util as test_util


class AuthenticatorTest(
    unittest.TestCase,
    dns_test_common.BaseAuthenticatorTest,
):
    def setUp(self):
        from certbot_dns_lightsail.authentication import Authenticator
        super().setUp()
        # boto3 requires a region and credentials to construct a client
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
        config = mock.MagicMock(dns_lightsail_propagation_seconds=0)
        self.auth = Authenticator(config, 'dns-lightsail')
        self.auth._client = mock.MagicMock()

    def tearDown(self):
        del os.environ['AWS_DEFAULT_REGION']
        del os.environ['AWS_ACCESS_KEY_ID']
        del os.environ['AWS_SECRET_ACCESS_KEY']
        super().tearDown()

    @test_util.patch_display_util()
    def test_perform(self, unused_mock_get_utility):
        self.auth.perform([self.achall])
        self.auth._client.create_txt_record.assert_called_once_with(
            dns_test_common.DOMAIN,
            self.achall.validation_domain_name(dns_test_common.DOMAIN),
            self.achall.validation(self.achall.account_key),
        )

    @test_util.patch_display_util()
    def test_perform_error(self, unused_mock_get_utility):
        self.auth._client.create_txt_record.side_effect = Exception('boom')
        with self.assertRaises(errors.PluginError):
            self.auth.perform([self.achall])

    def test_cleanup(self):
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])
        self.auth._client.delete_txt_record.assert_called_once_with(
            dns_test_common.DOMAIN,
            self.achall.validation_domain_name(dns_test_common.DOMAIN),
            self.achall.validation(self.achall.account_key),
        )

    def test_cleanup_error(self):
        self.auth._attempt_cleanup = True
        self.auth._client.delete_txt_record.side_effect = Exception('boom')
        # cleanup failures are logged, not raised
        with self.assertLogs(
            'certbot_dns_lightsail.authentication', level='ERROR',
        ) as cm:
            self.auth.cleanup([self.achall])
        self.assertIn('boom', cm.output[0])
