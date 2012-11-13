# coding: utf-8
"""
This script tests the general implementation of the ``template``
function and the ``Template`` class.
"""

import inspect
import os.path
import sys
import unittest
from xml.sax.saxutils import escape, quoteattr

SETUP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SETUP_DIR)

import pdt

class TemplateTest(unittest.TestCase):

	def setUp(self):
		self.func = html_func
		self.func_data = html_data
		self.func_str = html_str
	
	def test_00_template(self):
		# Compile template.
		temp = pdt.template(self.func)
		
		# Make sure template looks like the original function.
		self.assertTrue(inspect.isfunction(temp))
		self.assertTrue(temp.__name__ == self.func.__name__)
		self.assertTrue(temp.__module__ == self.func.__module__)
		self.assertTrue(temp.__globals__ is self.func.__globals__)
		self.assertTrue(temp.__doc__ is None)
		
		# Make sure template output is what is expected.
		temp_str = temp(self.func_data)
		self.assertTrue(temp_str == self.func_str)

	def test_01_template_with_args(self):
		# Get template decorator.
		dec = pdt.template()
		self.assertTrue(dec.__name__ == 'template_decorator')
		self.assertTrue(isinstance(dec.__closure__[0].cell_contents, pdt.Template))
		
		# Compile template.
		temp = dec(self.func)
		
		# Make sure template looks like the original function.
		self.assertTrue(inspect.isfunction(temp))
		self.assertTrue(temp.__name__ == self.func.__name__)
		self.assertTrue(temp.__module__ == self.func.__module__)
		self.assertTrue(temp.__globals__ is self.func.__globals__)
		self.assertTrue(temp.__doc__ is None)
		
		# Make sure template output is what is expected.
		temp_str = temp(self.func_data)
		self.assertTrue(temp_str == self.func_str)
		
	def test_02_doc(self):
		# Create template.
		@pdt.template(doc="The template function's doc string.")
		def temp():
			"The template function's result."
		
		# Make sure doc string is set.
		self.assertTrue(temp.__doc__ == "The template function's doc string.")
		
		# Make sure the added doc string was not added to the result.
		temp_str = temp()
		self.assertTrue(temp_str == "The template function's result.")

	def test_02_class_methods(self):
	
		# Create class with instance, class and static method templates.
		class TestClass(object):
		
			@pdt.template
			def instfunc(self, TestClass):
				assert isinstance(self, TestClass)
		
			@classmethod
			@pdt.template
			def classfunc(cls, TestClass):
				assert cls is TestClass
	
			@staticmethod
			@pdt.template
			def staticfunc():
				pass

		# Make sure all methods from instance work.
		test = TestClass()
		test.instfunc(TestClass)
		test.classfunc(TestClass)
		test.staticfunc()
		
		# Make sure all methods on class work.
		TestClass.instfunc(test, TestClass)
		TestClass.classfunc(TestClass)
		TestClass.staticfunc()


html_data = {
	'doctype': """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">""",
	'post_url': '/test/item',
	'post_data': [('action', 'add')],
	'back_url': '/test',
	'items': [
		{
			'item_id': "SC-333-006-03-16",
			'brand': "Scorpian",
			'title': "Scorpion Vision Vest",
			'edit_url': '/test/item/edit?item=SC-333-006-03-16',
			'delete_url': '/test/item/delete?item=SC-333-006-03-16'
		},
		{
			'item_id': "ZR-0103-0065",
			'brand': "Z1R",
			'title': "Z1R Nomad Ghost Flames Half Helmet",
			'edit_url': '/test/item/edit?item=ZR-0103-0065',
			'delete_url': '/test/item/delete?item=ZR-0103-0065'
		},
		{
			'item_id': "JR-356-1002",
			'brand': "Joe Rocket",
			'title': "Joe Rocket Highside Leather Gloves",
			'edit_url': '/test/item/edit?item=JR-356-1002',
			'delete_url': '/test/item/delete?item=JR-356-1002'
		},
		{
			'item_id': "HJC-901-109",
			'brand': "HJC",
			'title': "HJC Coolmax Balaclava",
			'edit_url': '/test/item/edit?item=HJC-901-109',
			'delete_url': '/test/item/delete?item=HJC-901-109'
		},
		{
			'item_id': "FR-352-0100YS",
			'brand': "Fly Racing",
			'title': "Fly Racing Youth Dropping Bombs Tee",
			'edit_url': '/test/item/edit?item=FR-352-0100YS',
			'delete_url': '/test/item/delete?item=FR-352-0100YS'
		},
		{
			'item_id': "SU-0130-0003",
			'brand': "Suomy",
			'title': "Suomy Ventura Helmet Shield",
			'edit_url': '/test/item/edit?item=SU-0130-0003',
			'delete_url': '/test/item/delete?item=SU-0130-0003'
		},
		{
			'item_id': "AR-817420",
			'brand': "Arai",
			'title': "Arai Signet-Q Racer Full Face Helmet",
			'edit_url': '/test/item/edit?item=AR-817420',
			'delete_url': '/test/item/delete?item=AR-817420'
		},
		{
			'item_id': "HMK-460-99225",
			'brand': "Hmk",
			'title': "Hmk Alpine Billed Knit Beanie",
			'edit_url': '/test/item/edit?item=HMK-460-99225',
			'delete_url': '/test/item/delete?item=HMK-460-99225'
		},
		{
			'item_id': "AS-2830-0058",
			'brand': "Alpinestars",
			'title': "Alpinestars Stealth Vest",
			'edit_url': '/test/item/edit?item=AS-2830-0058',
			'delete_url': '/test/item/delete?item=AS-2830-0058'
		},
		{
			'item_id': "IC-1533-30-02",
			'brand': "Icon",
			'title': "Icon Motorhead Leather Jacket",
			'edit_url': '/test/item/edit?item=IC-1533-30-02',
			'delete_url': '/test/item/delete?item=IC-1533-30-02'
		}
	]
}

def html_func(data):
	"""{doctype}
<html>
	<head>
		<title>Test Page</title>
	</head>
	<body>
	""".format(doctype=data['doctype'])
	
	# Header.
	"""
		<div id="header">
			<h1>Test Page</h1>
			<form id="form" method="POST" action={post_url}>
	""".format(post_url=quoteattr(data['post_url']))
	for key, value in data['post_data']:
		"""
				<input type="hidden" name={} value={}/>
		""".format(quoteattr(key), quoteattr(value))
	"""
				<input name="item" type="text"/>
				<input type="submit" value="Add"/>
			</form>
		</div>
	"""
	
	# Body.
	"""
		<div id="body">
			<h2>Items</h2>
			<table>
				<thead>
					<tr>
						<th>Item ID</th>
						<th>Brand</th>
						<th>Title</th>
						<th colspan="2"></th>
					</tr>
				</thead>
				<tbody>
	"""
	for item in data['items']:
		"""
					<tr class="item">
						<td class="id">{item_id}</td>
						<td class="brand">{brand}</td>
						<td class="title">{title}</td>
						<td class="edit"><a href={edit_url}>edit</a></td>
						<td class="delete"><a href={delete_url}>delete</a></td>
					</tr>
		""".format(
			item_id=escape(item['item_id']),
			brand=escape(item['brand']),
			title=escape(item['title']),
			edit_url=quoteattr(item['edit_url']),
			delete_url=quoteattr(item['delete_url'])
		)
	"""
				</tbody>
			</table>
		</div>
	"""
	
	# Footer.
	"""
		<div id="footer">
			<a href={back_url}>Go Back</a>
		</div>
	""".format(back_url=quoteattr(data['back_url']))
	
	"""
	</body>
</html>
	""".rstrip()
	
html_str = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
	<head>
		<title>Test Page</title>
	</head>
	<body>
	
		<div id="header">
			<h1>Test Page</h1>
			<form id="form" method="POST" action="/test/item">
	
				<input type="hidden" name="action" value="add"/>
		
				<input name="item" type="text"/>
				<input type="submit" value="Add"/>
			</form>
		</div>
	
		<div id="body">
			<h2>Items</h2>
			<table>
				<thead>
					<tr>
						<th>Item ID</th>
						<th>Brand</th>
						<th>Title</th>
						<th colspan="2"></th>
					</tr>
				</thead>
				<tbody>
	
					<tr class="item">
						<td class="id">SC-333-006-03-16</td>
						<td class="brand">Scorpian</td>
						<td class="title">Scorpion Vision Vest</td>
						<td class="edit"><a href="/test/item/edit?item=SC-333-006-03-16">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=SC-333-006-03-16">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">ZR-0103-0065</td>
						<td class="brand">Z1R</td>
						<td class="title">Z1R Nomad Ghost Flames Half Helmet</td>
						<td class="edit"><a href="/test/item/edit?item=ZR-0103-0065">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=ZR-0103-0065">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">JR-356-1002</td>
						<td class="brand">Joe Rocket</td>
						<td class="title">Joe Rocket Highside Leather Gloves</td>
						<td class="edit"><a href="/test/item/edit?item=JR-356-1002">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=JR-356-1002">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">HJC-901-109</td>
						<td class="brand">HJC</td>
						<td class="title">HJC Coolmax Balaclava</td>
						<td class="edit"><a href="/test/item/edit?item=HJC-901-109">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=HJC-901-109">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">FR-352-0100YS</td>
						<td class="brand">Fly Racing</td>
						<td class="title">Fly Racing Youth Dropping Bombs Tee</td>
						<td class="edit"><a href="/test/item/edit?item=FR-352-0100YS">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=FR-352-0100YS">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">SU-0130-0003</td>
						<td class="brand">Suomy</td>
						<td class="title">Suomy Ventura Helmet Shield</td>
						<td class="edit"><a href="/test/item/edit?item=SU-0130-0003">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=SU-0130-0003">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">AR-817420</td>
						<td class="brand">Arai</td>
						<td class="title">Arai Signet-Q Racer Full Face Helmet</td>
						<td class="edit"><a href="/test/item/edit?item=AR-817420">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=AR-817420">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">HMK-460-99225</td>
						<td class="brand">Hmk</td>
						<td class="title">Hmk Alpine Billed Knit Beanie</td>
						<td class="edit"><a href="/test/item/edit?item=HMK-460-99225">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=HMK-460-99225">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">AS-2830-0058</td>
						<td class="brand">Alpinestars</td>
						<td class="title">Alpinestars Stealth Vest</td>
						<td class="edit"><a href="/test/item/edit?item=AS-2830-0058">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=AS-2830-0058">delete</a></td>
					</tr>
		
					<tr class="item">
						<td class="id">IC-1533-30-02</td>
						<td class="brand">Icon</td>
						<td class="title">Icon Motorhead Leather Jacket</td>
						<td class="edit"><a href="/test/item/edit?item=IC-1533-30-02">edit</a></td>
						<td class="delete"><a href="/test/item/delete?item=IC-1533-30-02">delete</a></td>
					</tr>
		
				</tbody>
			</table>
		</div>
	
		<div id="footer">
			<a href="/test">Go Back</a>
		</div>
	
	</body>
</html>"""

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TemplateTest)
	unittest.TextTestRunner(verbosity=2).run(suite)
