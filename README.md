# Amazon Lightsail DNS Authenticator Plugin for Certbot
This plugin proves you have control over a domain by DNS-01 challenge to the Amazon Lightsail DNS.

## Additional Arguments for Certbot
- `--authenticator dns-lightsail`
  - Use this plugin as an authenticator. (required)
- `--dns-lightsail-propagation-seconds ${value}`
  - The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record. (default: 60, The default TTL for Amazon Lightsail DNS records is 60 seconds so I recommend to set a value greater than it)

## Getting Started
### Installation
Install this plugin using `pip`:
```
pip install certbot-dns-lightsail
```

### Usage
This plugin requires AWS region and credential settings before it can be used. And the region must be `us-east-1`.

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
        }
    ]
}
```

#### 2. Create Setting Files
Create setting files below:
```
# ~/.aws/config
[default]
region=us-east-1

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
  --dns-lightsail-propagation-seconds 70 \
  --non-interactive \
  --agree-tos \
  -m 'mail@example.com' \
  -d 'example.com' \
  -d '*.example.com'
```
