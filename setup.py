# coding: utf-8
import sys
import warnings
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

# Change data path to packages path.
for scheme in INSTALL_SCHEMES.itervalues():
	scheme['data'] = scheme['purelib']

if sys.version_info[:2] != (2, 7):
	warnings.warn("Only Python 2.7 has been tested, not %s.%s" % sys.version_info[:2])

import pdt

# Write readme file.
with open('README.rst', 'wb') as fh:
	fh.write(pdt.__doc__)

# Read changes file.
with open('CHANGES.rst', 'rb') as fh:
	changes = fh.read()
	
setup(
	name="pdt",
	version=pdt.__version__,
	author="Caleb P. Burns",
	author_email="cpburnz@gmail.com",
	url="https://github.com/cpburnz/python-decorated-templates.git",
	description="Python templating strategy involving decorators and inline expressions.",
	long_description=pdt.__doc__ + "\n\n" + changes,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	license="MIT",
	packages=['pdt'],
	package_dir={'pdt': 'pdt'},
	data_files=[('pdt', ['LICENSE.txt'])]
)
