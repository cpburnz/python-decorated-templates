# coding: utf-8
"""
This script tests the PDT template decorator.
"""

__author__ = "Caleb P. Burns"
__version__ = "0.1"
__status__ = "Prototype"

import os.path
import sys
from urllib import urlencode
from xml.sax.saxutils import escape, quoteattr

SETUP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SETUP_DIR)

import pdt

DOCTYPE = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">"""

def format_url(url, args):
	return (url + '?' + urlencode(args)) if args else url

@pdt.template
def render(loc, items, add_url, cancel_url, finish_url, menu_url, active_item=None, **kw):
	"""{doctype}
<html>
	<head>
		<title>Local Stock: Audit</title>
		<script type="text/javascript">
	""".format(doctype=DOCTYPE)
	"""
			function init() {
				document.item_form.item.focus();
			}
	"""
	"""
		</script>
	</head>
	<body onload="init();">
	"""
	
	# Header.
	"""
		<div id="header">
			<h1>Audit: {loc}</h1>
			<form id="item_form" name="item_form" method="GET" action={add_url}>
				<div class="hidden">
	""".format(
		loc=escape(loc),
		add_url=quoteattr(add_url[0])
	)
	for k, v in add_url[1]:
		"""
					<input type="hidden" name={key} value={value}/>
		""".format(key=quoteattr(k), value=quoteattr(v))
	"""
				</div>
				<table cellpadding="0" cellspacing="0">
					<tr>
						<td class="first">Item</td>
						<td>
							<input name="item" type="text" size="16"/>
						</td>
						<td>
							<input type="submit" value="ADD"/>
						</td>
					</tr>
				</table>
			</form>
			<table class="actions">
				<tr>
					<td><a href={cancel_url}>Cancel</a></td>
					<td class="right"><a href={finish_url}>Finish</a></td>
				</tr>
			</table>
		</div>
	""".format(
		cancel_url=quoteattr(format_url(*cancel_url)),
		finish_url=quoteattr(format_url(*finish_url))
	)
	
	# Items.
	if items:
		"""
		<table class="items" cellpadding="0" cellspacing="0">
		"""
		for i, item in enumerate(items):
			row_classes = ['item']
			if not i:
				row_classes.append('first')
			elif i == 2:
				row_classes.append('error')
				
			if item['sku'] == active_item:
				# Active item.
				row_classes.append('active')
				"""
			<tr class={row_classes}>
				<td class="cell">
					<table cellpadding="0" cellspacing="0">
						<tr>
							<td class="inc"><a href={inc_url}><img src="/static/inc_12.gif" alt="+"/></a></td>
						</tr>
						<tr>
							<td class="qty">{qty}</td>
						</tr>
						<tr>
							<td class="dec"><a href={dec_url}><img src="/static/dec_12.gif" alt="-"/></a></td>
						</tr>
					</table>
				</td>
				<td class="cell">
					<table cellpadding="0" cellspacing="0">
						<tr>
							<td class="sku">{sku}</td>
							<td class="brand">{brand}</td>
						</tr>
						<tr>
							<td class="title" colspan="2">{title}</td>
						</tr>
					</table>
				</td>
			</tr>
				""".format(
					row_classes=quoteattr(' '.join(row_classes)),
					inc_url=quoteattr(format_url(*item['inc_url'])),
					dec_url=quoteattr(format_url(*item['dec_url'])),
					item_url=quoteattr(format_url(*item['item_url'])),
					qty=escape(str(item['qty'])),
					sku=escape(item['sku']),
					brand=escape(item['brand']),
					title=escape(item['title'])
				)
				
			else:
				# Inactive item.
				"""
			<tr class={row_classes}>
				<td class="cell qty">{qty}</td>
				<td class="cell">
					<table cellpadding="0" cellspacing="0">
						<tr>
							<td class="sku">{sku}</td>
							<td class="brand">{brand}</td>
						</tr>
						<tr>
							<td class="title" colspan="2">{title}</td>
						</tr>
					</table>
				</td>
			</tr>
				""".format(
					row_classes=quoteattr(' '.join(row_classes)),
					qty=escape(str(item['qty'])),
					sku=escape(item['sku']),
					brand=escape(item['brand']),
					title=escape(item['title'])
				)
				
		"""
		</table>
		"""
		
	else:
		# No items.
		"""
		<div class="items">
			<h1>No Items Scanned</h1>	
		</div>
		"""
	raise Exception("an error")
	# Footer.
	"""
		<div id="footer">
			<table class="actions" cellpadding="0" cellspacing="0">
				<tr>
					<td><a href={cancel_url}>Cancel</a></td>
					<td class="right"><a href={finish_url}>Finish</a></td>
				</tr>
				<tr>
					<td class="center" colspan="2"><a href={menu_url}>Back to Menu</a></td>
				</tr>
			</table>
		</div>
	""".format(
		cancel_url=quoteattr(format_url(*cancel_url)),
		finish_url=quoteattr(format_url(*finish_url)),
		menu_url=quoteattr(format_url(*menu_url))
	)
	"""
	</body>
</html>"""

def main():
	loc = '123456789'
	data = {}
	data['menu_url'] = ('/', [])
	data['loc'] = loc
	data['add_url'] = ('/audit', [('loc', loc), ('action', 'add')])
	data['finish_url'] = ('/audit', [('loc', loc), ('action', 'finish')])
	data['cancel_url'] = ('/audit', [('loc', loc), ('action', 'cancel')])
	data['active_item'] = 'SS-333-006-03-16'
	data['items'] = [
		{'qty': 1, 'sku': "SS-333-006-03-16", 'brand': "Scorpian", 'title': "Scorpion Vision Vest"},
		{'qty': 2, 'sku': "0103-0065", 'brand': "Z1R", 'title': "Z1R Nomad Ghost Flames Half Helmet"},
		{'qty': 3, 'sku': "SU-356-1002", 'brand': "Joe Rocket", 'title': "Joe Rocket Highside Leather Gloves"},
		{'qty': 4, 'sku': "SU-901-109", 'brand': "HJC", 'title': "HJC Coolmax Balaclava"},
		{'qty': 5, 'sku': "WP-352-0100YS", 'brand': "Fly Racing", 'title': "Fly Racing Youth Dropping Bombs Tee"},
		{'qty': 6, 'sku': "0130-0003", 'brand': "Suomy", 'title': "Suomy Ventura Helmet Shield"},
		{'qty': 7, 'sku': "TR-817420", 'brand': "Arai", 'title': "Arai Signet-Q Racer Full Face Helmet"},
		{'qty': 8, 'sku': "WP-460-99225", 'brand': "Hmk", 'title': "Hmk Alpine Billed Knit Beanie"},
		{'qty': 9, 'sku': "2830-0058", 'brand': "Alpinestars", 'title': "Alpinestars Stealth Vest"},
		{'qty': 10, 'sku': "1533-30-02", 'brand': "Icon", 'title': "Icon Motorhead Leather Jacket"}
	]
	for item in data['items']:
		item['item_url'] = ('/item', [('sku', 'SS-333-006-03-16')])
		item['inc_url'] = ('/audit', [('loc', loc), ('action', 'item_inc')])
		item['dec_url'] = ('/audit', [('loc', loc), ('action', 'item_dec')])

	print render(**data)
	
	return 0

if __name__ == '__main__':
	exit(main())
