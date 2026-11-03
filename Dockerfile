ARG CERTBOT_VERSION
FROM certbot/certbot:v${CERTBOT_VERSION}

ARG CERTBOT_VERSION
ARG CERTBOT_DNS_LIGHTSAIL_VERSION

# Pin certbot so that installing the plugin never replaces the base image's one.
RUN pip install --no-cache-dir \
        "certbot==${CERTBOT_VERSION}" \
        "certbot-dns-lightsail==${CERTBOT_DNS_LIGHTSAIL_VERSION}"
