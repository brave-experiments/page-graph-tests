# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_html_element_node,
    pg_find_node,
    pg_node_check_predecessors,
    pg_node_check_successors,
    pg_node_id_mapping,
)

def test(page_graph, html, tab):
    page_graph_nodes = page_graph.nodes(data=True)
    id_mapping = pg_node_id_mapping(page_graph)

    link_nodes = pg_find_html_element_node(page_graph, 'link')
    assert len(link_nodes) == 1
    html_link_node = link_nodes[0]

    # Check the successors of |html_link_node|.
    successors = list(page_graph.successors(html_link_node))
    assert len(successors) == 1
    html_link_node_checks = {
        'css': [
            lambda x: 'node type' in page_graph_nodes[x]
            and page_graph_nodes[x]['node type'] == 'resource'
            and 'url' in page_graph_nodes[x]
            and page_graph_nodes[x]['url'].endswith('css_image.css'),
            None,
        ]
    }
    pg_node_check_successors(page_graph, html_link_node, html_link_node_checks)

    # Check the image request resulting from CSS.
    res_nodes = pg_find_node(
        page_graph,
        'resource',
        selector=lambda pg, n: 'url' in page_graph_nodes[n]
        and page_graph_nodes[n]['url'].endswith('css_image.png'),
    )
    assert len(res_nodes) == 1
    img_res_node = res_nodes[0]

    ## Check predecessors of |img_res_node| (should be only parser).
    img_res_node_checks = {
        'parser': [lambda x: page_graph_nodes[x]['node type'] == 'parser', None]
    }
    pg_node_check_predecessors(page_graph, img_res_node, img_res_node_checks)
