from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def find_chrome() -> str:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which("chrome") or shutil.which("chrome.exe")
    return found or ""


def find_edge() -> str:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which("msedge") or shutil.which("msedge.exe")
    return found or ""


def get_default_browser_progid() -> str:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice' -ErrorAction SilentlyContinue).ProgId",
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    return (result.stdout or "").strip()


def get_playwright_skill_dir() -> Path:
    return Path(r"C:\Users\zktst\.codex\skills\playwright-skill")


def check_playwright_runtime(skill_dir: Path | None = None) -> dict[str, str | bool]:
    resolved_dir = skill_dir or get_playwright_skill_dir()
    node_path = shutil.which("node") or shutil.which("node.exe") or ""
    if not node_path:
        return {
            "playwright_installed": False,
            "node_available": False,
            "skill_dir_exists": resolved_dir.exists(),
            "skill_dir": str(resolved_dir),
            "setup_command": f'cd "{resolved_dir}" && npm run setup',
        }

    if not resolved_dir.exists():
        return {
            "playwright_installed": False,
            "node_available": True,
            "skill_dir_exists": False,
            "skill_dir": str(resolved_dir),
            "setup_command": f'cd "{resolved_dir}" && npm run setup',
        }

    check = subprocess.run(
        [node_path, "-e", "require('playwright'); console.log('ok')"],
        cwd=str(resolved_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {
        "playwright_installed": check.returncode == 0,
        "node_available": True,
        "skill_dir_exists": True,
        "skill_dir": str(resolved_dir),
        "setup_command": f'cd "{resolved_dir}" && npm run setup',
    }


def resolve_login_browser(
    *,
    chrome_path: str,
    edge_path: str,
    playwright_installed: bool,
    default_browser_progid: str,
) -> dict[str, str]:
    if chrome_path:
        return {
            "preferred_browser": "chrome",
            "browser_label": "chrome",
            "chrome_path": chrome_path,
            "edge_path": edge_path,
            "default_browser_progid": "",
        }

    if edge_path:
        return {
            "preferred_browser": "msedge",
            "browser_label": "msedge",
            "chrome_path": "",
            "edge_path": edge_path,
            "default_browser_progid": "",
        }

    if playwright_installed:
        return {
            "preferred_browser": "chromium",
            "browser_label": "playwright-chromium",
            "chrome_path": "",
            "edge_path": "",
            "default_browser_progid": default_browser_progid or "unknown",
        }

    return {
        "preferred_browser": "default",
        "browser_label": "default",
        "chrome_path": "",
        "edge_path": "",
        "default_browser_progid": default_browser_progid or "unknown",
    }


def detect_browser() -> dict[str, str]:
    chrome_path = find_chrome()
    edge_path = find_edge()
    progid = get_default_browser_progid()
    playwright_installed = bool(check_playwright_runtime()["playwright_installed"])
    return resolve_login_browser(
        chrome_path=chrome_path,
        edge_path=edge_path,
        playwright_installed=playwright_installed,
        default_browser_progid=progid,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="检测登录抖音时优先使用的浏览器。")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出检测结果")
    args = parser.parse_args()

    browser_info = detect_browser()
    playwright_info = check_playwright_runtime()
    payload = {**browser_info, **playwright_info}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"preferred_browser={payload['preferred_browser']}")
    if payload["chrome_path"]:
        print(f"chrome_path={payload['chrome_path']}")
    else:
        print(f"default_browser_progid={payload['default_browser_progid']}")
    print(f"playwright_installed={payload['playwright_installed']}")
    print(f"node_available={payload['node_available']}")
    print(f"playwright_skill_dir={payload['skill_dir']}")
    print(f"setup_command={payload['setup_command']}")


if __name__ == "__main__":
    main()
