import os

import setuptools


with open('README.md', 'r') as readme:
    long_description = readme.read()

project_urls = {
    'Certbot': 'https://certbot.eff.org/',
    'Amazon Lightsail': 'https://aws.amazon.com/lightsail/',
}

python_requires = ', '.join([
    '>=2.7',
    '!=3.0.*',
    '!=3.1.*',
    '!=3.2.*',
    '!=3.3.*',
    '!=3.4.*',
    '!=3.5.*',
])

classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Operating System :: POSIX :: Linux',
    'Environment :: Plugins',
    'License :: OSI Approved :: MIT License',
]

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
    version=os.getenv('PACKAGE_VERSION', '0.0.0'),
    author='Nobuki Fujii',
    description='Amazon Lightsail DNS Authenticator Plugin for Certbot',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/noi/certbot-dns-lightsail',
    project_urls=project_urls,
    python_requires=python_requires,
    classifiers=classifiers,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
)
