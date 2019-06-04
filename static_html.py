#!/usr/bin/env python3

import sys
import unittest

from inspect import getframeinfo, stack
from networkx import graphml
from lxml import etree

def ASSERT(cond):
	if not cond:
		caller = getframeinfo(stack()[1][0])
		print("\n[-]: ASSERT failed: {0}, line {1}\n".format(
				caller.filename, caller.lineno))
		sys.exit(-1)

def dom_enumerate_xpaths(dom_node, parent_xpath, xpaths):
	current_xpath = parent_xpath + "/{0}".format(dom_node.tag)
	dom_children = dom_node.getchildren()
	if dom_children:
		for dom_child in dom_children:
			dom_enumerate_xpaths(dom_child, current_xpath, xpaths)
	else:
		xpaths.append(current_xpath)

def pg_enumerate_xpaths(pg, pg_node, parent_xpath, xpaths):
	pg_nodes = pg.nodes(data=True)
	current_xpath = parent_xpath + "/{0}".format(
			pg_nodes[pg_node]["tag name"])

	pg_children = list(pg[pg_node].keys())
	has_tag_children = False
	for pg_child in pg_children:
		if not "tag name" in pg_nodes[pg_child]:
			continue
		has_tag_children = True
		pg_enumerate_xpaths(pg, pg_child, current_xpath, xpaths)
	if not has_tag_children:
		xpaths.append(current_xpath)

class TestStringMethods(unittest.TestCase):
	def test_static_html(self):
		g = graphml.read_graphml("/tmp/pagegraph.log")
		nodes = g.nodes(data=True)

		# Find the "root" node.
		root = None
		for n, d in nodes:
			if "tag name" in d and d["tag name"] == "(root)":
				root = n
				break

		# Get the <html> node.
		ASSERT(len(g[root]) == 1)
		html = list(g[root].keys())[0]
		ASSERT("tag name" in nodes[html] and nodes[html]["tag name"] == "html")

		pg_xpaths = []
		pg_enumerate_xpaths(g, html, "", pg_xpaths)
		pg_xpaths.sort()
		#print("PG xpaths:\n")
		#for xpath in pg_xpaths:
		#	print(xpath)
		#print()

		# Parse the original page html for DOM.
		with open("static.html", "r") as f:
			dom_root = etree.parse(f)
		dom_html = dom_root.xpath("/html")[0]

		dom_xpaths = []
		dom_enumerate_xpaths(dom_html, "", dom_xpaths)
		dom_xpaths.sort()
		#print("DOM xpaths:\n")
		#for xpath in dom_xpaths:
		#	print(xpath)
		#print()

		self.assertEqual(pg_xpaths, dom_xpaths)


if __name__ == "__main__":
	unittest.main()

