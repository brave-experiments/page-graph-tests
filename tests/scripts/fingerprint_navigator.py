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
    pg_get_node_data,
)

def test(page_graph, html, tab):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('navigator.')
    )
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]

    # check so all the nodes directly reachable from the script goes to different navigator nodes
    all_navigator_nodes = pg_nodes_directly_reachable_from(page_graph, executing_node)
    node_order = [
        'NavigatorID.userAgent',
        'NavigatorLanguage.language',
        'NavigatorLanguage.languages',
        'NavigatorPlugins.plugins',
        'Navigator.doNotTrack',
        'Navigator.cookieEnabled',
        'NavigatorID.platform',
    ]
    for i in range(0, len(all_navigator_nodes)):
        assert pg_get_node_data(page_graph, all_navigator_nodes[i])['node type'] == node_order[i]

    # check the call edges
    for i in range(0, len(all_navigator_nodes)):
        edges = pg_edges_data_from_to(page_graph, executing_node, all_navigator_nodes[i])
        # should only be one call edge to each navigator node
        assert len(edges) == 1
        edge = edges[0]
        # should be exactly 2 keys since there's no arguments
        assert len(edge) == 2
        assert edge['edge type'] == 'webapi call'
        assert edge['key'] == node_order[i]

    # check the result edges
    expected_results = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/75.0.67.70 Safari/537.36',
        'en-US',
        'en-US',
        None,
        None,
        'true',
        'MacIntel',
    ]
    for i in range(0, len(all_navigator_nodes)):
        edges = pg_edges_data_from_to(page_graph, all_navigator_nodes[i], executing_node)
        # should only be one result edge from each navigator node
        assert len(edges) == 1
        edge = edges[0]
        assert edge['edge type'] == 'webapi result'
        assert edge['key'] == node_order[i]
        if expected_results[i]:
            # should be exactly 3 keys (type, key and value)
            assert len(edge) == 3
            assert edge['value'] == expected_results[i]
        else:
            # should be exactly 2 keys (type, key), since we didn't return a value
            assert len(edge) == 2
