
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
