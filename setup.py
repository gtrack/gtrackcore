from setuptools import setup, find_packages

setup(

name='gtrackcore',
version='0.1.0',
packages = find_packages(),
package_data={'gtrackcore': ['data/*\.*', 'data/gtrack/*', 'data/GESourceTracks/*/*']},

author='Sveinung Gundersen, Marcin Cieslik, Stephen Hoang, Tobias G. Waaler',
author_email='sveinugu@gmail.com',
test_suite='nose.collector',
setup_requires=['nose>=1.0', 'tables>=2.4.0']

)
