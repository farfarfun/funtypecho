# funtypecho

`funtypecho` is a Typecho XML-RPC client for posts, pages, categories, tags, attachments, and comments. It also includes an optional Markdown/Notebook publisher.

## Installation

```bash
uv add funtypecho
uv add 'funtypecho[publish]'
```

```python
from funtypecho import Post, Typecho

client = Typecho("https://example.com/action/xmlrpc", "user", "password")
post_id = client.new_post(Post(title="Hello", description="Content"), publish=False)
print(post_id)
```

RPC failures raise `RuntimeError` with the remote error context.

---

## About farfarfun

[farfarfun](https://github.com/farfarfun) is an open-source organization focused on practical libraries for cloud storage, data processing, AI, multimedia, and developer tooling.

- Organization: <https://github.com/farfarfun>
- PyPI: <https://pypi.org/user/niuliangtao/>
- Contact: farfarfun@qq.com

This project is released under the [MIT](LICENSE) license.
