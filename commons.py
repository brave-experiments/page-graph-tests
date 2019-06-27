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

def pg_enumerate_xpaths_with_action(pg, pg_node, parent_xpath,
		action, cross_dom):
	pg_nodes = pg.nodes(data=True)
	current_xpath = parent_xpath + "/{0}".format(
			pg_nodes[pg_node]["tag name"])

	pg_children = list(pg[pg_node].keys())
	is_leaf = True
	for pg_child in pg_children:
		if not "tag name" in pg_nodes[pg_child]:
			if cross_dom and "node type" in pg_nodes[pg_child] and \
					pg_nodes[pg_child]["node type"] == "local frame":
				pg_grandchildren = list(pg[pg_child].keys())
				ASSERT(len(pg_grandchildren) == 1)
				# pg_grandchildren[0] is the dom root node.
				pg_enumerate_xpaths_with_action(pg,
						_dom_root_html(pg, pg_grandchildren[0]),
						current_xpath, action, True)
			else:
				continue
		else:
			pg_enumerate_xpaths_with_action(pg, pg_child,
					current_xpath, action, cross_dom)
		is_leaf = False

	if is_leaf:
		action(current_xpath, pg_node)

def pg_enumerate_xpaths(pg, top_dom_root, cross_dom=False):
	xpaths = []
	def action(xpath, pg_node):
		xpaths.append(xpath)

	pg_enumerate_xpaths_with_action(pg, _dom_root_html(pg, top_dom_root),
			"", action, cross_dom)
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

def pg_find_node_by_xpath(pg, top_dom_root, xpath, cross_dom=False):
	node = None
	def action(p, pg_node):
		nonlocal node
		if p == xpath:
			node = pg_node

	pg_enumerate_xpaths_with_action(pg, _dom_root_html(pg, top_dom_root),
			"", action, cross_dom)
	return node

def _do_pg_node_checks(pg, nodes, node_checks):
	for node in nodes:
		for check_name, e in node_checks.items():
			if e[1]:
				continue  # Already checked.
			if e[0](node):
				e[1] = node
				break

def pg_node_check_successors(pg, pg_node, node_checks):
	_do_pg_node_checks(pg, pg.successors(pg_node), node_checks)

def pg_node_check_predecessors(pg, pg_node, node_checks):
	_do_pg_node_checks(pg, pg.predecessors(pg_node), node_checks)

def generate_script_text_selector(search_text, exclude_text=None):
	def selector_prototype(pg, n):
		pg_nodes = pg.nodes(data=True)
		for adj in pg[n].keys():
			if pg_nodes[adj]["node type"] == "text node":
				text = pg_nodes[adj]["text"]
				if text.find(search_text) != -1:
					if exclude_text and text.find(exclude_text) != -1:
						continue
					return True
		return False
	return selector_prototype

# TODO: Also account for attribute deletion.
def generate_html_element_id_selector(node_id):
	def selector_prototype(pg, n):
		for p in pg.predecessors(n):
			for e, d in pg[p][n].items():
				if d["edge type"] == "attr set" and \
						"key" in d and d["key"] == "id" and \
						"value" in d and d["value"] == node_id:
					return True
		return False
	return selector_prototype

def pg_find_html_element_node(pg, tag_name, selector):
	script_nodes = []
	for n, e in pg.nodes(data=True):
		if e["node type"] == "html node" and e["tag name"] == tag_name:
			script_nodes.append(n)

	ret = []
	for n in script_nodes:
		if selector(pg, n):
			ret.append(n)
	return ret

