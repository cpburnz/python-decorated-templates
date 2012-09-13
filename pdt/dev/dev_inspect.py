# coding: utf-8
"""
This script inspects a given function.
"""

__author__ = "Caleb Burns"
__version__ = "0.7.4"
__status__ = "Development"

import ast
import argparse
import inspect
import os.path
import pprint
import sys
import textwrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

import astpp
import dev_lib
import pdt

def main(argv):
	parser = argparse.ArgumentParser(prog=argv[0], description=__doc__)
	parser.add_argument('func', help="The function to inspect.")
	args = parser.parse_args(argv[1:])
	
	# Get function.
	func = dev_lib
	for seg in args.func.split('.'):
		func = getattr(func, seg)
	
	print "Function"
	print "--------"
	print repr(func)
		
	# Get function source.
	func_src = inspect.getsourcelines(func)[0]
	pdt.dedent_func_lines(func_src)
	func_src = ''.join(func_src)
	func_src = func_src.replace("\t", "  ")
	
	print 
	print "Source"
	print "------"
	print func_src
	
	# Parse function source to AST.
	mod_ast = ast.parse(func_src)
	
	print "AST"
	print "---"
	print astpp.dump(mod_ast, include_attributes=True, indent=" ")

if __name__ == '__main__':
	sys.exit(main(sys.argv))
