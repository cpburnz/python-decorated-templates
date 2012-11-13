# coding: utf-8
"""
PDT: Python Decorated Templates
===============================

Introduction
------------

Why bother working with embedded templating languages within Python when
Python is already a fully functional and extensible scripting language
perfect for templating? PDT provides a straight forward templating
strategy for Python. All that's involed is decorating your template
functions, and all expressions within them will be concatenated and
returned at function completion.


Source
------

The source code for PDT is available from the GitHub repo
`cpburnz/python-decorated-templates`_.

.. _`cpburnz/python-decorated-templates`: https://github.com/cpburnz/python-decorated-templates.git
    
    
Installation
------------

PDT can be installed from source with::
    
    python setup.py install
    
PDT is also available for install through PyPI_::

    pip install pdt

.. _PyPI: http://pypi.python.org/pypi/pdt


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

    def spam(eggs, ham=None):
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

Templates cannot define a doc string after their function signature
because it will be interpreted as an expression and prepended to the
result of each call. However, a doc string can be provided through the
*doc* argument of the template decorator::

    import pdt
    
    @pdt.template(doc="My doc string.")
    def span(...):
        ...


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
		
*io_args* (**sequence**) optionally specifies any positional arguments
passed to *io_factory* when it is called. Default is an empty ``tuple``.
		
*io_kw* (**mapping**) optionally specifies keyword arguments passed to
*io_factory* when it is called. Default is an empty ``dict``.

Here's a simplified version of the built-in ``ListIO`` class::

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
    
To decorate several templates with the same arguments, just store the
arguments in a ``dict`` and pass them as **keyword arguments**::
    
    latin1 = {'io_factory': CustomIO, 'io_kw': {'encoding': 'latin1'}}
  
    @pdt.template(**latin1)
    def spam2(...):
        ...
        
    @pdt.template(**latin1)
    def spam3(...):
        ...

The *io_args* and *io_kw* are passed as positional and keyword arguments
to *io_factory* which is the class constructor.

The *write()* function will receive the result of each expression in the
first argument: *data*. *data* will have to be converted to either a
``str`` or ``unicode`` manually. If *data* is ``None``, it should be
ignored so functions which do not return a value (i.e., ``None``) do not
output "None" for each call.

The *getvalue()* function returns the concatenated ``str`` or
``unicode`` result of every expression sent to *write()*.


Implementation
--------------

PDT is inspired by Quixote_'s PTL_ (Python Template Language) but without
the need for special file syntax, extensions and import hooks. The PDT
template decorator modifies the source of wrapped functions, and
recompiles them to allow for the expression output.

.. _Quixote: http://quixote.ca/
.. _PTL: http://quixote.ca/doc/PTL.html

Only functions ``def``\ ed in modules, classes and functions are
supported. Functions for which their text source code is not available
are not supported. Neither generators nor ``lambda``\ s are supported.
Functions can only be decorated above/after (not below/before) being
decorated as a template.

.. NOTE: Generator functions might be supported in the future.
"""

__author__ = "Caleb P. Burns <cpburnz@gmail.com>"
__copyright__ = "Copyright (C) 2012 by Caleb P. Burns"
__license__ = "MIT"
__version__ = "0.7.8"
__status__ = "Development"

import ast
import _ast
import collections
import functools
import inspect
import linecache

__all__ = ['template']

_ast_store = _ast.Store()
_ast_load = _ast.Load()
_ast_param = _ast.Param()

def template(*args, **kw):
	"""
	Wraps the specified template function which will be recompiled to
	concatenate all of its expressions and return the result at the end of
	a call.
	
	*args* (``tuple``) contains any variadic positional arguments. If set,
	the first positional argument must be the template ``function`` to
	recompile.
	
	*kw* (``dict``) contains any variable keyword arguments to be passed
	to the ``Template`` constructor.
	
	If the template ``function`` is passed in *args*, *kw* must be empty,
	and the recompiled template ``function`` will be returned.
	
	If the template ``function`` is not passed in *args*, then *kw* will
	contain any optional arguments for the ``Template`` constructor. A
	decorator (``function``) will be returned which will expect to be
	passed (by decorating) the template ``function``.
	"""
	wrapped = Template(*args, **kw)
	if wrapped.func:
		return wrapped.func
	
	def template_decorator(func):
		return wrapped(func).func
	
	return template_decorator


class Template(object):
	"""
	The ``Template`` class is used to wrap template functions which
	recompiles them to concatenate their expressions and return the final
	result at the end of the function call.
	"""
	
	__slots__ = ['doc', 'func', 'io_factory', 'io_args', 'io_kw']
	
	def __init__(self, *args, **kw):
		"""
		Initializes a ``Template`` instance.
		
		*args* (``list``) contains any variadic positional arguments. If
		set, the first positional argument must be the template ``function``
		to wrap.
		
		*kw* (``dict``) contains any variadic keyword arguments. The
		following keyword arguments can be set.
		
		*doc* (**string**) is the doc string to use for the wrapped template
		function.
		
		*io_factory* (**callable**) creates ``file``-like instances
		implementing *write()* and *getvalue()* when called. Default is
		``ListIO``.
		
		*io_args* (``tuple``) contains the positional arguments to pass to
		*io_factory* when it is called. Default is an empty ``tuple``.
		
		*io_kw* (``dict``) contains the keyword arguments to pass to
		*io_factory* when it is called. Default is an empty ``dict``.
		"""
		
		self.doc = None
		"""
		*doc* (**string**) is the template function doc string. Default is
		``None``.
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
		*io_args* (**sequence**) contains the positional arguments passed to
		*io_factory* when it is called. Default is an empty ``tuple``.
		"""
		
		self.io_kw = {}
		"""
		*io_kw* (**mapping**) contains the keyword arguments passed to
		*io_factory* when it is called. Default is an empty ``dict``.
		"""
		
		if kw:
			doc = kw.get('doc', None)
			if doc is not None:
				if not isinstance(doc, basestring):
					raise TypeError("doc:%r is not a string." % doc)
				self.doc = doc
		
			io_factory = kw.get('io_factory', None)
			if io_factory is not None:
				if not callable(io_factory):
					raise TypeError("io_factory:%r is not callable." % io_factory)
				self.io_factory = io_factory
			
			io_args = kw.get('io_args', None)
			if io_args is not None:
				if not isinstance(io_args, collections.Sequence):
					raise TypeError("io_args:%r is not a sequence." % io_args)
				self.io_args = io_args
			
			io_kw = kw.get('io_kw', None)
			if io_kw is not None:
				if not isinstance(io_kw, collections.Mapping):
					raise TypeError("io_kw:%r is not a mapping." % io_kw)
				self.io_kw = io_kw
			
		if args:
			# Wrap function.
			self.wrap_func(args[0])
		
	def __call__(self, func):
		# Wrap function.
		self.wrap_func(func)
		return self
	
	def __repr__(self):
		return "%s.%s(%s)" % (self.__class__.__module__, self.__class__.__name__, ", ".join([("%s=%s" % (k, repr(getattr(self, k)))) for k in self.__slots__ if getattr(self, k)]))

	def wrap_func(self, func):
		if self.func:
			raise RuntimeError("func is already set.")
		if not inspect.isfunction(func):
			raise TypeError("func:%r is not a function or method." % func)
			
		# Get function source code.
		#
		# HACK: Patch issue 1218234_. If getsource() is called on a
		# function, it's module is modified and reloaded afterward, and
		# getsource() is called again, then the returned source is the
		# cached source that was returned from the first call to
		# getsource(). This is due to the caching in the linecache module
		# not being tightly coupled with reload().
		#
		# .. 1218234: http://bugs.python.org/issue1218234
		func_file = inspect.getsourcefile(func)
		linecache.checkcache(func_file) # HACK: issue 1218234
		func_src, lineno = inspect.getsourcelines(func)
		
		# Dedent decorators and function def.
		dedent_func_lines(func_src)
		func_src = ''.join(func_src)
		
		# Parse function source code to AST.
		mod_ast = ast.parse(func_src)
		func_ast = mod_ast.body[0]
		
		# Wrap function in an enclosing function to create closure. This is
		# so that we can pass along our variables to the template function.
		if inspect.ismethod(func):
			enc_name = '__pdt_enc_%s_%s_%s' % (func.__module__, (func.im_self or func.im_class).__name__, func.__name__)
		else:
			enc_name = '__pdt_enc_%s_%s' % (func.__module__, func.__name__)
		enc_vars = {
			'__pdt_io_factory': self.io_factory,
			'__pdt_io_args': self.io_args,
			'__pdt_io_kw': self.io_kw
		}
		# def __pdt_enc_func(...):
		mod_ast.body[0] = _ast.FunctionDef(enc_name, _ast.arguments([
			_ast.Name('__pdt_io_factory', _ast_param),
			_ast.Name('__pdt_io_args', _ast_param),
			_ast.Name('__pdt_io_kw', _ast_param)
		], None, None, []), [
			# def func(...):
			#   ...
			func_ast,
			# return func
			_ast.Return(_ast.Name(func.__name__, _ast_load))
		], [])
		
		# Get template global namespace.
		# .. NOTE: This has to be the actual function globals (module dict)
		#    reference and NOT A COPY.
		func_globals = func.__globals__
		
		# Remove our decorator to prevent recursive wrapping. It is safe to
		# clear the whole list because decorators before ours have not yet
		# been called (but will be), and any decorators after ours would
		# have already caused an error with the call to get the function
		# source.
		func_ast.decorator_list = []
		
		# Add doc string and create template buffer at beginning of
		# function.
		func_body = []
		if self.doc:
			func_body.append(
				# """..."""
				_ast.Expr(_ast.Str(self.doc))
			)
		func_body += [
			# __pdt_buff = __pdt_io_factory(*__pdt_io_args, **__pdt_io_kw)
			_ast.Assign([_ast.Name('__pdt_buff', _ast_store)], _ast.Call(_ast.Name('__pdt_io_factory', _ast_load), [], [], _ast.Name('__pdt_io_args', _ast_load), _ast.Name('__pdt_io_kw', _ast_load))),
			# __pdt_write = __pdt_buff.write
			_ast.Assign([_ast.Name('__pdt_write', _ast_store)], _ast.Attribute(_ast.Name('__pdt_buff', _ast_load), 'write', _ast_load)),
			# __pdt_getvalue = __pdt_buff.getvalue
			_ast.Assign([_ast.Name('__pdt_getvalue', _ast_store)], _ast.Attribute(_ast.Name('__pdt_buff', _ast_load), 'getvalue', _ast_load))
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
		
		func_body += func_ast.body
		
		# Return buffer at end of function.
		func_body.append(
			# return __pdt_getvalue()
			_ast.Return(_ast.Call(_ast.Name('__pdt_getvalue', _ast_load), [], [], None, None))
		)
		
		func_ast.body = func_body
		
		# XXX
		'''
		import sys
		sys.path.append("../dev")
		from astpp import dump
		print "LINENO", lineno
		'''
		
		# Generate line and column information for modified AST.
		ast.fix_missing_locations(mod_ast)
		
		# Fix line numbers.
		ast.increment_lineno(mod_ast, lineno - 1)
		
		# XXX
		'''
		print "%s()" % func.__name__
		print dump(mod_ast, True, True, ' ')
		'''
		
		# Compile template function.
		exec compile(mod_ast, func_file, 'exec') in func_globals
		
		# Store compiled template function.
		self.func = func_globals[enc_name](**enc_vars)
		del func_globals[enc_name]
		

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


def dedent_func_lines(func_lines):
	# Dedent decorators and function def.
	for i, line in enumerate(func_lines):
		line = func_lines[i] = line.lstrip()
		if line.startswith('def'): 
			break

