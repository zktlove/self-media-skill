from __future__ import annotations

import argparse
from pathlib import Path

from common.tikhub_client import TikHubSearchClient
from common.utils import ensure_dir, now_string, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="按关键词通过 TikHub 搜索抖音视频。")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--pages", type=int, default=1, help="抓取页数，默认 1；第一页不传 search_id 和翻页参数")
    parser.add_argument(
        "--sort-type",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="排序：0 综合，1 最多点赞，2 最新发布；默认 1",
    )
    parser.add_argument(
        "--publish-time",
        type=int,
        default=180,
        choices=[0, 1, 7, 180],
        help="发布时间：0 不限，1 一天内，7 一周内，180 半年内；默认 180",
    )
    parser.add_argument(
        "--filter-duration",
        type=int,
        default=0,
        help="视频时长筛选，默认 0 不限",
    )
    parser.add_argument(
        "--content-type",
        type=int,
        default=1,
        help="内容分类，默认 1 视频",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / f"search_{now_string()}.json",
        help="输出 JSON 路径",
    )
    args = parser.parse_args()

    ensure_dir(args.output.parent)
    all_items: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    cursor: int | None = None
    search_id = ""
    backtrace = ""
    final_status = "empty"
    final_message = "TikHub 搜索执行完成。"

    with TikHubSearchClient() as client:
        for page_index in range(max(1, args.pages)):
            summary = client.search_videos(
                args.keyword,
                sort_type=args.sort_type,
                publish_time=args.publish_time,
                filter_duration=args.filter_duration,
                content_type=args.content_type,
                cursor=cursor if page_index > 0 else None,
                search_id=search_id if page_index > 0 else "",
                backtrace=backtrace if page_index > 0 else "",
            )
            diagnostics.extend(summary["diagnostics"])
            final_status = str(summary["status"])
            final_message = str(summary["message"])
            for item in summary["items"]:
                aweme_id = str(item.get("aweme_id", "")).strip()
                if aweme_id and any(existing.get("aweme_id") == aweme_id for existing in all_items):
                    continue
                all_items.append(item)
            if not summary["has_more"]:
                break
            cursor = int(summary["next_cursor"] or 0)
            search_id = str(summary["search_id"] or "")
            backtrace = str(summary["backtrace"] or "")
            if not cursor or not search_id or not backtrace:
                break

    payload = {
        "keyword": args.keyword,
        "pages": args.pages,
        "count": len(all_items),
        "sort_type": args.sort_type,
        "publish_time": args.publish_time,
        "filter_duration": args.filter_duration,
        "content_type": args.content_type,
        "status": "ok" if all_items else final_status,
        "source": "tikhub",
        "message": final_message,
        "diagnostics": diagnostics,
        "items": all_items,
    }
    write_json(args.output, payload)
    print(f"已输出: {args.output}")


if __name__ == "__main__":
    main()
