# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    pg_find_static_node,
    pg_find_html_element_node,
    generate_script_text_selector,
    pg_edges_data_from_to,
    pg_nodes_directly_reachable_from,
    pg_nodes_directly_reachable_from_with_edge_type,
)

def test(page_graph, html, tab):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('canvas')
    )

    assert len(script_nodes) == 3

    script_nodes_to_data_url = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('toDataURL')
    )
    assert len(script_nodes_to_data_url) == 1

    script_nodes_to_blob = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('toBlob')
    )
    assert len(script_nodes_to_blob) == 1

    script_nodes_measure_text = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('measureText')
    )
    assert len(script_nodes_measure_text) == 1

    script_node_to_data_url = script_nodes_to_data_url[0]
    script_node_to_blob = script_nodes_to_blob[0]
    script_node_measure_text = script_nodes_measure_text[0]

    successors_to_data_url = list(page_graph.successors(script_node_to_data_url))
    assert len(successors_to_data_url) == 2  # since we are an inline script tag

    successors_measure_text = list(page_graph.successors(script_node_measure_text))
    assert len(successors_measure_text) == 2  # since we are an inline script tag

    successors_to_blob = list(page_graph.successors(script_node_to_blob))
    assert len(successors_to_blob) == 2  # since we are an inline script tag

    # check so all the nodes directly reachable from each script goes to the correct canvas node
    executing_node_to_data_url = successors_to_data_url[1]
    canvas_to_data_url_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_to_data_url, 'webapi call'
    )
    assert len(canvas_to_data_url_node) == 1

    edges = pg_edges_data_from_to(
        page_graph, executing_node_to_data_url, canvas_to_data_url_node[0]
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'webapi call'
    assert edge['key'] == 'HTMLCanvasElement.toDataURL'
    assert edge['args'] == 'image/jpeg, 0.500000'

    executing_node_to_blob = successors_to_blob[1]
    canvas_to_blob_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_to_blob, 'webapi call'
    )
    assert len(canvas_to_blob_node) == 1

    edges = pg_edges_data_from_to(page_graph, executing_node_to_blob, canvas_to_blob_node[0])
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'webapi call'
    assert edge['key'] == 'HTMLCanvasElement.toBlob'
    assert edge['args'] == 'V8BlobCallback, image/png, -1.000000'

    executing_node_measure_text = successors_measure_text[1]
    canvas_measure_text_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_measure_text, 'webapi call'
    )
    assert len(canvas_measure_text_node) == 1

    edges = pg_edges_data_from_to(
        page_graph, executing_node_measure_text, canvas_measure_text_node[0]
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'webapi call'
    assert edge['key'] == 'CanvasRenderingContext2D.measureText'
    assert edge['args'] == 'Hello world'

    # result edges
    edges = pg_edges_data_from_to(
        page_graph, canvas_to_data_url_node[0], executing_node_to_data_url
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'webapi result'
    assert edge['key'] == 'HTMLCanvasElement.toDataURL'
    assert (
        edge['value']
        == 'data:image/jpeg;base64,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'
    )

    edges = pg_edges_data_from_to(page_graph, canvas_to_blob_node[0], executing_node_to_blob)
    assert len(edges) == 0

    edges = pg_edges_data_from_to(
        page_graph, canvas_measure_text_node[0], executing_node_measure_text
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'webapi result'
    assert edge['key'] == 'CanvasRenderingContext2D.measureText'
    assert (
        edge['value']
        == 'width: 49.4629, actualBoundingBoxLeft: -0.800781, actualBoundingBoxRight: 48.7402, fontBoundingBoxAscent: 9, fontBoundingBoxDescent: 2, actualBoundingBoxAscent: 7.1582, actualBoundingBoxDescent: 0.117188, emHeightAscent: 7.75, emHeightDescent: 2.25, hangingBaseline: 7.2, alphabeticBaseline: -0, ideographicBaseline: -2'
    )
