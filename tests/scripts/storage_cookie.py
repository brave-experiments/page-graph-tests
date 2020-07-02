# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_html_element_node,
    pg_find_static_node,
    pg_edges_data_from_to,
    generate_script_text_selector,
)

def test(page_graph, html, tab, headless):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('document.cookie')
    )

    # should be exactly one script node with document.cookie
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    storage_node = pg_find_static_node(page_graph, 'cookie jar')

    script_successors = list(page_graph.successors(script_node))

    # should be exactly two successors to the script node
    # (the text node with the code, and the actual script)
    assert len(script_successors) == 2

    execute_script_node = script_successors[1]
    script_to_cookie_edges = pg_edges_data_from_to(page_graph, execute_script_node, storage_node)

    # should be exactly three edges script->cookie
    assert len(script_to_cookie_edges) == 3

    expected_structure_script_to_cookie = [
        {'key': 'awesomeKey', 'value': 'awesomeValue'},
        {'key': 'anotherKey', 'value': 'anotherValue'},
        {'key': 'http://localhost:8080/storage_cookie.html'},
    ]

    # verify the script->cookie set edges contain the correct data
    for i in range(2):
        assert script_to_cookie_edges[i]['key'] == expected_structure_script_to_cookie[i]['key']
        assert (
            script_to_cookie_edges[i]['value'] == expected_structure_script_to_cookie[i]['value']
        )

    # verify the script->cookie read call edge contain the correct data
    assert script_to_cookie_edges[2]['key'] == expected_structure_script_to_cookie[2]['key']

    cookie_to_script_edge = pg_edges_data_from_to(page_graph, storage_node, execute_script_node)

    # should be exactly one edge cookie->script
    assert len(cookie_to_script_edge) == 1

    expected_structure_cookie_to_script = [
        {
            'key': 'http://localhost:8080/storage_cookie.html',
            'value': 'awesomeKey=awesomeValue; anotherKey=anotherValue',
        }
    ]

    # check the structure...
    assert cookie_to_script_edge[0]['key'] == expected_structure_cookie_to_script[0]['key']
    assert cookie_to_script_edge[0]['value'] == expected_structure_cookie_to_script[0]['value']
