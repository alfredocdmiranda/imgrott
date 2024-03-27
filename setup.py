from setuptools import setup

VERSION = open("VERSION").read()

setup(
    name='imgrott',
    version=VERSION,
    description='Alternative Growatt Monitor Server',
    url='https://github.com/alfredocdmiranda/imgrott',
    author='Alfredo Miranda',
    author_email='alfredocdmiranda@gmail.com',
    license='',
    packages=['imgrott'],
    entry_points={
        'console_scripts': ['imgrott=imgrott.main:main'],
    }
)
