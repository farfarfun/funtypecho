from dataclasses import asdict
from typing import Dict, List, Optional
from xmlrpc.client import Fault, ServerProxy

from .entry import Attachment, Category, Comment, Page, Post
from .log import logger


class TypechoBase:
    """
    TypechoBase
    """

    def __init__(self, rpc_url: str, username: str, password: str):
        """

        :param rpc_url:
        :param username:
        :param password:
        """
        self.rpc_url = rpc_url
        self.username = username
        self.password = password

        # self.s = ServerProxy(rpc_url)
        self.server = ServerProxy(rpc_url)
        # blog id could be any number.
        self.blog_id = 1

    def try_rpc(self, rpc_method, *args, **kw):
        """

        :param rpc_method:
        :param args:
        :param kw:
        :return:
        """
        return self._try_rpc(rpc_method, self.blog_id, self.username, self.password, *args, **kw)

    def _try_rpc(self, rpc_method, *args, **kw):
        """

        :param rpc_method:
        :param args:
        :param kw:
        :return:
        """
        res = None
        try:
            res = rpc_method(*args, **kw)
            logger.info(res)
            if res == '':
                res = None
        except Fault as e:
            logger.error("Error {}: {}".format(e.faultCode, e.faultString))
        except Exception as e:
            logger.error("Error {}".format(e))
        return res


class TypechoPostMixin(TypechoBase):
    """
    TypechoPostMixin
    """

    def get_posts(self, num: int = 10) -> Optional[List[Dict]]:
        """
        get_posts
        """
        return self.try_rpc(self.server.metaWeblog.getRecentPosts, num)

    def get_post(self, post_id: int) -> Optional[Dict]:
        """
        get_post
        """
        return self.try_rpc(self.server.metaWeblog.getPost, post_id)

    def new_post(self, post: Post, publish: bool) -> Optional[str]:
        """
        Post's status will cover publish, and if you only save post, the post id will only be '0'
        If Post's categories are not created, it will only create the first category
        """
        post.categories = ['default'] if post.categories is None or len(
            post.categories) == 0 else post.categories
        return self.try_rpc(self.server.metaWeblog.newPost, post, publish)

    def edit_post(self, post: Post, post_id: int, publish: bool) -> Optional[str]:
        """
        edit_post
        """
        d = asdict(post)
        d.update({'postId': post_id})
        return self.try_rpc(self.server.metaWeblog.newPost, d, publish)

    def del_post(self, post_id: int) -> None:
        """
        del_post
        """
        return self.try_rpc(self.server.blogger.deletePost, post_id)


class TypechoPageMixin(TypechoBase):
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super(TypechoPageMixin, self).__init__(*args, **kwargs)

    def get_pages(self) -> Optional[List[Dict]]:
        """

        :return:
        """
        return self.try_rpc(self.server.wp.getPages)

    def get_page(self, page_id: int) -> Optional[Dict]:
        """

        :param page_id:
        :return:
        """
        return self._try_rpc(self.server.wp.getPage, self.blog_id, page_id, self.username, self.password)

    def new_page(self, page: Page, publish: bool) -> Optional[str]:
        """

        :param page:
        :param publish:
        :return:
        """
        return self.try_rpc(self.server.metaWeblog.newPost, page, publish)

    def edit_page(self, page: Page, page_id: int, publish: bool) -> Optional[str]:
        """

        :param page: 
        :param page_id: 
        :param publish: 
        :return: 
        """
        d = asdict(page)
        d.update({'postId': page_id})
        return self.try_rpc(self.server.metaWeblog.newPost, d, publish)

    def del_page(self, page_id: int) -> Optional[bool]:
        """

        :param page_id: 
        :return: 
        """
        return self.try_rpc(self.server.wp.deletePage, page_id)


class TypechoCategoryMixin(TypechoBase):
    """
    TypechoCategoryMixin
    """

    def get_categories(self) -> Optional[Dict]:
        """

        :return:
        """
        return self.try_rpc(self.server.metaWeblog.getCategories)

    def new_category(self, category: Category, parent_id: int = 0, new_cate=False) -> Optional[str]:
        """

        :param category:
        :param parent_id:
        :return:
        """
        if new_cate:
            return self.try_rpc(self.server.wp.newCategory, category)
        else:
            cates = dict([(cate['categoryName'], cate['categoryId'])
                          for cate in self.get_categories()])
            if category in cates.keys():
                return cates[category]
            else:
                return self.try_rpc(self.server.wp.newCategory, category)

    def del_category(self, category_id: int) -> Optional[bool]:
        """

        :param category_id:
        :return:
        """
        return self.try_rpc(self.server.wp.deleteCategory, category_id)


class TypechoTagMixin(TypechoBase):
    """
    TypechoTagMixin
    """

    def get_tags(self) -> Optional[List[Dict]]:
        """

        :return:
        """
        return self.try_rpc(self.server.wp.getTags)


class TypechoAttachmentMixin(TypechoBase):
    """
    TypechoAttachmentMixin
    """

    def get_attachments(self, post_id: int = None, mime_type: str = None, page_size: int = None,
                        page_num: int = None) -> Optional[List[Dict]]:
        """

        :param post_id:
        :param mime_type:
        :param page_size:
        :param page_num:
        :return:
        """
        struct = {}
        if post_id:
            struct.update({'parent_id': post_id})
        if mime_type:
            struct.update({'mime_type': mime_type})
        if page_size:
            struct.update({'number': page_size})
        if page_num:
            struct.update({'offset': page_num})
        return self.try_rpc(self.server.wp.getMediaLibrary, struct)

    def get_attachment(self, attachment_id) -> Optional[Dict]:
        """

        :param attachment_id:
        :return:
        """
        return self.try_rpc(self.server.wp.getMediaItem, attachment_id)

    def new_attachment(self, data: Attachment):
        """

        :param data:
        :return:
        """
        return self.try_rpc(self.server.wp.uploadFile, data)


class TypechoCommentMixin(TypechoBase):
    """
    TypechoCommentMixin
    """

    def get_comments(self, status: str = None, post_id: int = None, page_size: int = None,
                     page_num: int = None) -> Optional[List[Dict]]:
        """

        :param status:
        :param post_id:
        :param page_size:
        :param page_num:
        :return:
        """
        struct = {}
        if status:
            struct.update({'status': status})
        if post_id:
            struct.update({'parent_id': post_id})
        if page_size:
            struct.update({'number': page_size})
        if page_num:
            struct.update({'offset': page_num})
        return self.try_rpc(self.server.wp.getComments, struct)

    def get_comment(self, comment_id: int) -> Optional[Dict]:
        """

        :param comment_id:
        :return:
        """
        return self.try_rpc(self.server.wp.getComment, comment_id)

    def new_comment(self, comment: Comment, post_id: int, comment_parent: str = None) -> None:
        """

        :param comment:
        :param post_id:
        :param comment_parent:
        :return:
        """
        d = asdict(comment)
        if comment_parent:
            d.update({'comment_parent': comment_parent})
        path = post_id
        return self.try_rpc(self.server.wp.newComment, path, d)

    def edit_comment(self, comment: Comment, comment_id: int) -> Optional[bool]:
        """

        :param comment:
        :param comment_id:
        :return:
        """
        return self.try_rpc(self.server.wp.editComment, comment_id, comment)

    def del_comment(self, comment_id: int) -> Optional[bool]:
        """

        :param comment_id:
        :return:
        """
        return self.try_rpc(self.server.wp.deleteComment, comment_id, )


class Typecho(TypechoPostMixin, TypechoPageMixin, TypechoCategoryMixin, TypechoTagMixin, TypechoAttachmentMixin,
              TypechoCommentMixin):
    """
    Typecho
    """
    pass
