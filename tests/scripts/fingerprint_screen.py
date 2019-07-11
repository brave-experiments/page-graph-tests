# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_static_node,
    pg_find_html_element_node,
    generate_script_text_selector,
    pg_edges_data_from_to,
)

def test(page_graph, html, tab):
    screen_node = pg_find_static_node(page_graph, 'Screen')
    assert screen_node != None

    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('screen.')
    )
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]
    edges_script_to_screen = pg_edges_data_from_to(page_graph, executing_node, screen_node)
    assert len(edges_script_to_screen) == 8

    edges_screen_to_script = pg_edges_data_from_to(page_graph, screen_node, executing_node)
    assert len(edges_screen_to_script) == 8

    # all outgoing edges should look the same aside from the function
    # called, and since the argument list is empty, it won't be a key
    # in edges_script_to_screen
    called_screen_functions = [
        'availWidth',
        'availHeight',
        'width',
        'height',
        'colorDepth',
        'pixelDepth',
        'availLeft',
        'availTop',
    ]
    for i in range(0, len(edges_script_to_screen)):
        assert edges_script_to_screen[i]['edge type'] == 'webapi call'
        assert edges_script_to_screen[i]['key'] == called_screen_functions[i]
        try:
            edges_script_to_screen[i]['args']
            assert False
        except KeyError:
            assert True

    # all result edges should look the same aside from the function
    # called and the actual result.
    expected_results = ['1680', '947', '1680', '1050', '24', '24', '0', '23']
    for i in range(0, len(edges_screen_to_script)):
        assert edges_screen_to_script[i]['edge type'] == 'webapi result'
        assert edges_screen_to_script[i]['key'] == called_screen_functions[i]
        assert edges_screen_to_script[i]['value'] == expected_results[i]
