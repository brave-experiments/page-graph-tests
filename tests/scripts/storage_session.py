#!/usr/bin/env python3

from test_utils import (
    pg_top_document_root,
    pg_find_html_element_node,
    pg_find_storage_node,
    pg_edges_data_from_to,
    generate_script_text_selector,
)

def test(page_graph, html, tab):
    top_dom_root = pg_top_document_root(page_graph)
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('sessionStorage')
    )

    # should be exactly one script node with document.cookie
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    storage_node = pg_find_storage_node(page_graph, 'session storage')

    script_successors = list(page_graph.successors(script_node))

    # should be exactly two successors to the script node
    # (the text node with the code, and the actual script)
    assert len(script_successors) == 2

    execute_script_node = script_successors[1]
    edges_script_to_session = pg_edges_data_from_to(page_graph, execute_script_node, storage_node)

    # should be exactly five edges with data
    assert len(edges_script_to_session) == 5

    expected_structure_script_to_session = [
        {'key': 'myCat', 'edge type': 'storage set', 'value': 'Tom'},
        {'key': 'myMouse', 'edge type': 'storage set', 'value': 'Jerry'},
        {'key': 'myCat', 'edge type': 'storage read call'},
        {'key': 'myCat', 'edge type': 'storage delete'},
        {'edge type': 'storage clear'},
    ]

    # verify the edges contain the correct data
    for i in range(len(edges_script_to_session)):
        # edge types and keys should always be the same
        assert (
            edges_script_to_session[i]['edge type']
            == expected_structure_script_to_session[i]['edge type']
        )

        # all but storage clear have defined keys
        if edges_script_to_session[i]['edge type'] != 'storage clear':
            assert (
                edges_script_to_session[i]['key'] == expected_structure_script_to_session[i]['key']
            )

        # set edges also have a value
        if edges_script_to_session[i]['edge type'] == 'storage set':
            assert (
                edges_script_to_session[i]['value']
                == expected_structure_script_to_session[i]['value']
            )

    # get the session->script edge(s)
    edges_session_to_script = pg_edges_data_from_to(page_graph, storage_node, execute_script_node)

    # should be exactly one edge storage->script
    assert len(edges_session_to_script) == 1

    expected_structure_session_to_script = [
        {'key': 'myCat', 'edge type': 'storage read result', 'value': 'Tom'}
    ]

    # check the edge
    assert edges_session_to_script[0]['key'] == expected_structure_session_to_script[0]['key']
    assert (
        edges_session_to_script[0]['edge type']
        == expected_structure_session_to_script[0]['edge type']
    )
    assert edges_session_to_script[0]['value'] == expected_structure_session_to_script[0]['value']
