from setuptools import setup, find_packages
from codecs import open
from os import path
from subprocess import run

here = path.abspath(path.dirname(__file__))
vers = '0.3.1'
desc = 'Script to create task records in airtable from parsed emails'

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='attaskcreator',
    version=vers,

    description=desc,
    long_description=long_description,

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
                    'boto3'
                ],

    entry_points={
        'console_scripts': [
            'attaskcreator = attaskcreator.create:main',
        ],
    },
)
