"""perfdemo 命令行入口点"""

import asyncio

from perfdemo.demos import run_all_demos


def main() -> None:
    """主入口函数"""
    asyncio.run(run_all_demos())


if __name__ == "__main__":
    main()
