from setuptools import setup


setup(
    name='trytond_integration_api',
    version='8.0.0',
    description='Configurable HTTP integrations for Tryton',
    package_dir={'trytond.modules.integration_api': '.'},
    packages=[
        'trytond.modules.integration_api',
        ],
    package_data={
        'trytond.modules.integration_api': [
            'tryton.cfg',
            '*.xml',
            'view/*.xml',
            'locale/*.po',
            ],
        },
    install_requires=[
        'Jinja2',
        'requests',
        'trytond>=8.0,<8.1',
        ],
    entry_points="""
    [trytond.modules]
    integration_api = trytond.modules.integration_api
    """,
    )
