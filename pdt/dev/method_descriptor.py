# coding: utf-8
"""
This script tests using a method descriptor.
"""

import sys

class Wrap(object):
	def __init__(self, func):
		print "INIT", self, func
		self.func = func
	
	def __get__(self, obj, type=None):
		print "GET", self, self.func
		print "ARG", obj, type
		bound = self.func.__get__(obj, type)
		print "BOUND", id(bound), bound
		self.func = bound
		#result = self.__class__(bound)
		#print "RES", result
		return self
	
	def __call__(self, *args, **kw):
		print "CALL", self, self.func
		return self.func(*args, **kw)
	
class NewClass(object):
	
	@Wrap
	def instfunc(self=None):
		assert isinstance(self, NewClass), "self:%r is not a NewClass." % self
		print "self:%r is a NewClass." % self
	
	@classmethod
	@Wrap
	def classfunc(cls=None):
		assert cls is NewClass, "cls:%r is not NewClass." % cls
		print "cls:%r is NewClass." % cls
		
	@staticmethod
	@Wrap
	def staticfunc(arg=None):
		assert arg is None, "args:%r is not None." % arg
		print "arg:%r is None." % arg

''' # Works
class OldClass:
	
	@Wrap
	def instfunc(self=None):
		assert isinstance(self, OldClass), "self:%r is not an OldClass." % self
		print "self:%r is an OldClass." % self
	
	@classmethod
	@Wrap
	def classfunc(cls=None):
		assert cls is OldClass, "cls:%r is not OldClass." % cls
		print "cls:%r is OldClass." % cls
		
	@staticmethod
	@Wrap
	def staticfunc(arg=None):
		assert arg is None, "args:%r is not None." % arg
		print "arg:%r is None." % arg
'''

def main(argv):
	new = NewClass()
	new.instfunc()
	new.instfunc()
	new.instfunc()
	new.classfunc()
	new.staticfunc()
	#old = OldClass()
	#old.instfunc()
	#old.classfunc()
	#old.staticfunc()
	return 0
	
if __name__ == '__main__':
	sys.exit(main(sys.argv))
