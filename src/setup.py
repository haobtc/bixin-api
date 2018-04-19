import os
from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))

requires = (
    "pendulum>=1.3.2",
    "requests",
    "pycrypto",
)


setup(
    name='poim',
    version='0.0.1',
    packages=find_packages(here),
    license='MIT',
    author='the-chosen-ones',
    description='POIM api wrapper',
    install_requires=requires,
)
