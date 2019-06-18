#!/usr/bin/env python3

import unittest

from networkx import graphml

from commons import ASSERT
from commons import dom_enumerate_xpaths, pg_enumerate_xpaths
from commons import pg_top_document_root

class TestStaticHTML(unittest.TestCase):
	def test_static_html(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")

		top_dom_root = pg_top_document_root(g)
		pg_xpaths = pg_enumerate_xpaths(g, top_dom_root)
		#print(pg_xpaths)

		dom_xpaths = dom_enumerate_xpaths("static_page.html")
		#print(dom_xpaths)

		self.assertEqual(pg_xpaths, dom_xpaths)

if __name__ == "__main__":
	unittest.main()

