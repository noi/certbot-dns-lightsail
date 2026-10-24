# Amazon Lightsail DNS Authenticator Plugin for Certbot
[![CI](https://github.com/noi/certbot-dns-lightsail/actions/workflows/ci.yml/badge.svg)](https://github.com/noi/certbot-dns-lightsail/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/certbot-dns-lightsail)](https://pypi.org/project/certbot-dns-lightsail/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/certbot-dns-lightsail)](https://pypi.org/project/certbot-dns-lightsail/)
[![GitHub - License](https://img.shields.io/github/license/noi/certbot-dns-lightsail)](https://github.com/noi/certbot-dns-lightsail/blob/main/LICENSE)

This plugin proves you have control over a domain by DNS-01 challenge to the Amazon Lightsail DNS.

## Additional Arguments for Certbot
- `--authenticator dns-lightsail`
  - Use this plugin as an authenticator. (required)
- `--dns-lightsail-propagation-seconds ${value}`
  - The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record. (default: 60, The default TTL for Amazon Lightsail DNS records is 60 seconds so I recommend to set a value greater than it)
- `--dns-lightsail-credentials ${path}`
  - Path to an INI file with AWS credentials. (optional, If omitted, credentials are looked up in the [boto3 default way](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html) such as environment variables and `~/.aws/credentials`)

## Getting Started
### Requirements
- Python 3.10 or later
- Certbot 5.0.0 or later

### Installation
Install this plugin using `pip` into the same Python environment as Certbot:
```
pip install certbot-dns-lightsail
```

This plugin is not available as a snap, so Certbot installed with `snap` cannot find it.
Instead, install Certbot and this plugin together into a virtual environment, as described in [Certbot's pip instructions](https://certbot.eff.org/instructions?ws=other&os=pip):
```sh
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-dns-lightsail
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
```
If Certbot is already installed with `snap`, remove it first with `sudo snap remove certbot`.

### Usage
This plugin requires AWS credential settings before it can be used.

It calls Lightsail DNS APIs in `us-east-1`, where they are available, regardless of the region in your AWS settings. Use `--dns-lightsail-region` to change it.

#### 1. Create Access Key
Create an access key using IAM policy below:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:CreateDomainEntry",
                "lightsail:DeleteDomainEntry"
            ],
            "Resource": "arn:aws:lightsail:us-east-1:${YOUR-ACCOUNT-ID}:Domain/${YOUR-DOMAIN-ID}"
        },
        {
            "Effect": "Allow",
            "Action": "lightsail:GetDomains",
            "Resource": "*"
        }
    ]
}
```

`lightsail:GetDomains` is used to find the Lightsail domain that contains each requested name (e.g. `example.com` for `sub.example.com`). Without it, each requested name itself must be a Lightsail domain.

#### 2. Create Credentials File
Create a credentials file below:
```ini
# /etc/letsencrypt/lightsail.ini
dns_lightsail_aws_access_key_id = ${YOUR-ACCESS-KEY-ID}
dns_lightsail_aws_secret_access_key = ${YOUR-SECRET-ACCESS-KEY}
```

Restrict its permissions so that other users cannot read it:
```sh
sudo chmod 600 /etc/letsencrypt/lightsail.ini
```

Alternatively, omit `--dns-lightsail-credentials` and configure credentials in any way boto3 supports, such as `~/.aws/credentials` or environment variables:
```ini
# ~/.aws/credentials
[default]
aws_access_key_id=${YOUR-ACCESS-KEY-ID}
aws_secret_access_key=${YOUR-SECRET-ACCESS-KEY}
```

#### 3. Run Certbot
You are ready to run this plugin with Certbot!

For example, run command below to obtain a certificate using this plugin:
```sh
certbot certonly \
  --authenticator dns-lightsail \
  --dns-lightsail-credentials /etc/letsencrypt/lightsail.ini \
  --dns-lightsail-propagation-seconds 70 \
  --non-interactive \
  --agree-tos \
  -m 'mail@example.com' \
  -d 'example.com' \
  -d '*.example.com'
```
