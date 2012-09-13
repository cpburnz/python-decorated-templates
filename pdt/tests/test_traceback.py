# coding: utf-8
"""
This script tests the traceback of a decorated template.
"""

__author__ = "Caleb Burns"
__version__ = "0.7.4"
__status__ = "Development"

import os.path
import pprint
import sys
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import pdt

@pdt.template
def test_traceback():
	this_will_cause_an_error()
	
class A:
	
	@staticmethod
	@pdt.template()
	def test():
		another_error()
	
def main(argv):	
	try:
		test_traceback()
	except:
		traceback.print_exc()
	try:
		A.test()
	except:
		traceback.print_exc()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
