# coding: utf-8

import functools
import sys

class A(object):
	"Class A doc-string"
	
	def __init__(self, func):
		self.wrap(func)
		
	def __call__(self, *args, **kw):
		return self.func(*args, **kw)
	
	def wrap(self, func):
		self.func = func
		for attr in functools.WRAPPER_ASSIGNMENTS:
			setattr(self, attr, getattr(func, attr))

class B(object):
	"Class B doc-string"
	
	def __init__(self, *args, **kw):
		self.func = None
	
	def __call__(self, *args, **kw):
		if self.func:
			return self.func(*args, **kw)
		else:
			self.wrap(args[0])
			return self
	
	def wrap(self, func):
		self.func = func
		for attr in functools.WRAPPER_ASSIGNMENTS:
			setattr(self, attr, getattr(func, attr))

class C(object):
	"Class C doc-string"
	
	def __init__(self, *args, **kw):
		print self, '__init__', args, kw
		if len(args) == 1 and callable(args[0]):
			self.wrap(args[0])
		else:
			self.func = None
	
	def __call__(self, *args, **kw):
		print self, '__call__', args, kw
		if self.func:
			return self.func(*args, **kw)
		else:
			self.wrap(args[0])
			return self
	
	def wrap(self, func):
		print self, 'wrap', func
		self.func = func
		for attr in functools.WRAPPER_ASSIGNMENTS:
			setattr(self, attr, getattr(func, attr))

def F():
	"Function doc-string"

def wrapA(func):
	wrapped = A(func)
	@functools.wraps(func)
	def wrapper(*args, **kw):
		return wrapped(*args, **kw)
	return wrapper

def wrapB(*args, **kw):
	b = B(*args, **kw)
	def decorator(func):
		wrapped = b(func)
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return wrapped(*args, **kw)
		return wrapper
	return decorator

def wrapC(*args, **kw):
	c = C(*args, **kw)
	if c.func:
		wrapped = c
		@functools.wraps(c.func)
		def wrapper(*args, **kw):
			return wrapped(*args, **kw)
		return wrapper
	else:
		def decorator(func):
			wrapped = c(func)
			@functools.wraps(func)
			def wrapper(*args, **kw):
				return wrapped(*args, **kw)
			return wrapper
		return decorator

def wrapC2(*args, **kw):
	c = C(*args, **kw)
	if c.func:
		return c.func
	else:
		def decorator(func):
			return func
		return decorator

def main(argv):
	print "F", F
	print "wrapA(F)", wrapA(F)
	print "wrapB()", wrapB()
	print "wrapB()(F)", wrapB()(F)
	print
	print "wrapC(F)"
	print wrapC(F)
	print
	print "wrapC()"
	print wrapC()
	print
	print "wrapC()(F)"
	print wrapC()(F)
	print
	print "wrapC2(F)"
	print wrapC2(F)
	print
	print "wrapC2()"
	print wrapC2()
	print
	print "wrapC2()(F)"
	print wrapC2()(F)


if __name__ == '__main__':
	sys.exit(main(sys.argv))
