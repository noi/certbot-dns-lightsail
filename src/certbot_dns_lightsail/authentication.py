import logging
from typing import Callable
from typing import Optional

import boto3

from botocore.exceptions import ClientError

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
        self.credentials: Optional[dns_common.CredentialsConfiguration] = None
        self._client: Optional[_LightsailClient] = None

    @classmethod
    def add_parser_arguments(
        cls,
        add: Callable[..., None],
        default_propagation_seconds: int = 60,
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        # Lightsail DNS APIs are only available in us-east-1, so the default
        # takes precedence over the region in the user's AWS settings
        add(
            'region',
            default='us-east-1',
            help='AWS region for Lightsail DNS APIs.',
        )
        add(
            'credentials',
            help='Path to an INI file with AWS credentials. If omitted, '
            'credentials are looked up as boto3 does by default '
            '(environment variables, ~/.aws/credentials, etc.).',
        )

    def more_info(self) -> str:
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
        # the credentials file is optional; do not prompt for it
        if self.conf('credentials'):
            self.credentials = self._configure_credentials(
                'credentials',
                'AWS credentials INI file',
                {
                    'aws_access_key_id': 'AWS access key ID',
                    'aws_secret_access_key': 'AWS secret access key',
                },
            )
        self._client = self._get_lightsail_client()

    def _get_lightsail_client(self) -> '_LightsailClient':
        if self.credentials is None:
            return _LightsailClient(self.conf('region'))
        return _LightsailClient(
            self.conf('region'),
            self.credentials.conf('aws_access_key_id'),
            self.credentials.conf('aws_secret_access_key'),
        )


class _LightsailClient:
    def __init__(
        self,
        region_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ) -> None:
        # boto3 falls back to its default credential chain for None
        self._client = boto3.client(
            'lightsail',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def create_txt_record(self, domain: str, name: str, value: str) -> None:
        self._client.create_domain_entry(
            domainName=self._find_domain_name(domain),
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': f'"{value}"',
            },
        )

    def delete_txt_record(self, domain: str, name: str, value: str) -> None:
        self._client.delete_domain_entry(
            domainName=self._find_domain_name(domain),
            domainEntry={
                'type': 'TXT',
                'name': name,
                'target': f'"{value}"',
            },
        )

    def _find_domain_name(self, domain: str) -> str:
        # the closest enclosing Lightsail domain (DNS zone) of the given name
        domain_names = set()
        paginator = self._client.get_paginator('get_domains')
        try:
            for page in paginator.paginate():
                domain_names.update(d['name'] for d in page['domains'])
        except ClientError as e:
            if e.response['Error']['Code'] != 'AccessDeniedException':
                raise
            # keep working with policies that predate lightsail:GetDomains
            logger.warning(
                'Not allowed to list Lightsail domains; using %s as is. '
                'Allow lightsail:GetDomains to use subdomains.', domain,
            )
            return domain

        for guess in dns_common.base_domain_name_guesses(domain):
            if guess in domain_names:
                return guess

        raise errors.PluginError(
            f'Unable to find a Lightsail domain for {domain}'
        )
