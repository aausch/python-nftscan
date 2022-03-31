#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['requests>=2.27.1']

test_requirements = ['pytest>=3', ]

setup(
    author="Alex Ausch",
    author_email='alex@ausch.name',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
        
    ],
    description="Python 3 wrapper for the NFTScan API",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=['nft', 'blockchain', 'nftscan'],
    maintainer='Alex Ausch',
    maintainer_email='alex@ausch.name',
    name='nftscan-api',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nftscan2022/nftscan-api-python-sdk',
    project_urls={
        'Source': 'https://github.com/nftscan2022/nftscan-api-python-sdk',
    },
    version='0.1.3',
    zip_safe=False,
)
