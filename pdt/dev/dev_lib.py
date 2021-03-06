
import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')))

L = lambda: None
L2 = lambda: "String"

def A():
	"Line 1"

def A2():
	pass
	
def A3():
	None
	
def A4():
	""
	
def B():
	1 + 1
	
def C():
	1 + 1
	"Line 2"

def D():
	"Line 1"
	1 + 1
	sum([1,2,3])
	"Line 4"

def E():
	a = 123
	b = 'asd'
	def e():
		return a, b 
	return e

def F():
	1 if 2 else 3
	
def G():
	return g

def H(f,*a,**k):
	x = f(*a,**k)

'''
FunctionDef(
	name='H',
	args=arguments(
		args=[Name(id='f', ctx=Param())],
		vararg='a',
		kwarg='k',
		defaults=[]
	),
	body=[
		Assign(
			targets=[Name(id='x', ctx=Store())],
			value=Call(
				func=Name(id='f', ctx=Load()),
				args=[],
				keywords=[],
				starargs=Name(id='a', ctx=Load()),
				kwargs=Name(id='k', ctx=Load())
			)
		)
	],
	decorator_list=[]
)
'''

def I():
	a.b

'''
FunctionDef(
	name='I',
	args=arguments(args=[], vararg=None, kwarg=None, defaults=[]),
	body=[
		Expr(
			value=Attribute(
				value=Name(id='a', ctx=Load()),
				attr='b',
				ctx=Load()
			)
		)
	],
	decorator_list=[]
)
'''

def J():
	return a.b()

'''
FunctionDef(
	name='J',
	args=arguments(args=[], vararg=None, kwarg=None, defaults=[]),
	body=[
		Return(
			value=Call(
				func=Attribute(
					value=Name(id='a', ctx=Load()),
					attr='b',
					ctx=Load()
				),
				args=[], keywords=[], starargs=None, kwargs=None
			)
		)
	],
	decorator_list=[]
)
'''

def K():
	"asd" + "qwe"
	a("asd" + "qwe")
	
'''
FunctionDef(
	name='K',
	args=arguments(args=[], vararg=None, kwarg=None, defaults=[]),
	body=[
		Expr(
			value=BinOp(left=Str(s='asd'), op=Add(), right=Str(s='qwe'))
		),
		Expr(
			value=Call(
				func=Name(id='a', ctx=Load()),
				args=[
					BinOp(left=Str(s='asd'), op=Add(), right=Str(s='qwe'))
				],
				keywords=[], starargs=None, kwargs=None
			)
		)
	],
	decorator_list=[]
)
'''

def MultiReturn():
	return
	return None
	return a

'''
FunctionDef(
	name='L',
	args=arguments(args=[], vararg=None, kwarg=None, defaults=[]),
	body=[
		Return(value=None),
		Return(value=Name(id='None', ctx=Load())),
		Return(value=Name(id='a', ctx=Load()))
	],
	decorator_list=[]
)
'''


import pdt
@staticmethod
@pdt.template
def M():
	pass

'''
FunctionDef(
	name='M',
	args=arguments(args=[], vararg=None, kwarg=None, defaults=[]),
	body=[Pass()],
	decorator_list=[
		Name(id='staticmethod', ctx=Load()),
		Attribute(
			value=Name(id='pdt', ctx=Load()),
			attr='template',
			ctx=Load()
		)
	]
)
'''

def S(a, b):
	if a:
		pass
	elif b:
		pass
	else:
		pass
	
	while 1:
		break
	else:
		pass
	
	for x in a:
		pass
	else:
		pass
	
	try:
		pass
	except:
		pass
	else:
		pass
	finally:
		pass
	
	with a:
		pass
	
'''
FunctionDef(
	name='S',
	args=arguments(
		args=[Name(id='a', ctx=Param()), Name(id='b', ctx=Param())],
		vararg=None, kwarg=None, defaults=[]
	),
	body=[
		If(
			test=Name(id='a', ctx=Load()),
			body=[Pass()],
			orelse=[
				If(
					test=Name(id='b', ctx=Load()),
					body=[Pass()],
					orelse=[Pass()]
				)
			]
		),
		While(
			test=Num(n=1),
			body=[Break()],
			orelse=[Pass()]
		),
		For(
			target=Name(id='x', ctx=Store()),
			iter=Name(id='a', ctx=Load()),
			body=[Pass()],
			orelse=[Pass()]
		),
		TryFinally(
			body=[
				TryExcept(
					body=[Pass()],
					handlers=[
						ExceptHandler(
							type=None,
							name=None,
							body=[Pass()]
						)
					],
					orelse=[Pass()]
				)
			],
			finalbody=[Pass()]
		),
		With(
			context_expr=Name(id='a', ctx=Load()),
			optional_vars=None,
			body=[Pass()]
		)
	],
	decorator_list=[]
)
'''


class Wrap(object):
	def __init__(self, func):
		self.func = func
	
	def __get__(self, obj, type=None):
		return self.__class__(self.func.__get__(obj, type))
	
	def __call__(self, *args, **kw):
		return self.func(*args, **kw)


class T:
	
	def instfunc(self):
		pass
	
	@classmethod
	def classfunc(cls):
		pass
	
	@staticmethod
	def staticfunc():
		pass
	
	@pdt.template
	def tempfunc():
		pass
	
	@Wrap
	def wrapfunc(self):
		pass


def enclose(a, b, c=None):
	val = 123
	def closure(d, e, f=None):
		return val
	return closure


class Dedent(object):
	
	@staticmethod
	def func():
		"""
This text has no indentation while the func 'def' does.
		"""
		
@pdt.template
def raise_error():
	raise Exception("Error within template function.")
