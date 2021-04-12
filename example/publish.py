# coding=utf-8
import os

from notetypecho.core import Typecho
from notetypecho.publish.core import PostAll

content_root = "/root/workspace/content/publish" if os.getcwd().startswith(
    '/root') else "/Users/new/workspace/noteanalyse/content"

typecho = Typecho('http://39.98.69.238:8442/index.php/action/xmlrpc')

posts = PostAll(typecho)
posts.post_all(content_root)
