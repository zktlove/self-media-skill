from __future__ import annotations

import argparse
from pathlib import Path

from common.douyin_client import DouyinWebClient
from common.utils import ensure_dir, now_string, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="根据主页 URL 或 sec_user_id 抓取主页作品。")
    parser.add_argument("homepage_url", nargs="?", default="", help="抖音主页 URL")
    parser.add_argument("--sec-user-id", default="", help="已知 sec_user_id 时可直接传")
    parser.add_argument("--days", type=int, default=365, help="抓取近多少天作品，默认 365")
    parser.add_argument("--count", type=int, default=18, help="每页数量，默认 18")
    parser.add_argument("--max-pages", type=int, default=None, help="最多抓多少页")
    parser.add_argument("--video-only", action="store_true", help="只保留有视频流的作品")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / f"homepage_{now_string()}.json",
        help="输出 JSON 路径",
    )
    parser.add_argument("--cookie", default="", help="可选，抖音 Cookie")
    parser.add_argument("--ms-token", default="", help="可选，抖音 msToken")
    args = parser.parse_args()

    if not args.homepage_url and not args.sec_user_id:
        raise SystemExit("必须提供主页 URL 或 --sec-user-id")

    ensure_dir(args.output.parent)
    with DouyinWebClient(cookie=args.cookie, ms_token=args.ms_token, require_cookie=True) as client:
        sec_user_id = args.sec_user_id or client.resolve_sec_user_id(args.homepage_url)
        items = client.fetch_user_posts(
            sec_user_id,
            days=args.days,
            count=args.count,
            max_pages=args.max_pages,
        )

    if args.video_only:
        items = [item for item in items if item.get("type") == "视频" and item.get("direct_download_url")]

    payload = {
        "homepage_url": args.homepage_url,
        "sec_user_id": sec_user_id,
        "days": args.days,
        "count": len(items),
        "items": items,
    }
    write_json(args.output, payload)
    print(f"已输出: {args.output}")


if __name__ == "__main__":
    main()
