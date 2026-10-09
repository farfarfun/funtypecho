"""公开 API 的本地边界测试。"""

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from xmlrpc.client import Fault

import pytest

from funtypecho import Attachment, Category, Comment, Page, Post, Typecho
from funtypecho.publish.core import PostAll, get_all_file


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


def test_rpc_transport_error_has_context():
    client = Typecho("http://example.test/xmlrpc", "u", "p")

    with pytest.raises(RuntimeError, match="unavailable"):
        client._try_rpc(Mock(side_effect=OSError("unavailable")))


def test_public_rpc_methods_pass_auth_and_payload():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    methods = SimpleNamespace(
        getRecentPosts=Mock(return_value=[]),
        newPost=Mock(return_value="12"),
        getCategories=Mock(return_value=[]),
    )
    wp = SimpleNamespace(
        getPages=Mock(return_value=[]),
        newCategory=Mock(return_value="3"),
        getMediaLibrary=Mock(return_value=[]),
        newComment=Mock(return_value={"comment_id": "4"}),
    )
    client.s = SimpleNamespace(metaWeblog=methods, wp=wp)

    post = Post(title="标题", description="正文")
    assert client.get_posts(5) == []
    assert client.new_post(post, publish=False) == "12"
    assert client.get_categories() == []
    assert client.get_pages() == []
    assert client.new_category(Category("Python")) == "3"
    assert client.get_attachments(post_id=2, mime_type="image/png", page_size=10) == []
    assert client.new_comment(Comment("内容"), post_id=2) == {"comment_id": "4"}

    methods.getRecentPosts.assert_called_once_with(1, "u", "p", 5)
    methods.newPost.assert_called_once_with(1, "u", "p", post, False)
    wp.getMediaLibrary.assert_called_once_with(
        1, "u", "p", {"parent_id": 2, "mime_type": "image/png", "number": 10}
    )


def test_edit_methods_add_remote_id():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    new_post = Mock(return_value="ok")
    client.s = SimpleNamespace(metaWeblog=SimpleNamespace(newPost=new_post))

    assert client.edit_post(Post("标题", "正文"), 7, True) == "ok"
    assert new_post.call_args.args[3]["postId"] == 7
    assert client.edit_page(Page("页面", "正文"), 8, False) == "ok"
    assert new_post.call_args.args[3]["postId"] == 8


def test_get_post_uses_post_id_first_without_blog_id():
    """`metaWeblog.getPost` 的真实参数顺序是 (post_id, username, password)，
    不带 blog_id，与其他方法不同；回归测试锁定这个修复。"""
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    get_post = Mock(return_value={"postid": "5"})
    client.s = SimpleNamespace(metaWeblog=SimpleNamespace(getPost=get_post))

    assert client.get_post(5) == {"postid": "5"}
    get_post.assert_called_once_with(5, "u", "p")


def test_get_post_empty_response_returns_none():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    client.s = SimpleNamespace(
        metaWeblog=SimpleNamespace(getPost=Mock(return_value=""))
    )
    assert client.get_post(404) is None


def test_del_post_sends_blogger_delete_post_full_signature():
    """`blogger.deletePost` 需要 (blog_id, post_id, username, password, publish)
    共 5 个参数且 post_id 在用户名密码之前；回归测试锁定这个修复。"""
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    delete_post = Mock(return_value=True)
    client.s = SimpleNamespace(blogger=SimpleNamespace(deletePost=delete_post))

    assert client.del_post(5) is True
    delete_post.assert_called_once_with(1, 5, "u", "p", True)


def test_del_post_propagates_fault():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    client.s = SimpleNamespace(
        blogger=SimpleNamespace(deletePost=Mock(side_effect=Fault(404, "not found")))
    )
    with pytest.raises(RuntimeError, match="404.*not found"):
        client.del_post(999)


def test_page_lifecycle_calls_expected_rpc_methods():
    """覆盖 get_page/new_page/del_page 的正常路径与参数结构。"""
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    get_page = Mock(return_value={"page_id": "9"})
    new_post = Mock(return_value="9")
    delete_page = Mock(return_value=True)
    client.s = SimpleNamespace(
        wp=SimpleNamespace(getPage=get_page, deletePage=delete_page),
        metaWeblog=SimpleNamespace(newPost=new_post),
    )

    assert client.get_page(9) == {"page_id": "9"}
    get_page.assert_called_once_with(1, 9, "u", "p")

    page = Page(title="页面", description="正文")
    assert client.new_page(page, True) == "9"
    new_post.assert_called_once_with(1, "u", "p", page, True)

    assert client.del_page(9) is True
    delete_page.assert_called_once_with(1, "u", "p", 9)


def test_get_page_empty_response_returns_none():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    client.s = SimpleNamespace(wp=SimpleNamespace(getPage=Mock(return_value="")))
    assert client.get_page(404) is None


def test_delete_and_detail_methods_pass_expected_arguments():
    """覆盖分类/评论删除、标签、附件详情与上传的正常路径与参数结构。"""
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    wp = SimpleNamespace(
        deleteCategory=Mock(return_value=True),
        deleteComment=Mock(return_value=True),
        getTags=Mock(return_value=[]),
        getMediaItem=Mock(return_value={"attachment_id": "3"}),
        uploadFile=Mock(return_value={"id": "3"}),
    )
    client.s = SimpleNamespace(wp=wp)

    assert client.del_category(2) is True
    wp.deleteCategory.assert_called_once_with(1, "u", "p", 2)

    assert client.del_comment(4) is True
    wp.deleteComment.assert_called_once_with(1, "u", "p", 4)

    assert client.get_tags() == []
    wp.getTags.assert_called_once_with(1, "u", "p")

    assert client.get_attachment(3) == {"attachment_id": "3"}
    wp.getMediaItem.assert_called_once_with(1, "u", "p", 3)

    attachment = Attachment(name="pic.png", bytes=BytesIO(b"data"))
    assert client.new_attachment(attachment) == {"id": "3"}
    wp.uploadFile.assert_called_once_with(1, "u", "p", attachment)


def test_delete_methods_empty_response_returns_none():
    """删除类方法在远端返回空串时应统一转为 None，而不是误判为删除失败。"""
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    client.s = SimpleNamespace(
        wp=SimpleNamespace(
            deleteCategory=Mock(return_value=""),
            deleteComment=Mock(return_value=""),
            deletePage=Mock(return_value=""),
        ),
        blogger=SimpleNamespace(deletePost=Mock(return_value="")),
    )

    assert client.del_category(1) is None
    assert client.del_comment(1) is None
    assert client.del_page(1) is None
    assert client.del_post(1) is None


def test_publish_rejects_unknown_extension():
    publisher = PostAll.__new__(PostAll)
    with pytest.raises(ValueError, match="不支持"):
        publisher.post("notes.txt", [])


def test_publish_accepts_empty_category_response():
    client = Typecho("http://example.test/xmlrpc", "u", "p")
    client.s = SimpleNamespace(
        metaWeblog=SimpleNamespace(getCategories=Mock(return_value=""))
    )

    assert PostAll(client).categories == []


def test_post_model_is_typed():
    assert Post(title="title", description="body").categories == []


class FakeTypecho:
    def __init__(self):
        self.posts = []
        self.created_categories = []

    def get_categories(self):
        return []

    def new_post(self, post, publish):
        self.posts.append((post, publish))
        return str(len(self.posts))

    def new_category(self, category):
        self.created_categories.append(category)
        return str(len(self.created_categories))


def test_markdown_publish_uses_filename_and_categories(tmp_path: Path):
    path = tmp_path / "01-hello.md"
    path.write_text("正文")
    typecho = FakeTypecho()

    assert PostAll(typecho).post(path, ["随笔"]) == "1"
    post, publish = typecho.posts[0]
    assert (post.title, post.description, post.categories, publish) == (
        "hello",
        "正文",
        ["随笔"],
        True,
    )


def test_notebook_metadata_categories_are_not_overwritten(tmp_path: Path):
    nbformat = pytest.importorskip("nbformat")
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell(
                "- title: 元数据标题\n- tags: python\n- category: Python, 笔记"
            ),
            nbformat.v4.new_markdown_cell("正文"),
        ]
    )
    path = tmp_path / "note.ipynb"
    nbformat.write(notebook, path)
    typecho = FakeTypecho()

    PostAll(typecho).post(path, [])

    post, _ = typecho.posts[0]
    assert post.title == "元数据标题"
    assert post.mt_keywords == "python"
    assert post.categories == ["Python", "笔记"]


def test_directory_scan_and_recursive_publish(tmp_path: Path, monkeypatch):
    child = tmp_path / "01-parent" / "02-child"
    child.mkdir(parents=True)
    (tmp_path / "01-parent" / "root.md").write_text("root")
    (child / "nested.md").write_text("nested")
    (child / "ignored.txt").write_text("ignored")
    tree = get_all_file(tmp_path)
    assert [item.name for item in tree.categories] == ["01-parent"]

    typecho = FakeTypecho()
    publisher = PostAll(typecho)
    monkeypatch.setattr("funtypecho.publish.core.sleep", lambda _: None)
    publisher.post_tree(tree.categories[0], categories=["01-parent"])

    assert [category.name for category in typecho.created_categories] == [
        "parent",
        "child",
    ]
    assert [post.categories for post, _ in typecho.posts] == [["parent"], ["child"]]
