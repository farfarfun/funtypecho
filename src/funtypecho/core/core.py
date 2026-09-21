"""旧版 `funtypecho.core.core` 的兼容导出。"""

from ..main import (
    Typecho,
    TypechoAttachmentMixin,
    TypechoCategoryMixin,
    TypechoCommentMixin,
    TypechoPageMixin,
    TypechoPostMixin,
    TypechoTagMixin,
)

__all__ = [
    "Typecho",
    "TypechoAttachmentMixin",
    "TypechoCategoryMixin",
    "TypechoCommentMixin",
    "TypechoPageMixin",
    "TypechoPostMixin",
    "TypechoTagMixin",
]
