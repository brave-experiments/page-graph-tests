#!/usr/bin/env python3

import unittest

from networkx import graphml

from commons import ASSERT
from commons import dom_enumerate_xpaths, pg_enumerate_xpaths
from commons import pg_top_document_root
from commons import pg_find_node_by_xpath

class TestInlineScript(unittest.TestCase):
	def test_inline_script(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")
		g_nodes = g.nodes(data=True)

		top_dom_root = pg_top_document_root(g)
		html_script_node = pg_find_node_by_xpath(g,
				top_dom_root, "/html/body/script")
		self.assertIsNotNone(html_script_node)

		children = list(g[html_script_node].keys())
		self.assertEqual(len(children), 2)

		script_text_node = None
		script_node = None
		if g_nodes[children[0]]["node type"] == "text node":
			script_text_node = children[0]
			script_node = children[1]
		elif g_nodes[children[0]]["node type"] == "script":
			script_text_node = children[1]
			script_node = children[0]
		self.assertIsNotNone(script_text_node)
		self.assertIsNotNone(script_node)

		script_text = g_nodes[script_text_node]["text"]
		self.assertNotEqual(script_text.find("This is a testing script"), -1)

		children = list(g[script_node].keys())
		self.assertEqual(len(children), 2)

		heading_node = None
		content_node = None
		if g_nodes[children[0]]["text"] == "Big Title":
			heading_node = children[0]
			content_node = children[1]
		elif g_nodes[children[1]]["text"] == "Big Title":
			heading_node = children[1]
			content_node = children[0]
		self.assertIsNotNone(heading_node)
		self.assertIsNotNone(content_node)

if __name__ == "__main__":
	unittest.main()

