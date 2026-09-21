import os

import setuptools


with open('README.md', 'r') as readme:
    long_description = readme.read()

project_urls = {
    'Certbot': 'https://certbot.eff.org/',
    'Amazon Lightsail': 'https://aws.amazon.com/lightsail/',
}

classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
    'Operating System :: POSIX :: Linux',
    'Environment :: Plugins',
]

certbot_version_restrictions = '>=5.0.0,<6'

install_requires = [
    f'certbot{certbot_version_restrictions}',
    f'acme{certbot_version_restrictions}',
    'boto3>=1.40.0',
]

dev_extras = [
    'tox',
    'flake8',
    'flake8-import-order',
    'build',
    'twine',
]

extras_require = {
    'dev': dev_extras,
}

entry_points = {
    'certbot.plugins': [
        'dns-lightsail = certbot_dns_lightsail.authentication:Authenticator'
    ]
}

setuptools.setup(
    name='certbot-dns-lightsail',
    version=os.getenv('PACKAGE_VERSION', '0.0.0'),
    author='Nobuki Fujii',
    description='Amazon Lightsail DNS Authenticator Plugin for Certbot',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/noi/certbot-dns-lightsail',
    license='MIT',
    project_urls=project_urls,
    python_requires='>=3.10',
    classifiers=classifiers,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
)
