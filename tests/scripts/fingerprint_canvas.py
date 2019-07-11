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
    canvas_node = pg_find_static_node(page_graph, 'Canvas')
    assert canvas_node != None

    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('canvas')
    )

    assert len(script_nodes) == 3

    script_node_to_data_url = script_nodes[0]
    script_node_to_blob = script_nodes[1]
    script_node_measure_text = script_nodes[2]

    successors_to_data_url = list(page_graph.successors(script_node_to_data_url))
    assert len(successors_to_data_url) == 2  # since we are an inline script tag

    successors_measure_text = list(page_graph.successors(script_node_measure_text))
    assert len(successors_measure_text) == 2  # since we are an inline script tag

    successors_to_blob = list(page_graph.successors(script_node_to_blob))
    assert len(successors_to_blob) == 2  # since we are an inline script tag

    executing_node_to_data_url = successors_to_data_url[1]
    edges_script_to_to_data_url = pg_edges_data_from_to(
        page_graph, executing_node_to_data_url, canvas_node
    )
    assert len(edges_script_to_to_data_url) == 1

    executing_node_to_blob = successors_to_blob[1]
    edges_script_to_blob = pg_edges_data_from_to(page_graph, executing_node_to_blob, canvas_node)
    assert len(edges_script_to_blob) == 1

    executing_node_measure_text = successors_measure_text[1]
    edges_script_measure_text = pg_edges_data_from_to(
        page_graph, executing_node_measure_text, canvas_node
    )
    assert len(edges_script_measure_text) == 1

    # result edges...
    edges_canvas_to_to_data_url_script = pg_edges_data_from_to(
        page_graph, canvas_node, executing_node_to_data_url
    )
    assert len(edges_canvas_to_to_data_url_script) == 1

    edges_canvas_to_to_blob = pg_edges_data_from_to(
        page_graph, canvas_node, executing_node_to_blob
    )
    assert len(edges_canvas_to_to_blob) == 0

    edges_canvas_to_measure_text_script = pg_edges_data_from_to(
        page_graph, canvas_node, executing_node_measure_text
    )
    assert len(edges_canvas_to_measure_text_script) == 1

    # check edges script --> canvas node
    edges_scripts_to_canvas = (
        edges_script_to_to_data_url + edges_script_to_blob + edges_script_measure_text
    )
    called_canvas_functions = ['toDataURL', 'toBlob', 'measureText']
    function_args = ['image/jpeg, 0.500000', 'V8BlobCallback, image/png, -1.000000', 'Hello world']
    for i in range(0, len(edges_scripts_to_canvas)):
        assert edges_scripts_to_canvas[i]['edge type'] == 'webapi call'
        assert edges_scripts_to_canvas[i]['key'] == called_canvas_functions[i]
        assert edges_scripts_to_canvas[i]['args'] == function_args[i]

    # check edges canvas node --> script (note that edges_canvas_to_to_blob is empty, so we ignore it)
    edges_canvas_to_scripts = (
        edges_canvas_to_to_data_url_script + edges_canvas_to_measure_text_script
    )
    resulting_functions = ['toDataURL', 'measureText']
    expected_results = [
        'data:image/jpeg;base64,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',
        'width: 49.4629, actualBoundingBoxLeft: -0.800781, actualBoundingBoxRight: 48.7402, fontBoundingBoxAscent: 9, fontBoundingBoxDescent: 2, actualBoundingBoxAscent: 7.1582, actualBoundingBoxDescent: 0.117188, emHeightAscent: 7.75, emHeightDescent: 2.25, hangingBaseline: 7.2, alphabeticBaseline: -0, ideographicBaseline: -2',
    ]
    for i in range(0, len(edges_canvas_to_scripts)):
        assert edges_canvas_to_scripts[i]['edge type'] == 'webapi result'
        assert edges_canvas_to_scripts[i]['key'] == resulting_functions[i]
        assert edges_canvas_to_scripts[i]['value'] == expected_results[i]
