# 更新日志

## [未发布]

### 修复

- `get_post` 调用 `metaWeblog.getPost` 时参数顺序错误（多传了 `blog_id` 且顺序不对），
  按 Typecho 服务端真实签名 `(post_id, username, password)` 修正，此前该方法对真实站点
  的调用从未成功过。
- `del_post` 调用 `blogger.deletePost` 时缺少 `post_id`/`publish` 等必填参数且顺序错误，
  按服务端真实签名 `(blog_id, post_id, username, password, publish)` 修正，此前该方法对
  真实站点的调用从未成功过。

### 新增

- 补充 `get_page`/`new_page`/`del_page`/`get_post`/`del_post`/`del_category`/`del_comment`/
  `get_tags`/`get_attachment`/`new_attachment` 等公开方法的正常路径、空响应与失败路径测试。

### 变更

- `main.py`、`publish/core.py` 中残留的英文注释改为中文。
- README 最小示例补充「需替换占位 URL/账号密码」的前置说明，并新增不依赖真实站点、
  基于 `unittest.mock` 的本地可运行示例。

### 移除

- 删除未被任何构建流程读取的 `script/__version__.md`，版本号唯一来源是
  `pyproject.toml`。

## [0.1.12] - 2026-09-21

### 新增

- 补充 Typecho API 的类型标注与中文说明。
- 增加 `publish` extra，支持 Markdown/Notebook 批量发布。

### 修复

- RPC 错误不再被吞掉，异常包含远端错误上下文。
- 发布器使用 `yaml.safe_load` 并拒绝不支持的文件类型。

### 变更

- 源码迁移至标准 `src/funtypecho/` 布局，日志统一使用 `farlog`。
- `notetypecho` 已更名为 `funtypecho`，迁移方式为更新安装包名与 import 名。

### 废弃

- 旧的 `notetypecho` 名称不再作为新代码入口。

## [0.1.11] - 2026-08-28

- 初始 `funtypecho` 包发布。
