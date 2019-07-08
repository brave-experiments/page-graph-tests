# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

from test_utils import dom_enumerate_xpaths, pg_enumerate_xpaths, pg_top_document_root

def test(page_graph, html, tab):
    top_dom_root = pg_top_document_root(page_graph)
    pg_xpaths = pg_enumerate_xpaths(page_graph, top_dom_root, cross_dom=True)
    dom_xpaths = dom_enumerate_xpaths(html, cross_dom=True)
    assert pg_xpaths == dom_xpaths
