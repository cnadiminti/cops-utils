#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

install_requires = ['docker-compose'
                    ]
tests_require = ['pytest']

setup(
    name='cops-utils',
    version='0.0.1dev0',
    description='''Utilities to convert COPS
        (Container Orchestration Platform Specifications)''',
    url='https://github.com/cnadiminti/cops-utils',
    author='Chandra Nadiminti <nadiminti.chandra@gmail.com>',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    test_suite='',
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points="""
    [console_scripts]
    dockercompose2marathon=cops_utils.dockercompose2marathon:main
    dockercompose2run=cops_utils.dockercompose2run:main
    """,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
