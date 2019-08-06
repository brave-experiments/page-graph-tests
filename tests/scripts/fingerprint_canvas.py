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
import networkx

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

    script_nodes_is_point_in_path = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('isPointInPath')
    )
    assert len(script_nodes_is_point_in_path) == 1

    script_node_to_data_url = script_nodes_to_data_url[0]
    script_node_to_blob = script_nodes_to_blob[0]
    script_node_measure_text = script_nodes_measure_text[0]
    script_node_is_point_in_path = script_nodes_is_point_in_path[0]

    successors_to_data_url = list(page_graph.successors(script_node_to_data_url))
    assert len(successors_to_data_url) == 2  # since we are an inline script tag

    successors_measure_text = list(page_graph.successors(script_node_measure_text))
    assert len(successors_measure_text) == 2  # since we are an inline script tag

    successors_to_blob = list(page_graph.successors(script_node_to_blob))
    assert len(successors_to_blob) == 2  # since we are an inline script tag

    successors_is_point_in_path = list(page_graph.successors(script_node_is_point_in_path))
    assert len(successors_is_point_in_path) == 2  # since we are an inline script tag

    # check so all the nodes directly reachable from each script goes to the correct canvas node
    executing_node_to_data_url = successors_to_data_url[1]
    canvas_to_data_url_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_to_data_url, 'js call'
    )
    # should be two, one edge to the 'getContext' call, and one for the 'toDataURL' node
    assert len(canvas_to_data_url_node) == 2

    edge_get_context = edges = pg_edges_data_from_to(
        page_graph, executing_node_to_data_url, canvas_to_data_url_node[0]
    )
    assert len(edge_get_context) == 1
    edge_get_context = edge_get_context[0]
    assert edge_get_context['edge type'] == 'js call'
    assert (
        edge_get_context['args']
        == '2d, alpha: 1, antialias: 1, color_space: "srgb", depth: 1, fail_if_major_performance_caveat: 0, desynchronized: 0, pixel_format: "uint8", premultiplied_alpha: 1, preserve_drawing_buffer: 0, power_preference: "default", stencil: 0, xr_compatible: 0'
    )
    canvas_get_context_web_api_node = page_graph.node[canvas_to_data_url_node[0]]
    assert canvas_get_context_web_api_node['method'] == 'HTMLCanvasElement.getContext'

    edge_to_data_url = pg_edges_data_from_to(
        page_graph, executing_node_to_data_url, canvas_to_data_url_node[1]
    )
    assert len(edge_to_data_url) == 1
    edge_to_data_url = edge_to_data_url[0]
    assert edge_to_data_url['edge type'] == 'js call'
    assert edge_to_data_url['args'] == 'image/jpeg, 0.500000'

    canvas_get_data_web_api_node = page_graph.node[canvas_to_data_url_node[1]]
    assert canvas_get_data_web_api_node['method'] == 'HTMLCanvasElement.toDataURL'

    executing_node_to_blob = successors_to_blob[1]
    canvas_to_blob_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_to_blob, 'js call'
    )
    assert len(canvas_to_blob_node) == 2

    edges = pg_edges_data_from_to(page_graph, executing_node_to_blob, canvas_to_blob_node[1])
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js call'
    assert edge['args'] == 'V8BlobCallback, image/png, -1.000000'

    canvas_to_blob_web_api_node = page_graph.node[canvas_to_blob_node[1]]
    assert canvas_to_blob_web_api_node['method'] == 'HTMLCanvasElement.toBlob'

    executing_node_measure_text = successors_measure_text[1]
    canvas_measure_text_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_measure_text, 'js call'
    )
    assert len(canvas_measure_text_node) == 2

    edges = pg_edges_data_from_to(
        page_graph, executing_node_measure_text, canvas_measure_text_node[1]
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js call'
    assert edge['args'] == 'Hello world'

    canvas_measure_text_web_api_node = page_graph.node[canvas_measure_text_node[1]]
    assert canvas_measure_text_web_api_node['method'] == 'CanvasRenderingContext2D.measureText'

    executing_node_is_point_in_path = successors_is_point_in_path[1]
    canvas_is_point_in_path_node = pg_nodes_directly_reachable_from_with_edge_type(
        page_graph, executing_node_is_point_in_path, 'js call'
    )

    assert len(canvas_is_point_in_path_node) == 1

    edges = pg_edges_data_from_to(
        page_graph, executing_node_is_point_in_path, canvas_is_point_in_path_node[0]
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js call'
    assert edge['args'] == '5.000000, 5.000000, evenodd'

    canvas_is_point_in_path_web_api_node = page_graph.node[canvas_is_point_in_path_node[0]]
    assert canvas_is_point_in_path_web_api_node['method'] == 'CanvasRenderingContext2D.isPointInPath'

    # result edges
    edges = pg_edges_data_from_to(
        page_graph, canvas_to_data_url_node[0], executing_node_to_data_url
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js result'
    assert edge['value'] == 'CanvasRenderingContext: 2d'

    edges = pg_edges_data_from_to(
        page_graph, canvas_to_data_url_node[1], executing_node_to_data_url
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js result'
    assert edge['value'].startswith('data:image/jpeg;base64,')

    edges = pg_edges_data_from_to(page_graph, canvas_to_blob_node[1], executing_node_to_blob)
    assert len(edges) == 0

    edges = pg_edges_data_from_to(
        page_graph, canvas_measure_text_node[1], executing_node_measure_text
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js result'
    assert edge['value'].startswith('width: ')

    edges = pg_edges_data_from_to(
        page_graph, canvas_is_point_in_path_node[0], executing_node_is_point_in_path
    )
    assert len(edges) == 1
    edge = edges[0]
    assert edge['edge type'] == 'js result'
    assert edge['value'] == 'false'
