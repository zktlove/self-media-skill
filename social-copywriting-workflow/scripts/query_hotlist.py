from __future__ import annotations

import argparse
from pathlib import Path

from common.douyin_client import DouyinWebClient
from common.utils import ensure_dir, now_string, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="查询抖音热榜。")
    parser.add_argument(
        "--board",
        default="hot",
        choices=["hot", "entertainment", "society", "challenge"],
        help="榜单类型",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / f"hotlist_{now_string()}.json",
        help="输出 JSON 路径",
    )
    parser.add_argument("--cookie", default="", help="可选，抖音 Cookie")
    parser.add_argument("--ms-token", default="", help="可选，抖音 msToken")
    args = parser.parse_args()

    ensure_dir(args.output.parent)
    with DouyinWebClient(cookie=args.cookie, ms_token=args.ms_token, require_cookie=True) as client:
        payload = client.fetch_hot_list(args.board)
    write_json(args.output, payload)
    print(f"已输出: {args.output}")


if __name__ == "__main__":
    main()
