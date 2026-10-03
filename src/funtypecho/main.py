from collections.abc import Callable
from dataclasses import asdict
from typing import Any
from xmlrpc.client import Fault, ServerProxy

from .log import logger
from .models import Attachment, Category, Comment, Page, Post


class TypechoPostMixin:
    """文章相关的 Typecho XML-RPC 操作。"""

    def get_posts(self, num: int = 10) -> list[dict[str, Any]] | None:
        """获取最近文章。

        参数：num 为最多返回的文章数。返回文章字典列表，空响应返回 None。
        """
        return self.try_rpc(self.s.metaWeblog.getRecentPosts, num)

    def get_post(self, post_id: int) -> dict[str, Any] | None:
        """按 ID 获取文章；返回文章字典，空响应返回 None。

        `metaWeblog.getPost` 的参数顺序是 `(post_id, username, password)`，
        不带 `blog_id`，与其他方法不同，因此不走 `try_rpc` 的通用拼参逻辑。
        """
        return self._try_rpc(
            self.s.metaWeblog.getPost, post_id, self.username, self.password
        )

    def new_post(self, post: Post, publish: bool) -> str | None:
        """创建文章；`post` 为文章数据，`publish` 控制是否立即发布。

        返回远端文章 ID，空响应返回 None。
        """
        return self.try_rpc(self.s.metaWeblog.newPost, post, publish)

    def edit_post(self, post: Post, post_id: int, publish: bool) -> str | None:
        """更新文章；传入文章数据、文章 ID 和发布状态，返回远端结果。

        Typecho 服务端的 `metaWeblog.editPost` 内部只是把 `postId` 塞进内容
        字典后转调 `metaWeblog.newPost`（服务端据此判断是编辑还是新建），
        这里直接调用 `newPost` 等价且少一次服务端转发。
        """
        d = asdict(post)
        d.update({"postId": post_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_post(self, post_id: int, publish: bool = True) -> bool | None:
        """按 `post_id` 删除文章；返回是否删除成功，空响应返回 None。

        `blogger.deletePost` 的参数顺序是
        `(blog_id, post_id, username, password, publish)`，`post_id` 在
        `username`/`password` 之前且必须传 `publish`，因此不走 `try_rpc`。
        """
        return self._try_rpc(
            self.s.blogger.deletePost,
            self.blog_id,
            post_id,
            self.username,
            self.password,
            publish,
        )


class TypechoPageMixin:
    """页面相关的 Typecho XML-RPC 操作。"""

    def get_pages(self) -> list[dict[str, Any]] | None:
        """获取全部页面；返回页面字典列表，空响应返回 None。"""
        return self.try_rpc(self.s.wp.getPages)

    def get_page(self, page_id: int) -> dict[str, Any] | None:
        """按 `page_id` 获取页面；返回页面字典，空响应返回 None。"""
        return self._try_rpc(
            self.s.wp.getPage, self.blog_id, page_id, self.username, self.password
        )

    def new_page(self, page: Page, publish: bool) -> str | None:
        """创建页面；`publish` 控制是否立即发布，返回远端页面 ID。

        Typecho 服务端的 `wp.newPage` 只是在 `content['post_type'] = 'page'`
        后转发给 `metaWeblog.newPost` 处理，是否生成页面完全由内容里的
        `post_type` 字段决定（`Page` 默认就是 `"page"`），因此直接调用
        `metaWeblog.newPost` 等价且少一次服务端转发。
        """
        return self.try_rpc(self.s.metaWeblog.newPost, page, publish)

    def edit_page(self, page: Page, page_id: int, publish: bool) -> str | None:
        """更新页面；传入页面数据、页面 ID 和发布状态，返回远端结果。

        同理，Typecho 服务端的 `wp.editPage`/`metaWeblog.editPost` 内部都是把
        `postId` 塞进内容字典后再调用 `metaWeblog.newPost`（服务端据此判断
        是编辑还是新建），这里直接复用同一条路径。
        """
        d = asdict(page)
        d.update({"postId": page_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_page(self, page_id: int) -> bool | None:
        """按 `page_id` 删除页面；返回是否删除成功，空响应返回 None。"""
        return self.try_rpc(self.s.wp.deletePage, page_id)


class TypechoCategoryMixin:
    """分类相关的 Typecho XML-RPC 操作。"""

    def get_categories(self) -> list[dict[str, Any]] | None:
        """获取全部分类；返回分类字典列表，空响应返回 None。"""
        return self.try_rpc(self.s.metaWeblog.getCategories)

    def new_category(self, category: Category, parent_id: int = 0) -> str | None:
        """创建 `category`；返回分类 ID，空响应返回 None。

        `parent_id` 为兼容参数；父分类应写入 `category.parent`。
        """
        return self.try_rpc(self.s.wp.newCategory, category)

    def del_category(self, category_id: int) -> bool | None:
        """按 `category_id` 删除分类；返回是否成功，空响应返回 None。"""
        return self.try_rpc(self.s.wp.deleteCategory, category_id)


class TypechoTagMixin:
    """标签相关的 Typecho XML-RPC 操作。"""

    def get_tags(self) -> list[dict[str, Any]] | None:
        """获取全部标签；返回标签字典列表，空响应返回 None。"""
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
        """按文章、MIME 类型及分页参数获取附件。

        返回附件字典列表，空响应返回 None。
        """
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
        """按 `attachment_id` 获取附件；返回附件字典或 None。"""
        return self.try_rpc(self.s.wp.getMediaItem, attachment_id)

    def new_attachment(self, data: Attachment) -> dict[str, Any] | None:
        """上传 `data` 附件；返回远端附件信息或 None。"""
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
        """按状态、文章及分页参数获取评论。

        返回评论字典列表，空响应返回 None。
        """
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
        """按 `comment_id` 获取评论；返回评论字典或 None。"""
        return self.try_rpc(self.s.wp.getComment, comment_id)

    def new_comment(
        self, comment: Comment, post_id: int, comment_parent: str | None = None
    ) -> dict[str, Any] | None:
        """为 `post_id` 创建评论，可指定父评论 ID。

        返回远端评论信息，空响应返回 None。
        """
        d = asdict(comment)
        if comment_parent:
            d.update({"comment_parent": comment_parent})
        path = post_id
        return self.try_rpc(self.s.wp.newComment, path, d)

    def edit_comment(self, comment: Comment, comment_id: int) -> bool | None:
        """更新 `comment_id` 对应的评论；返回是否成功或 None。"""
        return self.try_rpc(self.s.wp.editComment, comment_id, comment)

    def del_comment(self, comment_id: int) -> bool | None:
        """按 `comment_id` 删除评论；返回是否成功或 None。"""
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
    """Typecho XML-RPC 客户端，聚合文章、页面、分类和评论等 API。"""

    def __init__(self, rpc_url: str, username: str, password: str):
        """使用 XML-RPC 地址、用户名和密码创建客户端，无返回值。"""
        self.rpc_url = rpc_url
        self.username = username
        self.password = password

        self.s = ServerProxy(rpc_url)
        # Typecho 为单博客系统，blog id 取任意值均可，固定填 1。
        self.blog_id = 1

    def try_rpc(self, rpc_method: Callable[..., Any], *args: Any, **kw: Any) -> Any:
        """调用需要认证的 RPC 方法。

        `args` 和 `kw` 会追加到认证参数之后；返回远端响应，空串转为 None。
        """
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
