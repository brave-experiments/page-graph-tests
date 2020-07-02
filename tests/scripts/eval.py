# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import (
    dom_enumerate_xpaths,
    generate_script_text_selector,
    pg_enumerate_xpaths,
    pg_find_html_element_node,
    pg_node_check_predecessors,
    pg_node_check_successors,
    pg_node_id_mapping,
    pg_top_document_root,
)

def test(page_graph, html, tab, headless):
    page_graph_nodes = page_graph.nodes(data=True)
    id_mapping = pg_node_id_mapping(page_graph)

    script_nodes = pg_find_html_element_node(
        page_graph, 'script', generate_script_text_selector('eval("var script = ')
    )

    assert len(script_nodes) == 1
    html_script_node = script_nodes[0]

    script_nodes = pg_find_html_element_node(
        page_graph,
        'script',
        generate_script_text_selector('var title = document.getElementById', exclude_text='eval'),
    )
    assert len(script_nodes) == 1
    eval_script_node = script_nodes[0]

    # Check predecessors of |html_script_node|.
    predecessors = list(page_graph.predecessors(html_script_node))
    assert len(predecessors) == 2
    html_script_node_checks = {
        'parser': [lambda x: page_graph_nodes[x]['node type'] == 'parser', None],
        'body': [
            lambda x: page_graph_nodes[x]['node type'] == 'HTML element'
            and page_graph_nodes[x]['tag name'] == 'body',
            None,
        ],
    }
    pg_node_check_predecessors(page_graph, html_script_node, html_script_node_checks)
    assert html_script_node_checks['parser'][1] is not None
    assert html_script_node_checks['body'][1] is not None

    # Check predecessors of |eval_script_node|

    # TODO: Check other edges of |html_script_node|'s script node.
    def check_script_actor(pn):
        if (
            page_graph_nodes[pn]['node type'] == 'script'
            and list(page_graph.predecessors(pn))[0] == html_script_node
        ):
            # Check that |eval_script_node|'s text node was
            # only inserted once.
            for n in page_graph.successors(eval_script_node):
                if page_graph_nodes[n]['node type'] == 'text node':
                    eval_script_text_node = n
                    break
            insert_edges = []
            for e, d in page_graph[pn][eval_script_text_node].items():
                if d['edge type'] != 'insert node':
                    continue
                parent_id = d['parent']
                assert parent_id in id_mapping
                p = id_mapping[parent_id]
                if (
                    page_graph_nodes[p]['node type'] == 'HTML element'
                    and page_graph_nodes[p]['tag name'] == '#document-fragment'
                ):
                    continue
                insert_edges.append(e)
            if len(insert_edges) == 1:
                return True
        return False

    predecessors = list(page_graph.predecessors(eval_script_node))
    assert len(predecessors) == 2
    eval_script_node_checks = {
        'body': [
            lambda x: page_graph_nodes[x]['node type'] == 'HTML element'
            and page_graph_nodes[x]['tag name'] == 'body',
            None,
        ],
        'script_actor': [check_script_actor, None],
    }
    pg_node_check_predecessors(page_graph, eval_script_node, eval_script_node_checks)
    assert eval_script_node_checks['body'][1] is not None
    assert eval_script_node_checks['script_actor'][1] is not None

    # Check successors of |eval_script_node|.
    assert len(page_graph[eval_script_node]) == 2
    eval_script_node_checks = {
        'text node': [lambda x: page_graph_nodes[x]['node type'] == 'text node', None],
        'script': [lambda x: page_graph_nodes[x]['node type'] == 'script', None],
    }
    pg_node_check_successors(page_graph, eval_script_node, eval_script_node_checks)
    script_text_node = eval_script_node_checks['text node'][1]
    script_node = eval_script_node_checks['script'][1]
    assert script_text_node is not None
    assert script_node is not None

    # Check the successors of |script_node|, i.e., |eval_script_node|'s
    # script node..
    assert len(page_graph[script_node]) == 1
    script_node_checks = {'heading': [lambda x: page_graph_nodes[x]['text'] == 'Big Title', None]}
    pg_node_check_successors(page_graph, script_node, script_node_checks)
    assert script_node_checks['heading'][1] is not None
