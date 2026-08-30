"""Minimal smoke test for funtypecho.

Only verifies that the package imports cleanly. funtypecho.main builds an
xmlrpc.client.ServerProxy, but only inside Typecho.__init__ -- importing
the module itself performs no network I/O.
"""


def test_import():
    import funtypecho

    assert funtypecho is not None
    assert funtypecho.Typecho is not None
