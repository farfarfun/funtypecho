"""公开 API 的本地边界测试。"""

from xmlrpc.client import Fault

import pytest

from funtypecho import Post, Typecho
from funtypecho.publish.core import PostAll


def test_rpc_response_and_empty_response():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    assert client._try_rpc(lambda *args: "") is None
    assert client._try_rpc(lambda *args: {"id": 1}) == {"id": 1}


def test_rpc_fault_has_context():
    client = Typecho("http://example.test/xmlrpc", "u", "p")

    def fail(*args):
        raise Fault(403, "denied")

    with pytest.raises(RuntimeError, match="403.*denied"):
        client._try_rpc(fail)


def test_publish_rejects_unknown_extension():
    publisher = PostAll.__new__(PostAll)
    with pytest.raises(ValueError, match="不支持"):
        publisher.post("notes.txt", [])


def test_post_model_is_typed():
    assert Post(title="title", description="body").categories == []
