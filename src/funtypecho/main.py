from collections.abc import Callable
from dataclasses import asdict
from typing import Any
from xmlrpc.client import Fault, ServerProxy

from .log import logger
from .models import Attachment, Category, Comment, Page, Post


class TypechoPostMixin:
    """文章相关的 Typecho XML-RPC 操作。"""

    def get_posts(self, num: int = 10) -> list[dict[str, Any]] | None:
        """获取最近文章。"""
        return self.try_rpc(self.s.metaWeblog.getRecentPosts, num)

    def get_post(self, post_id: int) -> dict[str, Any] | None:
        """按 ID 获取文章。"""
        return self.try_rpc(self.s.metaWeblog.getPost, post_id)

    def new_post(self, post: Post, publish: bool) -> str | None:
        """创建文章；`publish` 决定立即发布还是保存草稿。"""
        return self.try_rpc(self.s.metaWeblog.newPost, post, publish)

    def edit_post(self, post: Post, post_id: int, publish: bool) -> str | None:
        """更新指定文章。"""
        d = asdict(post)
        d.update({"postId": post_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_post(self, post_id: int) -> bool | None:
        """删除指定文章。"""
        return self.try_rpc(self.s.blogger.deletePost, post_id)


class TypechoPageMixin:
    """页面相关的 Typecho XML-RPC 操作。"""

    def get_pages(self) -> list[dict[str, Any]] | None:
        """获取全部页面。"""
        return self.try_rpc(self.s.wp.getPages)

    def get_page(self, page_id: int) -> dict[str, Any] | None:
        """按 ID 获取页面。"""
        return self._try_rpc(
            self.s.wp.getPage, self.blog_id, page_id, self.username, self.password
        )

    def new_page(self, page: Page, publish: bool) -> str | None:
        """创建页面。"""
        return self.try_rpc(self.s.metaWeblog.newPost, page, publish)

    def edit_page(self, page: Page, page_id: int, publish: bool) -> str | None:
        """更新指定页面。"""
        d = asdict(page)
        d.update({"postId": page_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_page(self, page_id: int) -> bool | None:
        """删除指定页面。"""
        return self.try_rpc(self.s.wp.deletePage, page_id)


class TypechoCategoryMixin:
    """分类相关的 Typecho XML-RPC 操作。"""

    def get_categories(self) -> list[dict[str, Any]] | None:
        """获取分类。"""
        return self.try_rpc(self.s.metaWeblog.getCategories)

    def new_category(self, category: Category, parent_id: int = 0) -> str | None:
        """创建分类。"""
        return self.try_rpc(self.s.wp.newCategory, category)

    def del_category(self, category_id: int) -> bool | None:
        """删除分类。"""
        return self.try_rpc(self.s.wp.deleteCategory, category_id)


class TypechoTagMixin:
    """标签相关的 Typecho XML-RPC 操作。"""

    def get_tags(self) -> list[dict[str, Any]] | None:
        """获取标签。"""
        return self.try_rpc(self.s.wp.getTags)


class TypechoAttachmentMixin:
    """附件相关的 Typecho XML-RPC 操作。"""

    def get_attachments(
        self,
        post_id: int | None = None,
        mime_type: str | None = None,
        page_size: int | None = None,
        page_num: int | None = None,
    ) -> list[dict[str, Any]] | None:
        """按文章、类型和分页条件获取附件。"""
        struct = {}
        if post_id:
            struct.update({"parent_id": post_id})
        if mime_type:
            struct.update({"mime_type": mime_type})
        if page_size:
            struct.update({"number": page_size})
        if page_num:
            struct.update({"offset": page_num})
        return self.try_rpc(self.s.wp.getMediaLibrary, struct)

    def get_attachment(self, attachment_id: int) -> dict[str, Any] | None:
        """按 ID 获取附件。"""
        return self.try_rpc(self.s.wp.getMediaItem, attachment_id)

    def new_attachment(self, data: Attachment) -> dict[str, Any] | None:
        """上传附件。"""
        return self.try_rpc(self.s.wp.uploadFile, data)


class TypechoCommentMixin:
    """评论相关的 Typecho XML-RPC 操作。"""

    def get_comments(
        self,
        status: str | None = None,
        post_id: int | None = None,
        page_size: int | None = None,
        page_num: int | None = None,
    ) -> list[dict[str, Any]] | None:
        """按状态、文章和分页条件获取评论。"""
        struct = {}
        if status:
            struct.update({"status": status})
        if post_id:
            struct.update({"parent_id": post_id})
        if page_size:
            struct.update({"number": page_size})
        if page_num:
            struct.update({"offset": page_num})
        return self.try_rpc(self.s.wp.getComments, struct)

    def get_comment(self, comment_id: int) -> dict[str, Any] | None:
        """按 ID 获取评论。"""
        return self.try_rpc(self.s.wp.getComment, comment_id)

    def new_comment(
        self, comment: Comment, post_id: int, comment_parent: str | None = None
    ) -> dict[str, Any] | None:
        """创建评论。"""
        d = asdict(comment)
        if comment_parent:
            d.update({"comment_parent": comment_parent})
        path = post_id
        return self.try_rpc(self.s.wp.newComment, path, d)

    def edit_comment(self, comment: Comment, comment_id: int) -> bool | None:
        """更新评论。"""
        return self.try_rpc(self.s.wp.editComment, comment_id, comment)

    def del_comment(self, comment_id: int) -> bool | None:
        """删除评论。"""
        return self.try_rpc(
            self.s.wp.deleteComment,
            comment_id,
        )


class Typecho(
    TypechoPostMixin,
    TypechoPageMixin,
    TypechoCategoryMixin,
    TypechoTagMixin,
    TypechoAttachmentMixin,
    TypechoCommentMixin,
):
    def __init__(self, rpc_url: str, username: str, password: str):
        """创建客户端；参数依次为 XML-RPC 地址、用户名和密码。"""
        self.rpc_url = rpc_url
        self.username = username
        self.password = password

        self.s = ServerProxy(rpc_url)
        # blog id could be any number.
        self.blog_id = 1

    def try_rpc(self, rpc_method: Callable[..., Any], *args: Any, **kw: Any) -> Any:
        """调用需要 Typecho 认证参数的 RPC 方法。"""
        return self._try_rpc(
            rpc_method, self.blog_id, self.username, self.password, *args, **kw
        )

    def _try_rpc(self, rpc_method: Callable[..., Any], *args: Any, **kw: Any) -> Any:
        """调用 RPC，并把远端错误转换为带上下文的异常。"""
        try:
            res = rpc_method(*args, **kw)
            logger.info(res)
            return None if res == "" else res
        except Fault as e:
            raise RuntimeError(
                f"Typecho RPC 失败（{e.faultCode}）：{e.faultString}"
            ) from e
        except (OSError, ValueError) as e:
            raise RuntimeError(f"Typecho RPC 调用失败：{e}") from e
