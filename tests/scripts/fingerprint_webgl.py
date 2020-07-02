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

def test(page_graph, html, tab, headless):
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
    # length should be 4 (1 is getContext, the rest are the 3 different webgl functions)
    assert len(all_nodes_unique) == 4

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

    for node in all_nodes_unique:
        edges = pg_edges_data_from_to(page_graph, executing_node, node)
        if len(edges) == 2:
            # this can be either getExtension or getParameter to webgl2
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js call'
                try:
                    pos = get_extension_args.index(edges[i]['args'])
                except ValueError:
                    assert False

                del get_extension_args[pos]
        elif len(edges) == 36:
            # getShaderPrecisionFormat
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js call'
                try:
                    pos = shader_args.index(edges[i]['args'])
                except ValueError:
                    assert False

                del shader_args[pos]

        elif len(edges) == 1:
            # getContext
            assert edges[0]['edge type'] == 'js call'
            assert edges[0]['args'].startswith('webgl')
        elif len(edges) == 26:
            # getParameter to webgl
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js call'
                try:
                    pos = get_parameter_args.index(edges[i]['args'])
                except ValueError:
                    assert False

                del get_parameter_args[pos]
        else:
            # something went bad
            assert False

    # result edges...
    for node in all_nodes_unique:
        edges = pg_edges_data_from_to(page_graph, node, executing_node)
        if len(edges) == 2:
            # this can be either getExtension or getParameter to webgl2
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js result'
        elif len(edges) == 36:
            # getShaderPrecisionFormat
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js result'
        elif len(edges) == 1:
            # getContext
            assert edges[0]['edge type'] == 'js result'
        elif len(edges) == 26:
            # getParameter to webgl
            for i in range(0, len(edges)):
                assert edges[i]['edge type'] == 'js result'
        else:
            # something went bad
            assert False
