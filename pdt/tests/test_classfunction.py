# coding: utf-8
"""
This script tests to see if class functions can be decorated, not to be
confused with classmethod() or staticmethod().
"""

__author__ = "Caleb Burns"
__version__ = "0.7.4"
__status__ = "Development"

import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import pdt

class Test(object):
	
	@pdt.template
	def instfunc(self=None):
		assert isinstance(self, Test), "self:%r is not a Test." % self
		"self:%r is a Test." % self
		
	@pdt.template()
	def instfunc2(self=None):
		assert isinstance(self, Test), "self:%r is not a Test." % self
		"self:%r is a Test." % self
	
	@classmethod
	@pdt.template
	def classfunc(cls=None):
		assert cls is Test, "cls:%r is not Test." % cls
		"cls:%r is Test." % cls
	
	@classmethod
	@pdt.template()
	def classfunc2(cls=None):
		assert cls is Test, "cls:%r is not Test." % cls
		"cls:%r is Test." % cls
		
	@staticmethod
	@pdt.template
	def staticfunc(arg=None):
		assert arg is None, "args:%r is not None." % arg
		"arg:%r is None." % arg
		
	@staticmethod
	@pdt.template()
	def staticfunc2(arg=None):
		assert arg is None, "args:%r is not None." % arg
		"arg:%r is None." % arg

def main(argv):
	test = Test()
	print test.instfunc()
	print test.instfunc()
	print test.instfunc2()
	print test.instfunc2()
	print test.classfunc()
	print test.classfunc()
	print test.classfunc2()
	print test.classfunc2()
	print test.staticfunc()
	print test.staticfunc()
	print test.staticfunc2()
	print test.staticfunc2()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
