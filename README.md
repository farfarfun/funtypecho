# funtypecho

`funtypecho` 是 Typecho XML-RPC 客户端，提供文章、页面、分类、标签、附件和评论的 Python API，并支持把 Markdown/Notebook 批量发布到 Typecho。

## 安装

```bash
uv add funtypecho
uv add 'funtypecho[publish]'
```

## 最小示例

需要先有一个已开启 XML-RPC 的 Typecho 站点（后台「设置 - 常规 - 启用
XML-RPC 服务」），把下面的 URL、用户名、密码替换为该站点的实际值：

```python
from funtypecho import Post, Typecho

client = Typecho("https://your-site.example.com/action/xmlrpc", "user", "password")
post_id = client.new_post(Post(title="你好", description="正文"), publish=False)
print(post_id)
```

RPC 失败会抛出带远端错误信息的 `RuntimeError`。

### 不依赖真实站点的本地示例

没有可用的 Typecho 站点时，可以用 `unittest.mock` 打桩
`xmlrpc.client.ServerProxy`，不访问网络也能在本地跑通调用链：

```python
from types import SimpleNamespace
from unittest.mock import Mock

from funtypecho import Post, Typecho

client = Typecho("https://your-site.example.com/action/xmlrpc", "user", "password")
client.s = SimpleNamespace(metaWeblog=SimpleNamespace(newPost=Mock(return_value="1")))
post_id = client.new_post(Post(title="你好", description="正文"), publish=False)
print(post_id)  # "1"
```

## 开发

```bash
uv sync --extra publish
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run funbuild install
```

发布前先更新变更记录并确认版本递增符合预期，再执行 `uv run funbuild
build`。该命令会依次完成版本递增、构建、产物安装校验、发布和 Git
标签；需要预先通过环境变量配置 PyPI 凭据。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
