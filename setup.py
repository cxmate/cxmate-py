from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cxmate',
    version='0.1.0',
    description='SDK for creating cxMate services',
    long_description=long_description,
    url='https://github.com/cxmate/cxmate-py',
    author='Eric Sage, Brett Settle',
    author_email='eric.david.sage@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='cytoscape networkx network biology cxmate',
    packages=find_packages(),
    install_requires=['networkx', 'grpc', 'futures'],
)
