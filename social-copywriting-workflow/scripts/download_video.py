from __future__ import annotations

import argparse
from pathlib import Path

from common.cookies import load_cookie_context
from common.download import download_file
from common.douyin_client import DouyinWebClient
from common.utils import ensure_dir, sanitize_filename, write_json


def load_urls(args: argparse.Namespace) -> list[str]:
    urls = list(args.urls or [])
    if args.url_file:
        extra = [
            line.strip()
            for line in args.url_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        urls.extend(extra)
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(description="解析抖音视频 URL 并直接下载视频。")
    parser.add_argument("urls", nargs="*", help="一个或多个抖音视频 URL")
    parser.add_argument("--url-file", type=Path, help="每行一个 URL 的文本文件")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "downloads",
        help="视频保存目录",
    )
    parser.add_argument("--overwrite", action="store_true", help="已存在时覆盖")
    parser.add_argument("--cookie", default="", help="可选，抖音 Cookie")
    parser.add_argument("--ms-token", default="", help="可选，抖音 msToken")
    args = parser.parse_args()

    urls = load_urls(args)
    if not urls:
        raise SystemExit("至少提供一个视频 URL 或 --url-file")

    ensure_dir(args.output_dir)
    records = []
    resolved_cookie, _, _ = load_cookie_context(
        explicit_cookie=args.cookie,
        explicit_ms_token=args.ms_token,
    )
    request_headers = {
        "Referer": "https://www.douyin.com/",
        "Cookie": resolved_cookie,
    }

    with DouyinWebClient(cookie=args.cookie, ms_token=args.ms_token, require_cookie=True) as client:
        for url in urls:
            detail = client.fetch_aweme_detail_by_url(url)
            record = client.normalize_aweme(detail)
            if record["type"] != "视频":
                print(f"跳过非视频内容: {url}")
                continue
            direct_url = str(record.get("direct_download_url") or "")
            if not direct_url:
                print(f"跳过无视频流内容: {url}")
                continue

            filename = sanitize_filename(
                f"{record.get('author', '')}_{record.get('title', '')}_{record.get('aweme_id', '')}"
            )
            video_path = args.output_dir / f"{filename}.mp4"
            meta_path = args.output_dir / f"{filename}.json"
            download_file(
                direct_url,
                video_path,
                overwrite=args.overwrite,
                headers=request_headers,
            )
            write_json(meta_path, record)
            print(f"已下载: {video_path}")
            records.append({"video_path": str(video_path), "meta_path": str(meta_path), **record})

    if not records:
        raise SystemExit("没有可下载的视频。")


if __name__ == "__main__":
    main()
