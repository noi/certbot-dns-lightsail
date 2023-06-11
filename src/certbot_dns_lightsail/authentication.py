import boto3
import logging
import typing

from certbot import configuration
from certbot import errors
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    description = 'This plugin proves you have control over a domain ' \
        'by DNS-01 challenge to the Amazon Lightsail DNS.'

    def __init__(
        self,
        config: configuration.NamespaceConfig,
        name: str,
    ) -> None:
        super().__init__(config, name)
        self._client = _LightsailClient()

    @classmethod
    def add_parser_arguments(
        cls,
        add: typing.Callable[..., None],
        default_propagation_seconds: int = 60,
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)

    def more_info(self):
        return self.description

    def _perform(
        self,
        domain: str,
        validation_domain_name: str,
        validation: str,
    ) -> None:
        try:
            self._client.create_txt_record(
                domain,
                validation_domain_name,
                validation,
            )
        except Exception as e:
            raise errors.PluginError(
                f'Failed to create TXT record ({validation_domain_name}): {e}'
            )

    def _cleanup(
        self,
        domain: str,
        validation_domain_name: str,
        validation: str,
    ) -> None:
        try:
            self._client.delete_txt_record(
                domain,
                validation_domain_name,
                validation,
            )
        except Exception as e:
            logger.error(
                f'Failed to delete TXT record ({validation_domain_name}): {e}'
            )

    def _setup_credentials(self) -> None:
        pass


class _LightsailClient:
    def __init__(self) -> None:
        self._client = boto3.client('lightsail')

    def create_txt_record(self, domain: str, name: str, value: str) -> None:
        self._client.create_domain_entry(
            domainName=domain,
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': f'"{value}"',
            },
        )

    def delete_txt_record(self, domain: str, name: str, value: str) -> None:
        self._client.delete_domain_entry(
            domainName=domain,
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': f'"{value}"',
            },
        )
