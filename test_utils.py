# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from lxml import etree
import os
import posixpath

root_dir_path = os.path.dirname(os.path.realpath(__file__))
tests_dir_path = os.path.join(root_dir_path, 'tests')
test_html_dir_path = os.path.join(tests_dir_path, 'html')

def _do_dom_enumerate_xpaths(dom_node, parent_xpath, xpaths, cross_dom):
    current_xpath = parent_xpath + '/{0}'.format(dom_node.tag)

    if cross_dom and dom_node.tag == 'iframe' and 'src' in dom_node.attrib:
        framed_page_file_path = os.path.join(
            test_html_dir_path, posixpath.relpath(dom_node.attrib['src'], start='/')
        )
        with open(framed_page_file_path, 'r', encoding='utf-8') as framed_page_file:
            framed_page_html = framed_page_file.read()

        sub_xpaths = dom_enumerate_xpaths(framed_page_html, True)
        for p in sub_xpaths:
            xpaths.append('{0}{1}'.format(current_xpath, p))
        else:
            # If |cross_dom|, and iframe has a child, then iframe is not leaf.
            return

    dom_children = dom_node.getchildren()
    if dom_children:
        for dom_child in dom_children:
            _do_dom_enumerate_xpaths(dom_child, current_xpath, xpaths, cross_dom)
    else:
        xpaths.append(current_xpath)

def dom_enumerate_xpaths(html, cross_dom=False):
    dom_root = etree.fromstring(html)

    xpaths = []
    _do_dom_enumerate_xpaths(dom_root.xpath('/html')[0], '', xpaths, cross_dom)
    xpaths.sort()

    return xpaths

def _dom_root_html(pg, dom_root):
    root_html = list(pg[dom_root].keys())[0]
    assert 'tag name' in pg.nodes(data=True)[root_html]
    assert pg.nodes(data=True)[root_html]['tag name'] == 'html'
    return root_html

def pg_enumerate_xpaths_with_action(pg, pg_node, parent_xpath, action, cross_dom):
    pg_nodes = pg.nodes(data=True)
    current_xpath = parent_xpath + '/{0}'.format(pg_nodes[pg_node]['tag name'])

    pg_children = list(pg[pg_node].keys())
    is_leaf = True

    for pg_child in pg_children:
        if not 'tag name' in pg_nodes[pg_child]:
            if (
                cross_dom
                and 'node type' in pg_nodes[pg_child]
                and pg_nodes[pg_child]['node type'] == 'local frame'
            ):
                pg_grandchildren = list(pg[pg_child].keys())
                assert len(pg_grandchildren) == 2  # includes initial empty doc
                # pg_grandchildren[0] is the dom root node.
                pg_enumerate_xpaths_with_action(
                    pg, _dom_root_html(pg, pg_grandchildren[1]), current_xpath, action, True
                )
            else:
                continue
        else:
            pg_enumerate_xpaths_with_action(pg, pg_child, current_xpath, action, cross_dom)
        is_leaf = False

    if is_leaf:
        action(current_xpath, pg_node)

def pg_enumerate_xpaths(pg, top_dom_root, cross_dom=False):
    xpaths = []
    def action(xpath, pg_node):
        xpaths.append(xpath)

    pg_enumerate_xpaths_with_action(pg, _dom_root_html(pg, top_dom_root), '', action, cross_dom)
    xpaths.sort()
    return xpaths

def pg_top_document_root(pg):
    dom_roots = set()
    for n, d in pg.nodes(data=True):
        if 'node type' in d and d['node type'] == 'dom root' and pg[n]:
            dom_roots.add(n)

    # The top document root should have no predecessor other
    # than the parser node.
    for e in pg.edges:
        if e[1] in dom_roots and e[0] != 'n1':
            dom_roots.remove(e[1])

    assert len(dom_roots) == 1
    return dom_roots.pop()

def pg_find_node_by_xpath(pg, top_dom_root, xpath, cross_dom=False):
    node = None
    def action(p, pg_node):
        nonlocal node
        if p == xpath:
            node = pg_node

    pg_enumerate_xpaths_with_action(pg, _dom_root_html(pg, top_dom_root), '', action, cross_dom)
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
            if pg_nodes[adj]['node type'] == 'text node':
                text = pg_nodes[adj]['text']
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
                if (
                    d['edge type'] == 'attr set'
                    and 'key' in d
                    and d['key'] == 'id'
                    and 'value' in d
                    and d['value'] == node_id
                ):
                    return True
        return False
    return selector_prototype

def pg_find_html_element_node(pg, tag_name, selector):
    script_nodes = []
    for n, e in pg.nodes(data=True):
        if e['node type'] == 'html node' and e['tag name'] == tag_name:
            script_nodes.append(n)

    ret = []
    for n in script_nodes:
        if selector(pg, n):
            ret.append(n)
    return ret

def pg_node_id_mapping(pg):
    ret = {}
    for n, e in pg.nodes(data=True):
        if 'node id' in e:
            ret[e['node id']] = n
    return ret

# static_node is one of the following: "cookie jar", "local storage",
# "session storage", "Canvas", "Navigator", "WebGL" and "Screen"
def pg_find_static_node(pg, static_node):
    for n, e in pg.nodes(data=True):
        if e['node type'] == static_node:
            return n

    return None

# returns all data on edges from from_node to to_node
def pg_edges_data_from_to(pg, from_node, to_node):
    data_from = []
    for from_n, to_n, data in pg.edges(data=True):
        if from_n == from_node and to_n == to_node:
            data_from.append(data)

    return data_from

def pg_nodes_directly_reachable_from(pg, from_node):
    nodes = []
    for from_n, to_n, _data in pg.edges(data=True):
        if from_n == from_node:
            nodes.append(to_n)

    return nodes

def pg_nodes_directly_reachable_from_with_edge_type(pg, from_node, edge_type):
    nodes = []
    for from_n, to_n, data in pg.edges(data=True):
        if from_n == from_node and data['edge type'] == edge_type:
            nodes.append(to_n)

    return nodes

def pg_get_node_data(pg, node):
    return pg.nodes[node]

def pg_edge_out(edge):
    return edge[0]

def pg_edge_in(edge):
    return edge[1]

def pg_edge_data(edge, key):
    return edge[2][key]
