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

def test(page_graph, html, tab):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('localStorage')
    )

    # should be exactly one script node with document.cookie
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    storage_node = pg_find_static_node(page_graph, 'local storage')

    script_successors = list(page_graph.successors(script_node))

    # should be exactly two successors to the script node
    # (the text node with the code, and the actual script)
    assert len(script_successors) == 2

    execute_script_node = script_successors[1]
    edges_script_to_local = pg_edges_data_from_to(page_graph, execute_script_node, storage_node)

    # should be exactly five edges with data
    assert len(edges_script_to_local) == 5

    expected_structure_script_to_local = [
        {'key': 'myCat', 'value': 'Tom'},
        {'key': 'myMouse', 'value': 'Jerry'},
        {'key': 'myCat'},
        {'key': 'myCat'},
        {},
    ]

    # verify the edges contain the correct data
    for i in range(len(edges_script_to_local)):
        # all but storage clear have defined keys
        if i != len(edges_script_to_local) - 1:
            assert edges_script_to_local[i]['key'] == expected_structure_script_to_local[i]['key']

        # set edges also have a value
        if i < 2:
            assert (
                edges_script_to_local[i]['value'] == expected_structure_script_to_local[i]['value']
            )

    # get the local->script edge(s)
    edges_local_to_script = pg_edges_data_from_to(page_graph, storage_node, execute_script_node)

    # should be exactly one edge storage->script
    assert len(edges_local_to_script) == 1

    expected_structure_local_to_script = [
        {'key': 'myCat', 'value': 'Tom'}
    ]

    # check the edge
    assert edges_local_to_script[0]['key'] == expected_structure_local_to_script[0]['key']
    assert edges_local_to_script[0]['value'] == expected_structure_local_to_script[0]['value']
