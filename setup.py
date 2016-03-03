try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': "Python labware interface",
	'author': "OpenTrons",
	'url': 'http://opentrons.com',
	'version': '0.1',
	'install_requires': [
		'nose',
		'coverage',
		'labware'
	],
	'packages': ['labware-interface'],
	'scripts': ['./bin/labware-test'],
	'name': 'labware-interface'
}

setup(**config)