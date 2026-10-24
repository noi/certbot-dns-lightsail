# Changelog
Versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-10-24
### Added
- Option `--dns-lightsail-region` (default: `us-east-1`); the region in AWS settings is no longer required nor used ([#1](https://github.com/noi/certbot-dns-lightsail/issues/1))
- Option `--dns-lightsail-credentials` to read AWS credentials from an INI file (`dns_lightsail_aws_access_key_id`, `dns_lightsail_aws_secret_access_key`); without it, credentials are looked up as before ([#2](https://github.com/noi/certbot-dns-lightsail/issues/2))

### Fixed
- Support subdomains of a Lightsail domain (e.g. `sub.example.com` in the `example.com` domain); this requires the `lightsail:GetDomains` permission ([#3](https://github.com/noi/certbot-dns-lightsail/issues/3))

### Security
- Require urllib3 2.5.0 or later to exclude versions affected by CVE-2025-50181 (urllib3 is a transitive dependency via boto3/botocore and requests)

## [0.2.0] - 2026-10-24
### Changed
- Support Certbot 5.x (`certbot>=5.0.0,<6`, `acme>=5.0.0,<6`); the previous release was pinned to `certbot==1.8.0`
- Require Python 3.10 or later
- Require boto3 1.40.0 or later

### Removed
- Support for Python 2.7 and Python 3.6 - 3.9
- Dependency on `zope.interface` (Certbot no longer uses it for plugin interfaces)

## [0.1.0] - 2020-10-13
### Added
- Authenticator `dns-lightsail` (`--authenticator dns-lightsail`)
- Option `--dns-lightsail-propagation-seconds` (default: 60)

[0.3.0]: https://pypi.org/project/certbot-dns-lightsail/0.3.0/
[0.2.0]: https://pypi.org/project/certbot-dns-lightsail/0.2.0/
[0.1.0]: https://pypi.org/project/certbot-dns-lightsail/0.1.0/
