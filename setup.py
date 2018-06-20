import ast
import re

import setuptools

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open("terrafirma/__init__.py", 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

policy_files = ["policy/*.yaml"]

setuptools.setup(
    name="terrafirma",
    version=version,
    url="https://github.com/wayfair/terrafirma",

    author="Security Engineering",
    author_email="security@wayfair.com",

    description="terrafirma - a terraform security linter",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),
    package_data={'package': policy_files},
    include_package_data=True,

    tests_require=[
        'pytest',
    ],

    setup_requires=['pytest-runner'],

    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    entry_points={
        'console_scripts': [
            'terrafirma = terrafirma.__main__:main',
        ]
    },
)
