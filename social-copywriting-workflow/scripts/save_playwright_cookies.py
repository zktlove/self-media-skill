from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.cookies import save_cookie_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="把 Playwright 导出的 Cookie/Storage State 保存到 Skill 目录。")
    parser.add_argument("input", type=Path, help="Playwright 导出的 JSON 文件路径")
    parser.add_argument("--browser-name", default="", help="可选，浏览器名称")
    parser.add_argument("--note", default="playwright_export", help="可选，备注")
    parser.add_argument("--json", action="store_true", help="以 JSON 打印结果")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    status = save_cookie_payload(
        payload,
        browser_name=args.browser_name,
        note=args.note,
    )
    result = {
        "exists": status.exists,
        "complete": status.complete,
        "source": status.source,
        "missing_keys": status.missing_keys,
        "cookie_path": status.cookie_path,
        "json_path": status.json_path,
        "domains": status.domains,
        "cookie_count": status.cookie_count,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"保存完成: {result['complete']}")
    print(f"Cookie TXT: {result['cookie_path']}")
    print(f"Cookie JSON: {result['json_path']}")
    print(f"缺少字段: {', '.join(result['missing_keys']) if result['missing_keys'] else '无'}")


if __name__ == "__main__":
    main()
