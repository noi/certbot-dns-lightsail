import setuptools

install_requires = [
    'certbot>=1.8.0',
    'boto3>=1.14.59',
    'zope.interface>=5.1.0',
]

dev_extras = [
    'tox',
    'flake8',
    'flake8-import-order',
    'wheel',
    'twine',
]

dev_py27_extras = [
    'mock',
    'parsedatetime==2.5',
]

extras_require = {
    'dev': dev_extras,
    'dev:python_version=="2.7"': dev_py27_extras,
}

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
    extras_require=extras_require,
    entry_points=entry_points,
)
