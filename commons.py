#!/usr/bin/env python3

import sys

from networkx import graphml
from lxml import etree

from inspect import getframeinfo, stack

def ASSERT(cond):
	if not cond:
		caller = getframeinfo(stack()[1][0])
		print("\n[-]: ASSERT failed: {0}, line {1}\n".format(
				caller.filename, caller.lineno))
		sys.exit(-1)

def _do_dom_enumerate_xpaths(dom_node, parent_xpath, xpaths, cross_dom):
	current_xpath = parent_xpath + "/{0}".format(dom_node.tag)

	if cross_dom and dom_node.tag == "iframe" and \
			"src" in dom_node.attrib:
		sub_xpaths = dom_enumerate_xpaths(
				dom_node.attrib["src"], True)
		for p in sub_xpaths:
			xpaths.append("{0}{1}".format(current_xpath, p))
		else:
			# If |cross_dom|, and iframe has a child, then iframe is not leaf.
			return

	dom_children = dom_node.getchildren()
	if dom_children:
		for dom_child in dom_children:
			_do_dom_enumerate_xpaths(dom_child,
					current_xpath, xpaths, cross_dom)
	else:
		xpaths.append(current_xpath)

def dom_enumerate_xpaths(html_path, cross_dom=False):
	with open(html_path, "r") as f:
		dom_root = etree.parse(f)

	xpaths = []
	_do_dom_enumerate_xpaths(dom_root.xpath("/html")[0], "", xpaths, cross_dom)
	xpaths.sort()
	return xpaths

def _dom_root_html(pg, dom_root):
	root_html = list(pg[dom_root].keys())[0]
	ASSERT("tag name" in pg.nodes(data=True)[root_html])
	ASSERT(pg.nodes(data=True)[root_html]["tag name"] == "html")
	return root_html

def _do_pg_enumerate_xpaths(pg, pg_node, parent_xpath, xpaths, cross_dom):
	pg_nodes = pg.nodes(data=True)
	current_xpath = parent_xpath + "/{0}".format(
			pg_nodes[pg_node]["tag name"])

	pg_children = list(pg[pg_node].keys())
	is_leaf = True
	for pg_child in pg_children:
		if not "tag name" in pg_nodes[pg_child]:
			if cross_dom and "node type" in pg_nodes[pg_child] and \
					pg_nodes[pg_child]["node type"] == "dom root":
				_do_pg_enumerate_xpaths(pg, _dom_root_html(pg, pg_child),
						current_xpath, xpaths, True)
			else:
				continue
		else:
			_do_pg_enumerate_xpaths(pg, pg_child,
					current_xpath, xpaths, cross_dom)
		is_leaf = False

	if is_leaf:
		xpaths.append(current_xpath)

def pg_enumerate_xpaths(pg, top_dom_root, cross_dom=False):
	xpaths = []
	_do_pg_enumerate_xpaths(pg, _dom_root_html(pg, top_dom_root),
			"", xpaths, cross_dom)
	xpaths.sort()
	return xpaths

def pg_top_document_root(pg):
	dom_roots = set()
	for n, d in pg.nodes(data=True):
		if "node type" in d and d["node type"] == "dom root" and pg[n]:
			dom_roots.add(n)

	# The top document root should have no predecessor other
	# than the parser node.
	for e in pg.edges:
		if e[1] in dom_roots and e[0] != "n1":
			dom_roots.remove(e[1])

	ASSERT(len(dom_roots) == 1)
	return dom_roots.pop()

