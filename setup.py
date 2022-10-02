from setuptools import setup

setup(
    name='fergus jobs',
    version='0.1.0',
    packages=['jobs'],
    url='',
    license='',
    author='Armon Rabiyan',
    author_email='armonr@duck.com',
    description='Fergus Jobs API',
    install_requires=[
        "click==8.1.3",
        "Flask==2.2.2",
        "importlib-metadata==4.12.0",
        "itsdangerous==2.1.2",
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.1",
        "Werkzeug==2.2.2",
        "zipp==3.8.1",
    ],
    tests_require=['pytest-flask'],
)
