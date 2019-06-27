#!/usr/bin/env python3

import unittest

from networkx import graphml

from commons import pg_node_check_predecessors
from commons import pg_node_check_successors
from commons import pg_find_html_element_node
from commons import generate_html_element_id_selector

class TestLocalRemoteIFrames(unittest.TestCase):
	def test_local_remote_iframes(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")
		g_nodes = g.nodes(data=True)

		iframe_nodes = pg_find_html_element_node(g, "iframe",
				generate_html_element_id_selector("local_iframe"))
		self.assertEqual(len(iframe_nodes), 1)
		local_iframe_node = iframe_nodes[0]

		iframe_nodes = pg_find_html_element_node(g, "iframe",
				generate_html_element_id_selector("remote_iframe"))
		self.assertEqual(len(iframe_nodes), 1)
		remote_iframe_node = iframe_nodes[0]

		# Check successors of |local_iframe_node|.
		s = list(g.successors(local_iframe_node))
		self.assertEqual(len(s), 1)
		s = s[0]
		self.assertEqual(g_nodes[s]["node type"], "local frame")

		s = list(g.successors(s))
		self.assertEqual(len(s), 1)
		s = s[0]
		self.assertEqual(g_nodes[s]["node type"], "dom root")

		# Check successors of |remote_iframe_node|.
		#
		# We have no control how many content frames will be created
		# when we visit, say, google.com. So the below just checks
		# that all frame nodes are remote, and that they have no children.
		for s in list(g.successors(remote_iframe_node)):
			self.assertEqual(g_nodes[s]["node type"], "remote frame")
			self.assertEqual(len(list(g.successors(s))), 0)

if __name__ == "__main__":
	unittest.main()

