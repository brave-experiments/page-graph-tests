# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_static_node,
    pg_find_html_element_node,
    generate_script_text_selector,
    pg_edges_data_from_to,
    pg_nodes_directly_reachable_from,
)

def test(page_graph, html, tab, headless):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('screen.')
    )
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]
    # check so all the nodes directly reachable from the script goes to different screen nodes
    all_screen_nodes = pg_nodes_directly_reachable_from(page_graph, executing_node)
    assert len(all_screen_nodes) == 8

    # check the call edges
    for i in range(0, len(all_screen_nodes)):
        edges = pg_edges_data_from_to(page_graph, executing_node, all_screen_nodes[i])
        # should at most two call edges to each screen node (`colorDepth` and
        # `pixelDepth` are synonyms)
        assert len(edges) >= 1 and len(edges) <= 2
        edge = edges[0]
        # should be exactly 3 keys (type, id, timestamp)
        assert len(edge) == 3
        assert edge['edge type'] == 'js call'
        assert 'id' in edge and 'timestamp' in edge

    # check the result edges
    for i in range(0, len(all_screen_nodes)):
        edges = pg_edges_data_from_to(page_graph, all_screen_nodes[i], executing_node)
        # should be at most two result edges from each screen node
        assert len(edges) >= 1 and len(edges) <= 2
        edge = edges[0]
        # should be exactly 4 keys (type, id, timestamp, value)
        assert len(edge) == 4
        assert edge['edge type'] == 'js result'
        assert edge['value'] == str(int(edge['value']))
        assert 'id' in edge and 'timestamp' in edge
