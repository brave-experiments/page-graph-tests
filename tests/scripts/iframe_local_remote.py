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
    assert len(s) == 3
    # Check that we have the empty-frame DOM root that |local_iframe_node| is
    # initialized with.
    assert page_graph_nodes[s[0]]['node type'] == 'DOM root'
    assert page_graph_nodes[s[0]]['url'] == 'about:blank'
    # Check that we have the DOM root it gets when the local page loads.
    assert page_graph_nodes[s[1]]['node type'] == 'DOM root'
    assert page_graph_nodes[s[1]]['url'].endswith('/static_page.html')
    # Check that we have the remote frame it gets when the remote page loads
    # (after swapping frame srcs).
    assert page_graph_nodes[s[2]]['node type'] == 'remote frame'
    assert page_graph_nodes[s[2]]['url'] == 'https://example.com/'

    # Check successors of |remote_iframe_node|.
    s = list(page_graph.successors(remote_iframe_node))
    assert len(s) == 3
    # Check that we have the empty-frame DOM root that |remote_iframe_node| is
    # initialized with.
    assert page_graph_nodes[s[0]]['node type'] == 'DOM root'
    assert page_graph_nodes[s[0]]['url'] == 'about:blank'
    # Check that we have the remote frame it gets when the static page loads.
    assert page_graph_nodes[s[1]]['node type'] == 'remote frame'
    assert page_graph_nodes[s[1]]['url'] == 'https://example.com/'
    # Check that we have the DOM root it gets when the local page loads (after
    # swapping frame srcs).
    assert page_graph_nodes[s[2]]['node type'] == 'DOM root'
    assert page_graph_nodes[s[2]]['url'].endswith('/static_page.html')
