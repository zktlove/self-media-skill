from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from common.browser_profile import bootstrap_user_data_session, default_session_dir_for_browser
from common.cookies import save_cookie_payload
from common.utils import ensure_dir, now_string
from detect_browser_for_login import check_playwright_runtime, detect_browser


def resolve_browser_name(requested: str, detected: dict[str, str]) -> str:
    if requested != "auto":
        return requested
    return "chromium"


def main() -> None:
    parser = argparse.ArgumentParser(description="用 Playwright 浏览器会话自动采集抖音登录态。")
    parser.add_argument("--browser", default="chromium", choices=["auto", "chrome", "msedge", "chromium"])
    parser.add_argument("--timeout-ms", type=int, default=120000, help="等待登录完成的超时时间")
    parser.add_argument(
        "--session-dir",
        type=Path,
        default=None,
        help="Playwright 持久化会话目录",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / f"session_capture_{now_string()}.json",
        help="原始会话输出 JSON",
    )
    parser.add_argument(
        "--storage-state",
        type=Path,
        default=Path(__file__).resolve().parent / "cookies" / "douyin_storage_state.json",
        help="可选，已有 storage state，用于预热导入",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 打印结果")
    args = parser.parse_args()

    runtime = check_playwright_runtime()
    if not runtime["playwright_installed"]:
        raise SystemExit(f"Playwright 运行时不可用，请先执行: {runtime['setup_command']}")

    node_path = shutil.which("node") or shutil.which("node.exe")
    if not node_path:
        raise SystemExit("未检测到 Node.js，无法运行 Playwright 会话采集脚本。")

    detected = detect_browser()
    browser_name = resolve_browser_name(args.browser, detected)
    scripts_dir = Path(__file__).resolve().parent
    session_dir = args.session_dir or default_session_dir_for_browser(scripts_dir, browser_name)
    bootstrap_info: dict[str, str] = {}
    if browser_name in {"chrome", "msedge"}:
        try:
            bootstrap_info = bootstrap_user_data_session(
                browser_name=browser_name,
                session_dir=session_dir,
            )
        except FileNotFoundError:
            bootstrap_info = {}
    script_path = scripts_dir / "browser" / "douyin_browser_worker.js"
    ensure_dir(session_dir)
    ensure_dir(args.output.parent)
    command = [
        node_path,
        str(script_path),
        "--mode",
        "capture",
        "--browser",
        browser_name,
        "--timeout-ms",
        str(args.timeout_ms),
        "--session-dir",
        str(session_dir),
        "--output",
        str(args.output),
    ]
    if args.storage_state.exists():
        command.extend(["--storage-state", str(args.storage_state)])

    env = os.environ.copy()
    node_modules_path = str(Path(runtime["skill_dir"]) / "node_modules")
    env["NODE_PATH"] = node_modules_path + os.pathsep + env.get("NODE_PATH", "")
    subprocess.run(
        command,
        check=True,
        cwd=str(Path(runtime["skill_dir"])),
        text=True,
        encoding="utf-8",
        env=env,
    )
    payload = json.loads(args.output.read_text(encoding="utf-8"))
    status = save_cookie_payload(payload, browser_name=browser_name, note="playwright_session_capture")
    result = {
        "browser": browser_name,
        "session_dir": str(session_dir),
        "output": str(args.output),
        "login_status": str((payload.get("session") or {}).get("login_status", "")),
        "final_url": str((payload.get("session") or {}).get("final_url", "")),
        "cookie_complete": status.complete,
        "cookie_count": status.cookie_count,
        "missing_keys": status.missing_keys,
        "bootstrap": bootstrap_info,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"浏览器: {result['browser']}")
    print(f"登录状态: {result['login_status']}")
    print(f"Cookie 完整: {result['cookie_complete']}")
    print(f"会话目录: {result['session_dir']}")
    print(f"原始输出: {result['output']}")


if __name__ == "__main__":
    main()
