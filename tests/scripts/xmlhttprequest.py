# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_html_element_node,
    generate_script_text_selector,
    pg_nodes_directly_reachable_from_with_edge_type,
    pg_edge_out,
    pg_edge_in,
    pg_edge_data,
    pg_get_node_data,
)
import networkx

def test(page_graph, html, tab):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('xhr')
    )
    assert len(script_nodes) == 1

    html_element = script_nodes[0]

    # there should be an execute edge to the actual script
    scripts = pg_nodes_directly_reachable_from_with_edge_type(page_graph, html_element, 'execute')
    assert len(scripts) == 1
    actual_script = scripts[0]

    # there should be a request start edge to a resource node,
    # as well as a request complete edge back
    all_edges_from_script = []
    all_edges_to_script = []
    for edge in page_graph.edges(data=True):
        if pg_edge_out(edge) == actual_script:
            all_edges_from_script.append(edge)
        elif pg_edge_in(edge) == actual_script:
            all_edges_to_script.append(edge)

    # we have on edge from the script...
    assert len(all_edges_from_script) == 1
    # ... and it should be a request start edge ...
    assert pg_edge_data(all_edges_from_script[0], 'edge type') == 'request start'
    # ... and the target should be a resource node.
    assert pg_get_node_data(page_graph, all_edges_from_script[0][1])['node type'] == 'resource'

    # we should have two edges coming to the script (execute and request complete)...
    assert len(all_edges_to_script) == 2
    for edge in all_edges_to_script:
        assert (
            pg_edge_data(edge, 'edge type') == 'execute'
            or pg_edge_data(edge, 'edge type') == 'request complete'
        )

    # ... where the edge from the resource should be a request complete
    resource_node = all_edges_from_script[0][1]
    for edge in all_edges_to_script:
        if pg_edge_out(edge) == resource_node:
            assert pg_edge_data(edge, 'edge type') == 'request complete'
