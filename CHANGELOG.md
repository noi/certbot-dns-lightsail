# Changelog
Versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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

[Unreleased]: https://github.com/noi/certbot-dns-lightsail/compare/v0.1.0...HEAD
[0.1.0]: https://pypi.org/project/certbot-dns-lightsail/0.1.0/
