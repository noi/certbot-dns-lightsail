import setuptools

install_requires = [
    'certbot>=1.8.0',
    'boto3>=1.14.59',
    'zope.interface>=5.1.0',
]

entry_points = {
    'certbot.plugins': [
        'dns-lightsail = certbot_dns_lightsail.authentication:Authenticator'
    ]
}

setuptools.setup(
    name='certbot-dns-lightsail',
    version='0.0.0',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=install_requires,
    entry_points=entry_points,
)
