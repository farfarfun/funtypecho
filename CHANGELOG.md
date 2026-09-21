# 更新日志

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
