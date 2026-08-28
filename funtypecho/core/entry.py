from dataclasses import field
from typing import BinaryIO, List


class Meta:
    def __init__(self, name: str, parent: int = 0, slug: str = '', description: str = ''):
        self.name = name
        self.parent = parent
        self.slug = slug
        self.description = description


class Category(Meta):
    def __init__(self, name: str, parent: int = 0):
        super(Category, self).__init__(name=name, parent=parent)


class Tag(Meta):
    pass


class Content:
    """
    Post needs at least: title, description , category.
    Page needs at least: title, description.

    text_more will be connected with description as description+'\n<!--more-->\n'+text_more by Typecho.
    tags should be split by ',' like 'tag1, tag2'
    created should be timestamp.
    allow_feed has no effect because Typecho not use
    status could be 'publish' or 'save' or 'private'.
    """

    def __init__(self, title: str,
                 description: str,
                 slug: str = '',
                 mt_text_more: str = '',
                 wp_password: str = '',
                 mt_keywords: str = '',
                 created: str = '',
                 mt_allow_comments: int = 1,
                 mt_allow_pings: int = 1,
                 post_status: str = '', *args, **kwargs):
        self.slug = slug
        self.title = title
        self.created = created
        self.description = description
        self.wp_password = wp_password
        self.mt_keywords = mt_keywords
        self.post_status = post_status
        self.mt_text_more = mt_text_more
        self.mt_allow_pings = mt_allow_pings
        self.mt_allow_comments = mt_allow_comments

        super(Content, self).__init__(*args, **kwargs)


class Post(Content):
    def __init__(self, post_type: str = 'post', categories: List[str] = field(default_factory=list), *args, **kwargs):
        self.post_type = post_type
        self.categories = categories
        super(Post, self).__init__(*args, **kwargs)


class Page(Content):
    def __init__(self, post_type: str = 'page', wp_page_order: int = 0, wp_page_template: str = '', *args, **kwargs):
        self.post_type = post_type
        self.wp_page_order = wp_page_order
        self.wp_page_template = wp_page_template
        super(Page, self).__init__(*args, **kwargs)


class Attachment:
    def __init__(self, name: str, bytes: BinaryIO, *args, **kwargs):
        self.name = name
        self.bytes = bytes
        super(Attachment, self).__init__(*args, **kwargs)


class Comment:
    def __init__(self, content: str,
                 author: str = '',
                 author_email: str = '',
                 author_url: str = '',
                 comment_author: int = 0,
                 comment_author_email: int = 0,
                 comment_author_url: int = 0, *args, **kwargs
                 ):
        self.author = author
        self.content = content
        self.author_url = author_url
        self.author_email = author_email
        self.comment_author = comment_author
        self.comment_author_url = comment_author_url
        self.comment_author_email = comment_author_email
        super(Comment, self).__init__(*args, **kwargs)

    def __post_init__(self):
        if self.author:
            self.comment_author = 1
        if self.author_email:
            self.comment_author_email = 1
        if self.author_url:
            self.comment_author_url = 1
