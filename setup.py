# coding: utf-8
import sys
import warnings
from distutils.core import setup

if sys.version_info[:2] != (2, 7):
	warnings.warn("Only Python 2.7 has been tested, not %s.%s" % sys.version_info[:2]

import .pdt

setup(
	name="pdt"
	version=pdt.__version__,
	author="Caleb P. Burns",
	author_email="cpburnz@gmail.com",
	url="https://github.com/cpburnz/python-decorated-templates.git",
	description="Python templating strategy involving decorators and inline expressions.",
	long_description=pdt.__doc__,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python"
		"Programming Language :: Python :: 2.7",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	license="MIT",
	packages=['pdt']
)
