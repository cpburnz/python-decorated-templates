# coding: utf-8
"""
This function displays information about globals.
"""

import sys

def print_globals(obj):
	print obj
	print id(obj.__globals__), obj.__globals__.keys()
	return obj
	
@print_globals
def func():
	pass
	
class Test(object):
	
	@print_globals
	def instfunc(self):
		pass
	
	@classmethod
	@print_globals
	def classfunc(cls):
		pass
	
	@staticmethod
	@print_globals
	def staticfunc():
		pass
	
def main(argv):
	print sys.modules[__name__]
	print id(sys.modules[__name__].__dict__), sys.modules[__name__].__dict__.keys()
	print_globals(Test.instfunc)
	print_globals(Test.classfunc)
	print_globals(Test.staticfunc)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
