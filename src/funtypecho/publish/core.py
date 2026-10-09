import re
from pathlib import Path
from time import sleep
from typing import Any

from funtypecho.core import Category, Post, Typecho


class FileTree:
    """待发布内容的目录树。"""

    def __init__(self, name: str = "默认分类") -> None:
        self.name = name
        self.categories = []
        self.files = []

    def __str__(self):
        return "{}  {}  {}".format(
            self.name, ";".join([i.__str__() for i in self.categories]), len(self.files)
        )


def get_all_file(path_root: str | Path) -> FileTree:
    """扫描 `path_root`，返回其中 Markdown 和 Notebook 组成的目录树。"""
    root = Path(path_root)
    file_tree = FileTree(root.name)
    for path in root.iterdir():
        if path.is_dir():
            filename = path.name
            if filename in (".ipynb_checkpoints", "pass") or "pass" in filename:
                continue
            file_tree.categories.append(get_all_file(path))
        else:
            filename, filetype = path.stem, path.suffix
            if filetype in (".ipynb", ".md"):
                file_tree.files.append(path)

    file_tree.files.sort()
    file_tree.categories.sort(key=lambda x: x.name)
    return file_tree


def coalesce(params: list[Any] | None) -> Any:
    """返回 `params` 中第一个非 None 值；没有可用值时返回 None。"""
    if params is None or len(params) == 0:
        return None
    for param in params:
        if param is not None:
            return param
    return None


class PostAll:
    """把目录树中的文档发布到 Typecho。"""

    def __init__(self, typecho: Typecho) -> None:
        """使用 `typecho` 客户端创建批量发布器，无返回值。"""
        self.typecho: Typecho = typecho
        self.categories = [
            entry["categoryName"] for entry in (self.typecho.get_categories() or [])
        ]

    def post(self, path: str | Path, categories: list[str]) -> str | None:
        """将 `path` 发布到指定 `categories`，返回远端文章 ID。"""
        path = Path(path)
        filename, filetype = path.stem, path.suffix

        post = None
        if filetype == ".ipynb":
            import nbformat
            import yaml
            from nbconvert import MarkdownExporter

            jake_notebook = nbformat.reads(path.read_text(), as_version=4)
            mark = MarkdownExporter()
            content, _ = mark.from_notebook_node(jake_notebook)
            # 检查首个单元格是否为 YAML 格式的元数据标题块
            if len(jake_notebook.cells) >= 1:
                source = str(jake_notebook.cells[0].source)
                if source.startswith("- "):
                    s = yaml.safe_load(source)
                    res = {}
                    [res.update(i) for i in s]

                    title = res.get("title", filename)
                    tags = res.get("tags", "")
                    metadata_categories = [
                        item.strip()
                        for item in res.get("category", "").split(",")
                        if item.strip()
                    ]
                    tmp_categories = categories or metadata_categories

                    del jake_notebook.cells[0]
                    content, _ = mark.from_notebook_node(jake_notebook)
                    post = Post(
                        title=title,
                        description=content,
                        mt_keywords=tags,
                        categories=tmp_categories,
                    )

            post = post or Post(
                title=self.name_convent(filename),
                description=content,
                categories=categories,
            )
        elif filetype == ".md":
            content = path.read_text()
            post = Post(
                title=self.name_convent(filename),
                description=content,
                categories=categories,
            )
        else:
            raise ValueError(f"不支持的发布文件类型：{filetype}（文件：{path}）")

        return self.typecho.new_post(post, publish=True)

    def name_convent(self, name: str) -> str:
        """去除 `name` 开头的编号和分隔符，返回处理后的名称。"""
        return re.sub(r"^[\d|_.-]+", "", name)

    def category_manage(self, category: str, parent_id: int = 0) -> tuple[str, int]:
        """创建分类，可指定父分类 ID；返回规范化名称和远端 ID。"""
        category = self.name_convent(category)

        cate = Category(name=category, parent=parent_id)
        return category, int(self.typecho.new_category(cate))

    def post_tree(
        self, file_tree: FileTree, categories: list[str], parent_id: int = 0
    ) -> None:
        """递归发布 `file_tree`，继承分类列表和父分类 ID，无返回值。"""
        if len(file_tree.files) == 0 and len(file_tree.categories) == 0:
            return

        categories, parent_id = self.category_manage(
            file_tree.name, parent_id=parent_id
        )

        for path in file_tree.files:
            self.post(path, categories=[categories])
            sleep(1)
        for tree in file_tree.categories:
            if "pass" in tree.name:
                continue
            self.post_tree(tree, categories=[tree.name], parent_id=parent_id)

    def post_all(self, path_root: str | Path) -> None:
        """扫描并发布 `path_root` 下的全部文档，无返回值。"""
        res = get_all_file(path_root)

        for path in res.categories:
            self.post_tree(path, categories=[path.name], parent_id=0)
