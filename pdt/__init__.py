# coding: utf-8
"""
PDT: Python Decorated Templates
===============================

Introduction
------------

Why bother working with embedded templating languages within Python when
Python is already a fully functional and extensible scripting language
perfect for templating? PDT provides a straight forword templating
strategy for Python. All that's involed is decorating your template
functions, and all expressions within them will be concatenated and
returned at function completion.


Templates
---------

Here's an example using a simple template::

    import ptd
    
    @pdt.template
    def spam(eggs, ham=None):
        '''
        This would normally be the doc string but this is going to be
        outputted like an expression.
        '''
        eggs # Output some eggs
        sum(xrange(10)) # Output 45
        "Here's another string expression."
        
        print "These are still regular print statements that will be"
        print "printed to stdout."
        
        if not ham:
            # All expressions up to this point will be returned with the
            # empty return statement.
            return
        
        "Have some %s ham." % ham # Output the ham
        
        # All expressions outputted will be return at the end of a
        # template.
			
Here's what the template will look like after being recompiled::

    import pdt

    def spam(eggs, ham=None)
        _buffer = pdt.ListIO()
        _buffer.write('''
        This would normally be the doc string but this is going to be
        outputted like an expression.
        ''')
        _buffer.write(eggs) # Output some eggs.
        _buffer.write(sum(xrange(10))) # Output 45
        _buffer.write("Here's another string expression.")

        print "These are still regular print statements that will be"
        print "printed to stdout."

        if not ham:
            # All expressions up to this point will be returned with the
            # empty return statement.
            return _buffer.getvalue()

        _buffer.write("Have some %s ham." % ham) # Output the ham

        # All expressions outputted will be returned at the end of a
        # template.
        return _buffer.getvalue()


Template IO Buffer
------------------

Templates use an internal buffer to store expression results which will
be returned at the end of the function. A custom buffer factory function
and arguments can be specified with::

    import pdt
    
    @pdt.template(io_factory=myfactory, io_args=myargs, io_kw=mykeywords)
    def spam(...):
			...

*io_factory* (**callable**) creates ``file``-like instances implementing
*write()* and *getvalue()* when called. Typically, this will be a
class object. By default this is ``ListIO``. 
		
*io_args* (``tuple``) optionally specifies any positional arguments
passed to *io_factory* when it is called. Default is an empty ``tuple``.
		
*io_kw* (``dict``) optionally specifies keyword arguments passed to
*io_factory* when it is called. Default is an empty ``dict``.

Here's a simplified version of the ``ListIO`` class::

    class SimpleListIO(object):
        def __init__(self):
            self.buff = []
        
        def write(self, data):
            if data is not None:
                self.buff.append(str(data))
        
        def getvalue(self):
            return "".join(self.buff)

    import pdt
    
    @pdt.template(io_factory=SimpleListIO)
    def spam(...):
        ...

Here's an example IO Buffer that encodes the results and stores them
using ``cStringIO``::

    import cStringIO
    
    class CustomIO(object):
        def __init__(self, encoding='utf8'):
            self.buff = cStringIO.StringIO()
            self.enc = encoding

        def write(self, data):
            if data is not None:
                self.buff.write(unicode(data).encode(self.enc))

        def getvalue(self):
            return self.buff.getvalue()

    import pdt

    @pdt.template(io_factory=CustomIO, io_kw={'encoding': 'latin1'})
    def spam(...):
        ...

The *io_args* and *io_kw* are passed as positional and keyword arguments
to *io_factory* which is the class constructor.

The *write()* function will receive the result of each expression in the
first (*data*) argument. *data* will have to be converted to either a
``str`` or ``unicode`` manually. If *data* is ``None``, it should be
ignored so functions which do not return a value (i.e., ``None``) do not
output "None" for each call.

The *getvalue()* function returns the concatenated ``str`` or
``unicode`` result of every expression sent to *write()*.


Implementation
--------------

PDT is inspired by Quixote's PTL_ (Python Template Language) but without
the need for special file syntax, extensions and import hooks. The PDT
template decorator modifies the source of wrapped functions, and
recompiles them to allow for the expression output.

.. _PTL: http://quixote.ca/

Only in source ``def``ed functions are supported. Functions for which
their text source (not byte code) is not available are not supported.
Neither are closures, generators, nor are ``lambda``s supported.
Functions can only be decorated above/after (not below/before) being
decorated as a template.

.. NOTE: Generator functions might be supported in the future.
"""

__author__ = "Caleb P. Burns <cpburnz@gmail.com>"
__copyright__ = "Copyright (C) 2012 by Caleb P. Burns"
__license__ = "MIT"
__version__ = "0.7"
__status__ = "Development"

import ast
import _ast
import inspect
import types

__all__ = ['template']

_ast_store = _ast.Store()
_ast_load = _ast.Load()

class ListIO(object):
	"""
	The ``ListIO`` class is the default factory used by the ``Template``
	class to create ``file``-like buffer objects. 
	"""
	
	__slots__ = ['buff', 'is_unicode']
	
	def __init__(self):
		"""
		Initializes a ``ListIO`` instance.
		"""
		
		self.buff = []
		"""
		*buff* (``list``) is the internal buffer.
		"""
		
		self.is_unicode = None
		"""
		*is_unicode* (``bool``) is whether buffer contains ``unicode``
		(``True``), or ``str`` (``False``) data.
		"""
		
	def write(self, data):
		"""
		Writes the data to the buffer.
		
		*data* (**mixed**) is the data to write.
		"""
		if data is None:
			return
		
		# Convert data to string.
		if self.is_unicode is None:
			if isinstance(data, basestring):
				self.is_unicode = isinstance(data, unicode)
			elif hasattr(data, '__unicode__'):
				self.is_unicode = True
				data = unicode(data)
			else:
				self.is_unicode = False
				data = str(data)
		elif self.is_unicode:
			data = unicode(data)
		else:
			data = str(data)
			
		# Buffer string.
		self.buff.append(data)
			
	def getvalue(self):
		"""
		Gets the entire contents of the buffer.
		
		Returns the buffer's contents (``str`` or ``unicode``).
		"""
		return ''.join(self.buff)
		

class Template(object):
	"""
	The ``Template`` class is used to wrap template functions which
	recompiles them to concatenate their expressions and return the final
	result at the end of the function call.
	"""
	
	__slots__ = ['func', 'io_factory', 'io_args', 'io_kw']
	
	def __init__(self, *args, **kw):
		"""
		Initializes a ``Template`` instance.
		
		*args* (``list``) contains any variadic positional arguments. If
		set, the first positional argument must be the template ``function``
		to wrap.
		
		*kw* (``dict``) contains any variadic keyword arguments. The
		following keyword arguments can be set.
		
		*io_factory* (**callable**) creates ``file``-like instances
		implementing *write()* and *getvalue()* when called. Default is
		``ListIO``.
		
		*io_args* (``tuple``) contains the positional arguments to pass to
		*io_factory* when it is called. Default is an empty ``tuple``.
		
		*io_kw* (``dict``) contains the keyword arguments to pass to
		*io_factory* when it is called. Default is an empty ``dict``.
		"""
		
		self.func = None
		"""
		*func* (``function``) is the wrapped template function.
		"""
		
		self.io_factory = ListIO
		"""
		*io_factory* (**callable**) creates ``file``-like instances
		implementing *write()* and *getvalue()* when called.
		"""
		
		self.io_args = ()
		"""
		*io_args* (``tuple``) contains the positional arguments passed to
		*io_factory* when it is called. Default is an empty ``tuple``.
		"""
		
		self.io_kw = {}
		"""
		*io_kw* (``dict``) contains the keyword arguments passed to
		*io_factory* when it is called. Default is an empty ``dict``.
		"""
		
		if kw:
			# Set options.
			if 'io_factory' in kw:
				self.io_factory = kw['io_factory']
			
			if 'io_args' in kw:
				self.io_args = kw['io_args']
			
			if 'io_kw' in kw:
				self.io_kw = kw['io_kw']
			
		if args:
			# Wrap function.
			self.wrap_func(*args)
		
	def __call__(self, *args, **kw):
		if self.func:
			# Render template.
			return self.func(*args, **kw)
		
		# Wrap function.
		self.wrap_func(*args, **kw)
		return self

	def __repr__(self):
		return "%s.%s(%s)" % (self.__class__.__module__, self.__class__.__name__, ", ".join([("%s=%s" % (k, repr(getattr(self, k)))) for k in self.__slots__ if getattr(self, k)]))

	def wrap_func(self, func):
		if self.func:
			raise RuntimeError("func is already set.")
		if not isinstance(func, types.FunctionType):
			raise TypeError("func:%r is not a function." % func)
		
		# Get function source code.
		func_src = inspect.getsource(func)
		
		# Parse function source code to AST.
		mod_ast = ast.parse(func_src)
		func_ast = mod_ast.body[0]
		
		# Setup template global namespace.
		func_ns = func.__globals__.copy()
		func_ns['__pdt_io_factory'] = self.io_factory
		func_ns['__pdt_io_args'] = self.io_args
		func_ns['__pdt_io_kw'] = self.io_kw

		# Remove our decorator to prevent recursive wrapping. It is safe to
		# clear the whole list because decorators before ours have not yet
		# be called (but will be), and any decorators after ours would have
		# already caused an error with the call to get the function source.
		func_ast.decorator_list = []
		
		# Create template buffer, and return buffer value.
		func_ast.body = [
			# __pdt_buff = __pdt_io_factory(*__pdt_io_args, **__pdt_io_kw)
			_ast.Assign([_ast.Name('__pdt_buff', _ast_store)], _ast.Call(_ast.Name('__pdt_io_factory', _ast_load), [], [], _ast.Name('__pdt_io_args', _ast_load), _ast.Name('__pdt_io_kw', _ast_load))),
			# __pdt_write = __pdt_buff.write
			_ast.Assign([_ast.Name('__pdt_write', _ast_store)], _ast.Attribute(_ast.Name('__pdt_buff', _ast_load), 'write', _ast_load)),
			# __pdt_getvalue = __pdt_buff.getvalue
			_ast.Assign([_ast.Name('__pdt_getvalue', _ast_store)], _ast.Attribute(_ast.Name('__pdt_buff', _ast_load), 'getvalue', _ast_load))
		] + func_ast.body + [
			# return __pdt_getvalue()
			_ast.Return(_ast.Call(_ast.Name('__pdt_getvalue', _ast_load), [], [], None, None))
		]

		# Wrap expressions to write to buffer.
		node_lists = [func_ast.body]
		while node_lists:
			nodes = node_lists.pop()
			for i, node in enumerate(nodes):
				if isinstance(node, _ast.Expr):
					# expr -> __pdt_write(expr)
					nodes[i] = _ast.Expr(_ast.Call(_ast.Name('__pdt_write', _ast_load), [node.value], [], None, None))
				elif isinstance(node, _ast.Return):
					if not node.value:
						# return -> return __pdt_getvalue()
						node.value = _ast.Call(_ast.Name('__pdt_getvalue', _ast_load), [], [], None, None)
				elif isinstance(node, (_ast.If, _ast.While, _ast.For)):
					node_lists += [node.body, node.orelse]
				elif isinstance(node, _ast.TryExcept):
					node_lists += [node.body, node.orelse, node.handlers]
				elif isinstance(node, _ast.TryFinally):
					node_lists += [node.body, node.finalbody]
				elif isinstance(node, (_ast.ExceptHandler, _ast.With)):
					node_lists.append(node.body)
				elif isinstance(node, _ast.Yield):
					raise TypeError("Generator functions are not supported.")
		
		# Generate line and column information for modified AST.
		ast.fix_missing_locations(func_ast)
		
		# Compile template function.
		exec compile(mod_ast, "<%r %r>" % (self, func), 'exec') in func_ns
		
		# Store compiled template function.
		self.func = func_ns[func.__name__]
		
template = Template
