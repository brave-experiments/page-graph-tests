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
)

def test(page_graph, html, tab):
    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('webgl')
    )

    assert len(script_nodes) == 1

    script_node = script_nodes[0]

    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]
    all_webgl_nodes = pg_nodes_directly_reachable_from(page_graph, executing_node)
    all_nodes_unique = sorted(set(all_webgl_nodes))
    # length should be 3 (we call 3 different webgl functions)
    assert len(set(all_nodes_unique)) == 3

    node_order = [
        'WebGLRenderingContext.getShaderPrecisionFormat',
        'WebGLRenderingContext.getParameter',
        'WebGLRenderingContext.getExtension',
    ]

    shader_args = [
        'gl.VERTEX_SHADER, gl.HIGH_FLOAT',
        'gl.VERTEX_SHADER, gl.HIGH_FLOAT',
        'gl.VERTEX_SHADER, gl.HIGH_FLOAT',
        'gl.VERTEX_SHADER, gl.MEDIUM_FLOAT',
        'gl.VERTEX_SHADER, gl.MEDIUM_FLOAT',
        'gl.VERTEX_SHADER, gl.MEDIUM_FLOAT',
        'gl.VERTEX_SHADER, gl.LOW_FLOAT',
        'gl.VERTEX_SHADER, gl.LOW_FLOAT',
        'gl.VERTEX_SHADER, gl.LOW_FLOAT',
        'gl.FRAGMENT_SHADER, gl.HIGH_FLOAT',
        'gl.FRAGMENT_SHADER, gl.HIGH_FLOAT',
        'gl.FRAGMENT_SHADER, gl.HIGH_FLOAT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT',
        'gl.FRAGMENT_SHADER, gl.LOW_FLOAT',
        'gl.FRAGMENT_SHADER, gl.LOW_FLOAT',
        'gl.FRAGMENT_SHADER, gl.LOW_FLOAT',
        'gl.VERTEX_SHADER, gl.HIGH_INT',
        'gl.VERTEX_SHADER, gl.HIGH_INT',
        'gl.VERTEX_SHADER, gl.HIGH_INT',
        'gl.VERTEX_SHADER, gl.MEDIUM_INT',
        'gl.VERTEX_SHADER, gl.MEDIUM_INT',
        'gl.VERTEX_SHADER, gl.MEDIUM_INT',
        'gl.VERTEX_SHADER, gl.LOW_INT',
        'gl.VERTEX_SHADER, gl.LOW_INT',
        'gl.VERTEX_SHADER, gl.LOW_INT',
        'gl.FRAGMENT_SHADER, gl.HIGH_INT',
        'gl.FRAGMENT_SHADER, gl.HIGH_INT',
        'gl.FRAGMENT_SHADER, gl.HIGH_INT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_INT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_INT',
        'gl.FRAGMENT_SHADER, gl.MEDIUM_INT',
        'gl.FRAGMENT_SHADER, gl.LOW_INT',
        'gl.FRAGMENT_SHADER, gl.LOW_INT',
        'gl.FRAGMENT_SHADER, gl.LOW_INT',
    ]

    get_parameter_args = [
        'gl.ALIASED_LINE_WIDTH_RANGE',
        'gl.ALIASED_POINT_SIZE_RANGE',
        'gl.ALPHA_BITS',
        'gl.BLUE_BITS',
        'gl.DEPTH_BITS',
        'gl.GREEN_BITS',
        'gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS',
        'gl.MAX_CUBE_MAP_TEXTURE_SIZE',
        'gl.MAX_FRAGMENT_UNIFORM_VECTORS',
        'gl.MAX_RENDERBUFFER_SIZE',
        'gl.MAX_TEXTURE_IMAGE_UNITS',
        'gl.MAX_TEXTURE_SIZE',
        'gl.MAX_VARYING_VECTORS',
        'gl.MAX_VERTEX_ATTRIBS',
        'gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS',
        'gl.MAX_VERTEX_UNIFORM_VECTORS',
        'gl.MAX_VIEWPORT_DIMS',
        'gl.RED_BITS',
        'gl.RENDERER',
        'gl.SHADING_LANGUAGE_VERSION',
        'gl.STENCIL_BITS',
        'gl.VENDOR',
        'gl.VERSION',
        'ext.UNMASKED_VENDOR_WEBGL',
        'ext.UNMASKED_RENDERER_WEBGL',
        'ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT',
    ]

    get_extension_args = ['WEBGL_debug_renderer_info', 'EXT_texture_filter_anisotropic']

    i = 0
    for node in all_nodes_unique:
        edges = pg_edges_data_from_to(page_graph, executing_node, node)
        # we make 64 calls to webgl in total (26 to getParameter, 2 to getExtension, and 36 to getContextAttributes)
        if i == 0:
            assert len(edges) == 36
            for j in range(0, len(edges)):
                assert edges[j]['edge type'] == 'webapi call'
                assert edges[j]['key'] == node_order[i]
                assert edges[j]['args'] == shader_args[j]
        elif i == 1:
            assert len(edges) == 26
            for j in range(0, len(edges)):
                assert edges[j]['edge type'] == 'webapi call'
                assert edges[j]['key'] == node_order[i]
                assert edges[j]['args'] == get_parameter_args[j]
        else:
            assert len(edges) == 2
            for j in range(0, len(edges)):
                assert edges[j]['edge type'] == 'webapi call'
                assert edges[j]['key'] == node_order[i]
                assert edges[j]['args'] == get_extension_args[j]

        i += 1

    # result edges...
    expected_result_shader = [
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 127, rangeMax: 127, precision: 23',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
        'rangeMin: 31, rangeMax: 30, precision: 0',
    ]

    expected_result_get_parameter = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        'WebKit WebGL',
        'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)',
        None,
        'WebKit',
        'WebGL 1.0 (OpenGL ES 2.0 Chromium)',
        'Google Inc.',
        'Google SwiftShader',
        None,
    ]

    i = 0
    for node in all_nodes_unique:
        edges = pg_edges_data_from_to(page_graph, node, executing_node)
        if i == 0:
            assert len(edges) == 36
            for j in range(0, len(edges)):
                assert edges[j]['edge type'] == 'webapi result'
                assert edges[j]['key'] == node_order[i]
                assert edges[j]['value'] == expected_result_shader[j]
        elif i == 1:
            assert len(edges) == 26
            for j in range(0, len(edges)):
                assert edges[j]['edge type'] == 'webapi result'
                assert edges[j]['key'] == node_order[i]
                if expected_result_get_parameter[j] != None:
                    assert edges[j]['value'] == expected_result_get_parameter[j]
                else:
                    assert len(edges[j]) == 2
        else:
            assert len(edges) == 2
            for j in range(0, len(edges)):
                # we can't convert the result values to strings...
                assert len(edges[j]) == 2
                assert edges[j]['edge type'] == 'webapi result'
                assert edges[j]['key'] == node_order[i]

        i += 1
