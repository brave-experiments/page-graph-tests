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
    navigator_node = pg_find_static_node(page_graph, 'Navigator')
    assert navigator_node != None

    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('navigator.')
    )
    assert len(script_nodes) == 1

    script_node = script_nodes[0]
    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]
    edges_script_to_navigator = pg_edges_data_from_to(page_graph, executing_node, navigator_node)
    assert len(edges_script_to_navigator) == 7

    edges_navigator_to_script = pg_edges_data_from_to(page_graph, navigator_node, executing_node)
    assert len(edges_navigator_to_script) == 7

    # all outgoing edges should look the same aside from the function
    # called, and since the argument list is empty, it won't be a key
    # in edges_script_to_navigator
    called_navigator_functions = [
        'userAgent',
        'language',
        'languages',
        'plugins',
        'doNotTrack',
        'cookieEnabled',
        'platform',
    ]
    for i in range(0, len(edges_script_to_navigator)):
        assert edges_script_to_navigator[i]['edge type'] == 'webapi call'
        assert edges_script_to_navigator[i]['key'] == called_navigator_functions[i]
        try:
            edges_script_to_navigator[i]['args']
            assert False
        except KeyError:
            assert True

    # all result edges should look the same aside from the function
    # called and the actual result. In this case, since plugins and
    # doNotTrack returns empty results, the key 'value' will not be
    # interpreted in Python
    expected_results = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/75.0.67.70 Safari/537.36',
        'en-US',
        'en-US',
        None,
        None,
        'true',
        'MacIntel',
    ]
    for i in range(0, len(edges_navigator_to_script)):
        assert edges_navigator_to_script[i]['edge type'] == 'webapi result'
        assert edges_navigator_to_script[i]['key'] == called_navigator_functions[i]
        if i < 3 or i > 4:
            assert edges_navigator_to_script[i]['value'] == expected_results[i]
        else:
            try:
                edges_navigator_to_script[i]['value']
                assert False
            except KeyError:
                assert True
