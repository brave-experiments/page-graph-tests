# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    generate_html_element_id_selector,
    pg_find_html_element_node,
    pg_node_check_predecessors,
    pg_node_check_successors,
)

def test(page_graph, html, tab):
    page_graph_nodes = page_graph.nodes(data=True)

    iframe_nodes = pg_find_html_element_node(
        page_graph, 'iframe', generate_html_element_id_selector('local_iframe')
    )
    assert len(iframe_nodes) == 1
    local_iframe_node = iframe_nodes[0]

    iframe_nodes = pg_find_html_element_node(
        page_graph, 'iframe', generate_html_element_id_selector('remote_iframe')
    )
    assert len(iframe_nodes) == 1
    remote_iframe_node = iframe_nodes[0]

    # Check successors of |local_iframe_node|.
    s = list(page_graph.successors(local_iframe_node))
    assert len(s) == 1
    s = s[0]
    assert page_graph_nodes[s]['node type'] == 'local frame'

    s = list(page_graph.successors(s))
    assert len(s) == 1
    s = s[0]
    assert page_graph_nodes[s]['node type'] == 'dom root'

    # Check successors of |remote_iframe_node|.
    #
    # We have no control how many content frames will be created
    # when we visit, say, google.com. So the below just checks
    # that all frame nodes are remote, and that they have no children.
    for s in list(page_graph.successors(remote_iframe_node)):
        assert page_graph_nodes[s]['node type'] == 'remote frame'
        assert len(list(page_graph.successors(s))) == 0
