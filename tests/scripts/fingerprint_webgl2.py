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
    webgl_node = pg_find_static_node(page_graph, 'WebGL')
    assert webgl_node != None

    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('webgl')
    )

    assert len(script_nodes) == 1

    script_node = script_nodes[0]

    successors = list(page_graph.successors(script_node))
    assert len(successors) == 2  # since we are an inline script tag

    executing_node = successors[1]
    edges_script_to_webgl = pg_edges_data_from_to(page_graph, executing_node, webgl_node)
    # we make 28 calls to webgl in total (26 to getParameter, 2 to getExtension, and 36 to getContextAttributes)
    assert len(edges_script_to_webgl) == 64

    # result edges...
    edges_webgl_to_script = pg_edges_data_from_to(page_graph, webgl_node, executing_node)
    assert len(edges_webgl_to_script) == 64

    # check edges script --> webgl node
    function_args = [
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
        'WEBGL_debug_renderer_info',
        'ext.UNMASKED_VENDOR_WEBGL',
        'ext.UNMASKED_RENDERER_WEBGL',
        'EXT_texture_filter_anisotropic',
        'ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT',
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

    for i in range(0, len(edges_script_to_webgl)):
        assert edges_script_to_webgl[i]['edge type'] == 'webapi call'
        if i > 27:
            assert edges_script_to_webgl[i]['key'] == 'getShaderPrecisionFormat'
        elif i == 23 or i == 26:
            assert edges_script_to_webgl[i]['key'] == 'getExtension'
        else:
            assert edges_script_to_webgl[i]['key'] == 'getParameter'
        assert edges_script_to_webgl[i]['args'] == function_args[i]

    # check edges webgl node --> script
    expected_results = [
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
        'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)',
        None,
        'WebKit',
        'WebGL 2.0 (OpenGL ES 3.0 Chromium)',
        None,
        'Google Inc.',
        'Google SwiftShader',
        None,
        None,
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
    for i in range(0, len(edges_webgl_to_script)):
        assert edges_webgl_to_script[i]['edge type'] == 'webapi result'
        if i > 27:
            assert edges_webgl_to_script[i]['key'] == 'getShaderPrecisionFormat'
        elif i == 23 or i == 26:
            assert edges_webgl_to_script[i]['key'] == 'getExtension'
        else:
            assert edges_webgl_to_script[i]['key'] == 'getParameter'
        if i == 18 or i == 19 or i == 21 or i == 22 or i == 24 or i == 25 or i > 27:
            assert edges_webgl_to_script[i]['value'] == expected_results[i]
