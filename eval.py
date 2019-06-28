#!/usr/bin/env python3

import unittest

from networkx import graphml

from commons import ASSERT
from commons import pg_node_id_mapping
from commons import pg_node_check_predecessors
from commons import pg_node_check_successors
from commons import pg_find_html_element_node
from commons import generate_script_text_selector

class TestEval(unittest.TestCase):
	def test_eval(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")
		g_nodes = g.nodes(data=True)
		id_mapping = pg_node_id_mapping(g)

		script_nodes = pg_find_html_element_node(g, "script",
				generate_script_text_selector("eval(\"var script = "))
		self.assertEqual(len(script_nodes), 1)
		html_script_node = script_nodes[0]

		script_nodes = pg_find_html_element_node(g, "script",
				generate_script_text_selector(
					"var title = document.getElementById",
					exclude_text="eval"))
		self.assertEqual(len(script_nodes), 1)
		eval_script_node = script_nodes[0]

		# Check predecessors of |html_script_node|.
		predecessors = list(g.predecessors(html_script_node))
		self.assertEqual(len(predecessors), 2)
		html_script_node_checks = {
				"parser": [lambda x:
					g_nodes[x]["node type"] == "parser", None],
				"body": [lambda x:
					g_nodes[x]["node type"] == "html node" and \
					g_nodes[x]["tag name"] == "body", None],
			}
		pg_node_check_predecessors(g,
				html_script_node, html_script_node_checks)
		self.assertIsNotNone(html_script_node_checks["parser"][1] and \
				html_script_node_checks["body"][1])

		#
		# Check predecessors of |eval_script_node|
		#

		# TODO: Check other edges of |html_script_node|'s script node.
		def check_script_actor(pn):
			if g_nodes[pn]["node type"] == "script" and \
					list(g.predecessors(pn))[0] == html_script_node:
				# Check that |eval_script_node|'s text node was
				# only inserted once.
				for n in g.successors(eval_script_node):
					if g_nodes[n]["node type"] == "text node":
						eval_script_text_node = n
						break
				insert_edges = []
				for e, d in g[pn][eval_script_text_node].items():
					if d["edge type"] != "insert":
						continue
					parent_id = d["parent"]
					self.assertTrue(parent_id in id_mapping)
					p = id_mapping[parent_id]
					if g_nodes[p]["node type"] == "html node" and \
							g_nodes[p]["tag name"] == "#document-fragment":
						continue
					insert_edges.append(e)
				if len(insert_edges) == 1:
					return True
			return False

		predecessors = list(g.predecessors(eval_script_node))
		self.assertEqual(len(predecessors), 2)
		eval_script_node_checks = {
				"body": [lambda x:
					g_nodes[x]["node type"] == "html node" and \
					g_nodes[x]["tag name"] == "body", None],
				"script_actor": [check_script_actor, None],
			}
		pg_node_check_predecessors(g,
				eval_script_node, eval_script_node_checks)
		self.assertIsNotNone(eval_script_node_checks["body"][1] and \
				eval_script_node_checks["script_actor"][1])

		# Check successors of |eval_script_node|.
		self.assertEqual(len(g[eval_script_node]), 2)
		eval_script_node_checks = {
				"text node": [lambda x:
					g_nodes[x]["node type"] == "text node", None],
				"script": [lambda x:
					g_nodes[x]["node type"] == "script", None],
			}
		pg_node_check_successors(g, eval_script_node, eval_script_node_checks)
		script_text_node = eval_script_node_checks["text node"][1]
		script_node = eval_script_node_checks["script"][1]
		self.assertIsNotNone(script_text_node)
		self.assertIsNotNone(script_node)

		# Check the successors of |script_node|, i.e., |eval_script_node|'s
		# script node..
		self.assertEqual(len(g[script_node]), 1)
		script_node_checks = {
				"heading": [lambda x: g_nodes[x]["text"] == "Big Title", None],
			}
		pg_node_check_successors(g, script_node, script_node_checks)
		self.assertIsNotNone(script_node_checks["heading"][1])

if __name__ == "__main__":
	unittest.main()

