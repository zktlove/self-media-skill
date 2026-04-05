from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.cookies import COOKIE_DIR, COOKIE_JSON_PATH, COOKIE_META_PATH, COOKIE_TXT_PATH, load_cookie_context
from common.session_validator import build_session_report
from detect_browser_for_login import check_playwright_runtime, detect_browser


def run_session_check() -> dict[str, object]:
    _, _, cookie_status = load_cookie_context()
    browser_info = detect_browser()
    playwright_info = check_playwright_runtime()
    session_check = {
        "status": "ok" if cookie_status.complete else "missing_cookie",
        "message": "Cookie 完整，可继续执行登录态相关脚本。"
        if cookie_status.complete
        else "Cookie 不完整，需要重新登录并采集浏览器会话。",
    }

    report = build_session_report(
        cookie_complete=cookie_status.complete,
        playwright_installed=bool(playwright_info["playwright_installed"]),
        session_status=str(session_check["status"]),
        browser_label=str(browser_info["browser_label"]),
    )
    return {
        "cookie": {
            "exists": cookie_status.exists,
            "complete": cookie_status.complete,
            "source": cookie_status.source,
            "missing_keys": cookie_status.missing_keys,
            "cookie_count": cookie_status.cookie_count,
            "cookie_dir": str(COOKIE_DIR),
            "cookie_txt": str(COOKIE_TXT_PATH),
            "cookie_json": str(COOKIE_JSON_PATH),
            "cookie_meta": str(COOKIE_META_PATH),
        },
        "browser": browser_info,
        "playwright": playwright_info,
        "session_check": session_check,
        "report": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="检查抖音登录态是否具备可用的 Cookie/浏览器环境。")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="可选，输出 JSON 路径",
    )
    parser.add_argument("--json", action="store_true", help="直接打印 JSON")
    args = parser.parse_args()

    payload = run_session_check()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    report = payload["report"]
    cookie = payload["cookie"]
    session_check = payload["session_check"]
    print(f"状态: {report['status']}")
    print(f"下一步: {report['next_action']}")
    print(f"浏览器: {report['browser']}")
    print(f"Cookie 完整: {cookie['complete']}")
    print(f"Cookie 来源: {cookie['source']}")
    print(f"登录态校验状态: {session_check['status']}")
    print(f"登录态校验信息: {session_check['message']}")
    print("原因:")
    for item in report["reasons"]:
        print(f"- {item}")
    print("建议操作:")
    for item in report["instructions"]:
        print(f"- {item}")
    if args.output:
        print(f"已输出: {args.output}")


if __name__ == "__main__":
    main()
