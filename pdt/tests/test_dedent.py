# coding: utf-8
"""
This script tests dedenting a decorated function.
"""

__author__ = "Caleb Burns"
__version__ = "0.7.6"
__status__ = "Development"

import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import pdt

class Test(object):
	
	@pdt.template
	def func(self):
		"""
This text has no indentation while the func 'def' does.
		"""
		
def main(argv):
	test = Test()
	print test.func()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
