#!/usr/bin/env python3

import unittest

from networkx import graphml

from commons import ASSERT
from commons import dom_enumerate_xpaths, pg_enumerate_xpaths
from commons import pg_top_document_root
from commons import pg_find_node_by_xpath
from commons import pg_node_check_predecessors
from commons import pg_node_check_successors

class TestInlineScript(unittest.TestCase):
	def test_inline_script(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")
		g_nodes = g.nodes(data=True)

		# TODO: Don't rely on xpaths.
		top_dom_root = pg_top_document_root(g)
		html_script_node = pg_find_node_by_xpath(g,
				top_dom_root, "/html/body/script")
		self.assertIsNotNone(html_script_node)

		# Check predecessors of |html_script_node|.
		predecessors = list(g.predecessors(html_script_node))
		self.assertEqual(len(predecessors), 2)
		html_script_node_checks = {
				"parser": [lambda x: x["node type"] == "parser", None],
				"body": [lambda x: x["node type"] == "html node" and \
						x["tag name"] == "body", None],
			}
		pg_node_check_predecessors(g,
				html_script_node, html_script_node_checks)
		self.assertIsNotNone(html_script_node_checks["parser"][1] and \
				html_script_node_checks["body"][1])

		# Check successors of |html_script_node|.
		self.assertEqual(len(g[html_script_node]), 2)
		html_script_node_checks = {
				"text node": [lambda x: x["node type"] == "text node", None],
				"script": [lambda x: x["node type"] == "script", None],
			}
		pg_node_check_successors(g, html_script_node, html_script_node_checks)
		script_text_node = html_script_node_checks["text node"][1]
		script_node = html_script_node_checks["script"][1]
		self.assertIsNotNone(script_text_node)
		self.assertIsNotNone(script_node)

		# Verify we have the expected script content.
		script_text = g_nodes[script_text_node]["text"]
		self.assertNotEqual(script_text.find("This is a testing script"), -1)

		# Check the successors of |script_node|.
		self.assertEqual(len(g[script_node]), 2)
		script_node_checks = {
				"heading": [lambda x: x["text"] == "Big Title", None],
				"content": [lambda x: x["text"] == "Lorem Ipsum", None],
			}
		pg_node_check_successors(g, script_node, script_node_checks)
		heading_node = script_node_checks["heading"][1]
		content_node = script_node_checks["content"][1]
		self.assertIsNotNone(heading_node)
		self.assertIsNotNone(content_node)

if __name__ == "__main__":
	unittest.main()

