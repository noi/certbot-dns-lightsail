import unittest
from unittest import mock

from botocore.exceptions import ClientError

from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.tests import util as test_util


class AuthenticatorTest(
    test_util.TempDirTestCase,
    dns_test_common.BaseAuthenticatorTest,
):
    def setUp(self):
        from certbot_dns_lightsail.authentication import Authenticator
        super().setUp()
        patcher = mock.patch(
            'certbot_dns_lightsail.authentication._LightsailClient',
        )
        self.client_class = patcher.start()
        self.addCleanup(patcher.stop)
        config = mock.MagicMock(
            dns_lightsail_credentials=None,
            dns_lightsail_propagation_seconds=0,
            dns_lightsail_region='us-east-1',
        )
        self.auth = Authenticator(config, 'dns-lightsail')
        self.auth._client = self.client_class.return_value

    def write_credentials(self, values):
        path = os.path.join(self.tempdir, 'credentials.ini')
        dns_test_common.write(values, path)
        self.auth.config.dns_lightsail_credentials = path

    @test_util.patch_display_util()
    def test_perform_without_credentials(self, unused_mock_get_utility):
        self.auth.perform([self.achall])
        self.client_class.assert_called_once_with('us-east-1')

    @test_util.patch_display_util()
    def test_perform_with_credentials(self, unused_mock_get_utility):
        self.write_credentials({
            'dns_lightsail_aws_access_key_id': 'key-id',
            'dns_lightsail_aws_secret_access_key': 'secret',
        })
        self.auth.perform([self.achall])
        self.client_class.assert_called_once_with(
            'us-east-1', 'key-id', 'secret',
        )

    @test_util.patch_display_util()
    def test_perform_with_incomplete_credentials(
        self, unused_mock_get_utility,
    ):
        self.write_credentials({'dns_lightsail_aws_access_key_id': 'key-id'})
        with self.assertRaises(errors.PluginError):
            self.auth.perform([self.achall])
        self.client_class.assert_not_called()

    def test_region_default(self):
        add = mock.MagicMock()
        self.auth.add_parser_arguments(add)
        add.assert_any_call(
            'region', default='us-east-1', help=mock.ANY,
        )

    @test_util.patch_display_util()
    def test_region(self, unused_mock_get_utility):
        self.auth.config.dns_lightsail_region = 'us-west-2'
        self.auth.perform([self.achall])
        self.client_class.assert_called_once_with('us-west-2')

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


class LightsailClientTest(unittest.TestCase):
    def setUp(self):
        from certbot_dns_lightsail.authentication import _LightsailClient
        patcher = mock.patch('certbot_dns_lightsail.authentication.boto3')
        self.boto3 = patcher.start()
        self.addCleanup(patcher.stop)
        self.client = _LightsailClient('us-east-1')
        self.boto3_client = self.boto3.client.return_value
        self.set_domains([['example.com']])

    def set_domains(self, pages):
        paginator = self.boto3_client.get_paginator.return_value
        paginator.paginate.return_value = [
            {'domains': [{'name': name} for name in names]}
            for names in pages
        ]

    def test_default_credentials(self):
        self.boto3.client.assert_called_once_with(
            'lightsail',
            region_name='us-east-1',
            aws_access_key_id=None,
            aws_secret_access_key=None,
        )

    def test_explicit_credentials(self):
        from certbot_dns_lightsail.authentication import _LightsailClient
        _LightsailClient('us-east-1', 'key-id', 'secret')
        self.boto3.client.assert_called_with(
            'lightsail',
            region_name='us-east-1',
            aws_access_key_id='key-id',
            aws_secret_access_key='secret',
        )

    def assert_entry(self, method, domain_name):
        method.assert_called_once_with(
            domainName=domain_name,
            domainEntry={
                'type': 'TXT',
                'name': '_acme-challenge.sub.example.com',
                'target': '"value"',
            },
        )

    def test_create_txt_record(self):
        self.client.create_txt_record(
            'example.com', '_acme-challenge.example.com', 'value',
        )
        self.boto3_client.create_domain_entry.assert_called_once_with(
            domainName='example.com',
            domainEntry={
                'type': 'TXT',
                'name': '_acme-challenge.example.com',
                'target': '"value"',
            },
        )

    def test_create_txt_record_subdomain(self):
        self.client.create_txt_record(
            'sub.example.com', '_acme-challenge.sub.example.com', 'value',
        )
        self.assert_entry(self.boto3_client.create_domain_entry, 'example.com')

    def test_delete_txt_record_subdomain(self):
        self.client.delete_txt_record(
            'sub.example.com', '_acme-challenge.sub.example.com', 'value',
        )
        self.assert_entry(self.boto3_client.delete_domain_entry, 'example.com')

    def test_closest_domain_is_preferred(self):
        self.set_domains([['example.com', 'sub.example.com']])
        self.client.create_txt_record(
            'sub.example.com', '_acme-challenge.sub.example.com', 'value',
        )
        self.assert_entry(
            self.boto3_client.create_domain_entry, 'sub.example.com',
        )

    def test_domains_across_pages(self):
        self.set_domains([['example.org'], ['example.com']])
        self.client.create_txt_record(
            'sub.example.com', '_acme-challenge.sub.example.com', 'value',
        )
        self.assert_entry(self.boto3_client.create_domain_entry, 'example.com')

    def test_domain_not_found(self):
        self.set_domains([['example.org']])
        with self.assertRaises(errors.PluginError):
            self.client.create_txt_record(
                'sub.example.com', '_acme-challenge.sub.example.com', 'value',
            )
        self.boto3_client.create_domain_entry.assert_not_called()

    def test_list_domains_access_denied(self):
        paginator = self.boto3_client.get_paginator.return_value
        paginator.paginate.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException'}}, 'GetDomains',
        )
        with self.assertLogs(
            'certbot_dns_lightsail.authentication', level='WARNING',
        ):
            self.client.create_txt_record(
                'sub.example.com', '_acme-challenge.sub.example.com', 'value',
            )
        self.assert_entry(
            self.boto3_client.create_domain_entry, 'sub.example.com',
        )

    def test_list_domains_error(self):
        paginator = self.boto3_client.get_paginator.return_value
        paginator.paginate.side_effect = ClientError(
            {'Error': {'Code': 'ServiceException'}}, 'GetDomains',
        )
        with self.assertRaises(ClientError):
            self.client.create_txt_record(
                'sub.example.com', '_acme-challenge.sub.example.com', 'value',
            )
