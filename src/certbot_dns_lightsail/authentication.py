import logging

import boto3

from certbot.errors import PluginError
from certbot.interfaces import IAuthenticator
from certbot.interfaces import IPluginFactory
from certbot.plugins.dns_common import DNSAuthenticator

import zope.interface

logger = logging.getLogger(__name__)


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class Authenticator(DNSAuthenticator):
    description = 'This plugin proves you have control over a domain ' \
        'by DNS-01 challenge to the Amazon Lightsail DNS.'

    def __init__(self, config, name):
        super(Authenticator, self).__init__(config, name)
        self._client = _LightsailClient()

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=60)

    def more_info(self):
        return self.description

    def _perform(self, domain, validation_domain_name, validation):
        try:
            self._client.create_txt_record(
                domain, validation_domain_name, validation)
        except Exception as e:
            raise PluginError(
                'Failed to create TXT record ({}): {}'.format(
                    validation_domain_name, e))

    def _cleanup(self, domain, validation_domain_name, validation):
        try:
            self._client.delete_txt_record(
                domain, validation_domain_name, validation)
        except Exception as e:
            logger.error(
                'Failed to delete TXT record ({}): {}'.format(
                    validation_domain_name, e))

    def _setup_credentials(self):
        pass


class _LightsailClient:
    def __init__(self):
        self._client = boto3.client('lightsail')

    def create_txt_record(self, domain, name, value):
        self._client.create_domain_entry(
            domainName=domain,
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': '"{}"'.format(value)
            }
        )

    def delete_txt_record(self, domain, name, value):
        self._client.delete_domain_entry(
            domainName=domain,
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': '"{}"'.format(value)
            }
        )
