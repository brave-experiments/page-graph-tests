# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_edge_data,
    pg_edge_in,
    pg_edge_out,
    pg_find_html_element_node,
    pg_top_document_root,
    pg_get_node_data,
)

def test(page_graph, html, tab):
    form = pg_find_html_element_node(page_graph, 'form', lambda page_graph, node: True)[0]
    expected_edge_type = 'add event listener'
    event_edge_in = [
        edge
        for edge in page_graph.in_edges(form, data=True)
        if pg_edge_data(edge, 'edge type') == expected_edge_type
    ]

    assert len(event_edge_in) == 1
    event_edge_in = event_edge_in[0]

    parser_node = list(page_graph.nodes)[0]
    assert parser_node == pg_edge_out(event_edge_in)
    assert form == pg_edge_in(event_edge_in)

    # check the edge from the form to the event handler
    expected_edge_type_out = 'event listener'
    event_edge_out = [
        edge
        for edge in page_graph.out_edges(form, data=True)
        if pg_edge_data(edge, 'edge type') == expected_edge_type_out
    ]
    assert len(event_edge_out) == 1
    event_edge_out = event_edge_out[0]

    event_function_node = pg_find_html_element_node(
        page_graph, 'script', lambda page_graph, node: True
    )[0]
    successors = list(page_graph.successors(event_function_node))
    assert len(successors) == 2  # the text node, and a script node
    # actual_function_node = successors[1]

    # form has an edge from itself to the event handler
    assert form == pg_edge_out(event_edge_out)
    # assert actual_function_node == pg_edge_in(event_edge_out)

    # it should be the same event listener id on the two edges
    assert pg_edge_data(event_edge_in, 'event listener id') == pg_edge_data(
        event_edge_out, 'event listener id'
    )
