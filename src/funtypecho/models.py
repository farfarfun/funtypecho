from dataclasses import dataclass, field
from typing import BinaryIO


@dataclass
class Meta:
    """分类和标签的公共元数据。

    参数：
        name: 显示名称。
        parent: 父分类 ID，顶级条目为 0。
        slug: URL 别名。
        description: 条目说明。
    """

    name: str
    parent: int = 0
    slug: str = ""
    description: str = ""


@dataclass
class Category(Meta):
    """Typecho 分类数据，参数继承自 :class:`Meta`。"""


@dataclass
class Tag(Meta):
    """Typecho 标签数据，参数继承自 :class:`Meta`。"""


@dataclass
class Content:
    """文章和页面共用的内容数据。

    参数：
        title: 标题。
        description: 正文。
        slug: URL 别名。
        mt_text_more: `<!--more-->` 之后的正文。
        wp_password: 访问密码。
        mt_keywords: 以逗号分隔的标签。
        created: 创建时间戳。
        mt_allow_comments: 是否允许评论。
        mt_allow_pings: 是否允许引用通知。
        post_status: `publish`、`save` 或 `private`。
    """

    title: str
    description: str

    slug: str = ""
    mt_text_more: str = ""
    wp_password: str = ""
    mt_keywords: str = ""
    created: str = ""
    mt_allow_comments: int = 1
    mt_allow_pings: int = 1
    post_status: str = ""


@dataclass
class Post(Content):
    """文章数据；`categories` 是文章所属分类名称列表。"""

    post_type: str = "post"
    categories: list[str] = field(default_factory=list)


@dataclass
class Page(Content):
    """页面数据，包含页面顺序和模板。"""

    post_type: str = "page"
    wp_page_order: int = 0
    wp_page_template: str = ""


@dataclass
class Attachment:
    """待上传附件。

    参数：
        name: 文件名。
        bytes: 可读取的二进制文件对象。
    """

    name: str
    bytes: BinaryIO


@dataclass
class Comment:
    """评论数据。

    参数：
        content: 评论正文。
        author: 作者名称。
        author_email: 作者邮箱。
        author_url: 作者主页。
    """

    content: str

    author: str = ""
    author_email: str = ""
    author_url: str = ""

    comment_author: int = 0
    comment_author_email: int = 0
    comment_author_url: int = 0

    def __post_init__(self):
        if self.author:
            self.comment_author = 1
        if self.author_email:
            self.comment_author_email = 1
        if self.author_url:
            self.comment_author_url = 1
