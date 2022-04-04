from setuptools import setup

setup(
    name='ts-pip-plugin',

    packages=['ts_pip_plugin'],

    version='1.0.3',

    description='Scans a Python project for all installed pip modules and posts the scan information to the TrustSource service or writes it to disc',

    author='EACG GmbH',

    license='ASL-2.0',

    url='https://github.com/trustsource/ts-pip-plugin.git',

    download_url='',

    keywords=['scanning', 'dependencies', 'modules', 'compliance', 'TrustSource'],

    classifiers=[],

    install_requires=[
        'ts-python-client==1.0.3', 
        'importlib-metadata'
    ],

    scripts=['ts-pip-plugin'],

    entry_points={
        'console_scripts': ['ts-pip-plugin=ts_pip_plugin.cli:main'],
    }
)