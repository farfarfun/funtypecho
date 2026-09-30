import argparse
import os
from pathlib import Path

from funtypecho.core import Typecho
from funtypecho.publish.core import PostAll


def main() -> None:
    """从命令行参数和环境变量读取配置并发布指定目录。"""
    parser = argparse.ArgumentParser(description="将本地文档批量发布到 Typecho")
    parser.add_argument("content_root", type=Path, help="包含待发布文档的目录")
    parser.add_argument("--rpc-url", default=os.getenv("TYPECHO_RPC_URL"))
    parser.add_argument("--username", default=os.getenv("TYPECHO_USERNAME"))
    parser.add_argument("--password", default=os.getenv("TYPECHO_PASSWORD"))
    args = parser.parse_args()

    missing = [
        name
        for name, value in (
            ("rpc-url/TYPECHO_RPC_URL", args.rpc_url),
            ("username/TYPECHO_USERNAME", args.username),
            ("password/TYPECHO_PASSWORD", args.password),
        )
        if not value
    ]
    if missing:
        parser.error(f"缺少配置：{', '.join(missing)}")

    typecho = Typecho(args.rpc_url, args.username, args.password)
    PostAll(typecho).post_all(args.content_root)


if __name__ == "__main__":
    main()
