# funtypecho

`funtypecho` 是 Typecho XML-RPC 客户端，提供文章、页面、分类、标签、附件和评论的 Python API，并支持把 Markdown/Notebook 批量发布到 Typecho。

## 安装

```bash
uv add funtypecho
uv add 'funtypecho[publish]'
```

## 最小示例

```python
from funtypecho import Post, Typecho

client = Typecho("https://example.com/action/xmlrpc", "user", "password")
post_id = client.new_post(Post(title="你好", description="正文"), publish=False)
print(post_id)
```

RPC 失败会抛出带远端错误信息的 `RuntimeError`。

## 开发

```bash
uv sync --extra publish
uv run pytest
uv build
```

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
