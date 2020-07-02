# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import pg_edge_data, pg_edge_in, pg_edge_out, pg_find_html_element_node

def test(page_graph, html, tab, headless):
    div_node = pg_find_html_element_node(page_graph, 'div', lambda page_graph, node: True)[0]

    relevant_edge_types = {'add event listener', 'remove event listener'}
    relevant_edges = [
        edge
        for edge in page_graph.in_edges(div_node, data=True)
        if pg_edge_data(edge, 'edge type') in relevant_edge_types
    ]
    relevant_edges.reverse()

    script_nodes = []
    script_ids = []

    event_listeners = {}

    def take_add_event_listener_edge(event_type):
        assert len(relevant_edges) > 0

        edge = relevant_edges.pop()
        assert pg_edge_data(edge, 'edge type') == 'add event listener'
        assert pg_edge_data(edge, 'key') == event_type

        event_listener_id = pg_edge_data(edge, 'event listener id')
        event_listener_script_id = pg_edge_data(edge, 'script id')
        assert event_listener_id not in event_listeners
        event_listeners[event_listener_id] = event_listener_script_id

        return edge

    def take_remove_event_listener_edge(event_type):
        assert len(relevant_edges) > 0

        edge = relevant_edges.pop()
        assert pg_edge_data(edge, 'edge type') == 'remove event listener'
        assert pg_edge_data(edge, 'key') == event_type

        event_listener_id = pg_edge_data(edge, 'event listener id')
        event_listener_script_id = pg_edge_data(edge, 'script id')
        assert event_listener_id in event_listeners
        assert event_listeners[event_listener_id] == event_listener_script_id
        del event_listeners[event_listener_id]

        return edge

    # Check the "add event listener" edges from the first script node.

    # addEventListener('click', foo):
    edge = take_add_event_listener_edge('click')
    script_nodes.append(pg_edge_out(edge))
    script_ids.append(page_graph.nodes[script_nodes[0]]['script id'])
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # A duplicate addEventListener('click', foo) call should be ignored here...

    # addEventListener('click', boundFoo):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', boundBoundFoo):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', bar):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', baz):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    assert len(event_listeners) == 5

    # Check the "remove event listener" edges from the first script node.

    # removeEventListener('click', foo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # A duplicate removeEventListener('click', foo) call should be ignored here...

    # removeEventListener('click', boundFoo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', boundBoundFoo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', bar):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', baz):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[0] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    assert len(event_listeners) == 0

    # Check the "add event listener" edges from the second script node.

    # addEventListener('click', foo):
    edge = take_add_event_listener_edge('click')
    script_nodes.append(pg_edge_out(edge))
    assert script_nodes.count(script_nodes[1]) == 1
    script_ids.append(page_graph.nodes[script_nodes[1]]['script id'])
    assert script_ids.count(script_ids[1]) == 1
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # A duplicate addEventListener('click', foo) call should be ignored here...

    # addEventListener('click', boundFoo):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', boundBoundFoo):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', boundBoundBoundFoo):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', bar):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # addEventListener('click', baz):
    edge = take_add_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    assert len(event_listeners) == 6

    # Check the "remove event listener" edges from the second script node.

    # removeEventListener('click', foo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # A duplicate removeEventListener('click', foo) call should be ignored here...

    # removeEventListener('click', boundFoo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', boundBoundFoo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', boundBoundBoundFoo):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', bar):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # removeEventListener('click', baz):
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[1] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    assert len(event_listeners) == 0

    # Check attribute event listener behavior for the third script node.

    # onclick = quux
    edge = take_add_event_listener_edge('click')
    script_nodes.append(pg_edge_out(edge))
    assert script_nodes.count(script_nodes[2]) == 1
    script_ids.append(page_graph.nodes[script_nodes[2]]['script id'])
    assert script_ids.count(script_ids[2]) == 1
    assert script_ids[2] == pg_edge_data(edge, 'script id')

    # onclick = foo (removing quux)
    edge = take_remove_event_listener_edge('click')
    assert script_nodes[2] == pg_edge_out(edge)
    assert script_ids[2] == pg_edge_data(edge, 'script id')

    # onclick = foo (adding foo)
    edge = take_add_event_listener_edge('click')
    assert script_nodes[2] == pg_edge_out(edge)
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # Check attribute event listener behavior for the fourth script node.

    # onclick = quux (removing foo)
    edge = take_remove_event_listener_edge('click')
    script_nodes.append(pg_edge_out(edge))
    assert script_nodes.count(script_nodes[3]) == 1
    script_ids.append(page_graph.nodes[script_nodes[3]]['script id'])
    assert script_ids.count(script_ids[3]) == 1
    assert script_ids[0] == pg_edge_data(edge, 'script id')

    # onclick = quux (adding quux)
    edge = take_add_event_listener_edge('click')
    assert script_nodes[3] == pg_edge_out(edge)
    assert script_ids[2] == pg_edge_data(edge, 'script id')
