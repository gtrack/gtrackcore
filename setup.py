from setuptools import setup, find_packages

setup(

name='track5',
version='0.1.0',
packages=find_packages(),

author='Sveinung Gundersen, Marcin Cieslik, Stephen Hoang, Tobias G. Waaler',
author_email='sveinugu@gmail.com',
test_suite='nose.collector',
test_requires=['Nose']

)
