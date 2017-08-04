from codecs import open
from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))
VERS = '1.0.3'
DESC = 'Script to create task records in airtable from parsed emails'

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='attaskcreator',
    version=VERS,

    description=DESC,
    long_description=LONG_DESCRIPTION,

    url='https://github.com/rickh94/attaskcreator.git',
    author='Rick Henry',
    author_email='fredericmhenry@gmail.com',

    license='GPLv3',
    python_requires='>=3',

    packages=find_packages(),

    install_requires=[
        'requests',
        'airtable',
        'html2text',
        'nameparser',
        'boto3',
        'daiquiri',
        ],

    entry_points={
        'console_scripts': [
            'attaskcreator = attaskcreator.create:main',
        ],
    },
)
