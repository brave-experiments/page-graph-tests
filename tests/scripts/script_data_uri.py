# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_edge_data,
    pg_edge_in,
    pg_edge_out,
    pg_edges_directly_leading_to_with_edge_type,
    pg_find_html_element_node,
    pg_nodes_directly_leading_to_with_edge_type,
)

def test(page_graph, html, tab):
    div_nodes = pg_find_html_element_node(page_graph, 'div', lambda page_graph, node: True)
    assert len(div_nodes) == 1

    div_node = div_nodes[0]

    div_create_nodes = pg_nodes_directly_leading_to_with_edge_type(page_graph, div_node, 'create')
    assert len(div_create_nodes) == 1

    data_uri_script_node = div_create_nodes[0]
    assert page_graph.nodes[data_uri_script_node]['node type'] == 'script'

    data_uri_script_execute_nodes = pg_nodes_directly_leading_to_with_edge_type(
        page_graph, data_uri_script_node, 'execute'
    )
    assert len(data_uri_script_execute_nodes) == 1

    data_uri_script_elem_node = data_uri_script_execute_nodes[0]
    assert page_graph.nodes[data_uri_script_elem_node]['node type'] == 'html node'
    assert page_graph.nodes[data_uri_script_elem_node]['tag name'] == 'script'

    data_uri_script_elem_attr_set_edges = pg_edges_directly_leading_to_with_edge_type(
        page_graph, data_uri_script_elem_node, 'attr set'
    )
    assert len(data_uri_script_elem_attr_set_edges) == 1

    data_uri_script_elem_attr_set_edge = data_uri_script_elem_attr_set_edges[0]
    assert data_uri_script_elem_attr_set_edge['data']['key'] == 'src'
    assert data_uri_script_elem_attr_set_edge['data']['value'].startswith('data:')
    assert page_graph.nodes[data_uri_script_elem_attr_set_edge['from']]['node type'] == 'script'
