# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    dom_enumerate_xpaths,
    pg_enumerate_xpaths,
    pg_find_node_by_xpath,
    pg_node_check_predecessors,
    pg_node_check_successors,
    pg_top_document_root,
)

def test(page_graph, html, tab):
    page_graph_nodes = page_graph.nodes(data=True)

    # TODO: Don't rely on xpaths.
    top_dom_root = pg_top_document_root(page_graph)
    html_script_node = pg_find_node_by_xpath(page_graph, top_dom_root, '/html/body/script')
    assert html_script_node is not None

    # Check predecessors of |html_script_node|.
    predecessors = list(page_graph.predecessors(html_script_node))
    assert len(predecessors) == 2
    html_script_node_checks = {
        'parser': [lambda x: page_graph_nodes[x]['node type'] == 'parser', None],
        'body': [
            lambda x: page_graph_nodes[x]['node type'] == 'HTML element'
            and page_graph_nodes[x]['tag name'] == 'body',
            None,
        ],
    }
    pg_node_check_predecessors(page_graph, html_script_node, html_script_node_checks)
    assert html_script_node_checks['parser'][1] is not None
    assert html_script_node_checks['body'][1] is not None

    # Check successors of |html_script_node|.
    assert len(page_graph[html_script_node]) == 2
    html_script_node_checks = {
        'text node': [lambda x: page_graph_nodes[x]['node type'] == 'text node', None],
        'script': [lambda x: page_graph_nodes[x]['node type'] == 'script', None],
    }
    pg_node_check_successors(page_graph, html_script_node, html_script_node_checks)
    script_text_node = html_script_node_checks['text node'][1]
    script_node = html_script_node_checks['script'][1]
    assert script_text_node is not None
    assert script_node is not None

    # Verify we have the expected script content.
    script_text = page_graph_nodes[script_text_node]['text']
    assert script_text.find('This is a testing script') != -1

    # Check the successors of |script_node|.
    assert len(page_graph[script_node]) == 2
    script_node_checks = {
        'heading': [lambda x: page_graph_nodes[x]['text'] == 'Big Title', None],
        'content': [lambda x: page_graph_nodes[x]['text'] == 'Lorem Ipsum', None],
    }
    pg_node_check_successors(page_graph, script_node, script_node_checks)
    heading_node = script_node_checks['heading'][1]
    content_node = script_node_checks['content'][1]
    assert heading_node is not None
    assert content_node is not None
