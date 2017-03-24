from setuptools import setup

setup(
    name='ecs-pip-plugin',

    packages=['ecs_pip_plugin'],

    version='0.1',

    description='Scans a Python project for all installed pip modules and posts the scan information to the ECS service',

    author='EACG GmbH',

    license='MIT',

    url='https://github.com/eacg-gmbh/ecs-pip-plugin.git',

    download_url='',

    keywords=['scanning', 'dependencies', 'modules', 'ECS'],

    classifiers=[],

    install_requires=['requests'],

    scripts=['ecs-pip-plugin'],

    entry_points={
        'console_scripts': ['ecs-pip-plugin=ecs_pip_plugin.cli:main'],
    }
)