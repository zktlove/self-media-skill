from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _repo_paths() -> tuple[Path, Path, Path]:
    runtime_dir = Path(__file__).resolve().parent
    lesson_dir = runtime_dir.parent.parent.parent
    mcp_dir = lesson_dir / "mcp"
    return runtime_dir, lesson_dir, mcp_dir


RUNTIME_DIR, LESSON_DIR, MCP_DIR = _repo_paths()
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from xiaohongshu_keyword_mcp.image_service import XiaohongshuImageService
from xiaohongshu_keyword_mcp.publish_payload_service import (  # noqa: E402
    build_publish_payload,
    render_copy_text,
)
from xiaohongshu_keyword_mcp.service import TikHubXiaohongshuService  # noqa: E402
from xiaohongshu_keyword_mcp.workflow_retry import retry_async  # noqa: E402

DEFAULT_PLAYWRIGHT_SKILL_DIR = Path(r"C:\Users\zktst\.codex\skills\playwright-skill")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行完整的小红书自动发布工作流。")
    parser.add_argument("--keyword", required=True, help="对标和发布使用的关键词")
    parser.add_argument(
        "--publish-mode",
        default="stop_before_publish",
        choices=["stop_before_publish", "publish", "preview"],
        help="发布模式：preview/stop_before_publish 只停在发布前，publish 直接点击发布。",
    )
    parser.add_argument(
        "--storage-state-path",
        default=str(RUNTIME_DIR / "xiaohongshu-storage-state_20260315_190812.json"),
        help="小红书创作平台的 Playwright storage state 文件路径",
    )
    parser.add_argument(
        "--playwright-skill-dir",
        default=str(DEFAULT_PLAYWRIGHT_SKILL_DIR),
        help="playwright-skill 目录，用它的 run.js 执行发布脚本",
    )
    parser.add_argument("--account-positioning", default="普通人AI副业入门分享")
    parser.add_argument("--target-audience", default="想做副业但没方向的普通人和上班族")
    parser.add_argument("--content-direction", default="AI副业入门、低门槛变现、先做案例再接单")
    parser.add_argument("--tone-style", default="口语化、干货型、轻鼓励")
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def write_console_text(text: str, *, stream: Any) -> None:
    encoding = getattr(stream, "encoding", None) or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    stream.write(safe_text)


def render_summary(
    *,
    keyword: str,
    benchmark_markdown_path: str,
    payload: dict[str, Any],
    images_result: dict[str, Any],
    publish_result: dict[str, Any],
    summary_path: Path,
    screenshot_path: Path,
) -> str:
    image_lines = "\n".join(
        f"{index}. {image['path']}" for index, image in enumerate(images_result["images"], start=1)
    )
    topic_aliases = []
    debug_html = publish_result.get("debugInfo", {}).get("editorHtml", "")
    for topic in payload["topics"]:
        topic_aliases.append(f"- {topic}")

    return (
        "# 小红书自动发布运行记录\n\n"
        f"- 关键词：{keyword}\n"
        f"- 对标内容：{benchmark_markdown_path}\n"
        f"- 标题：{payload['title']}\n"
        f"- 发布状态：{publish_result.get('status')}\n"
        f"- 发布模式：{publish_result.get('publishMode')}\n"
        f"- 发布页地址：{publish_result.get('url')}\n"
        f"- 截图：{screenshot_path}\n"
        f"- 结果 JSON：{summary_path.with_name(summary_path.name.replace('run_summary', 'publish_result')).with_suffix('.json')}\n\n"
        "## 正文\n\n"
        f"{payload['body']}\n\n"
        "## 配图\n\n"
        f"{image_lines}\n\n"
        "## 目标话题\n\n"
        f"{chr(10).join(topic_aliases)}\n\n"
        "## 编辑器结果片段\n\n"
        f"{debug_html}\n"
    )


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    payload_path = RUNTIME_DIR / f"publish_payload_{timestamp}.json"
    copy_text_path = RUNTIME_DIR / f"copy_text_{timestamp}.txt"
    result_path = RUNTIME_DIR / f"publish_result_{timestamp}.json"
    screenshot_path = RUNTIME_DIR / f"publish_{timestamp}.png"
    summary_path = RUNTIME_DIR / f"run_summary_{timestamp}.md"

    benchmark_service = TikHubXiaohongshuService()
    benchmark_result = subprocess_run_async(
        retry_async(
            lambda: benchmark_service.collect_keyword_notes(args.keyword),
            retries=3,
            delay_seconds=2,
        )
    )

    payload = build_publish_payload(
        keyword=args.keyword,
        notes=benchmark_result["notes"],
        account_positioning=args.account_positioning,
        target_audience=args.target_audience,
        content_direction=args.content_direction,
        tone_style=args.tone_style,
    )

    copy_text = render_copy_text(payload)
    copy_text_path.write_text(copy_text, encoding="utf-8")

    image_service = XiaohongshuImageService()
    prompt_framework_text = (
        RUNTIME_DIR.parent / "references" / "小红书配图提示词框架.txt"
    ).read_text(encoding="utf-8")
    images_result = subprocess_run_async(
        retry_async(
            lambda: image_service.generate_xiaohongshu_images(
                copy_text=copy_text,
                prompt_framework_text=prompt_framework_text,
                image_count=3,
            ),
            retries=2,
            delay_seconds=2,
        )
    )

    payload["publish_mode"] = args.publish_mode
    payload["image_paths"] = [image["path"] for image in images_result["images"]]
    payload["benchmark_markdown_path"] = benchmark_result["markdown_path"]
    write_json(payload_path, payload)

    env = os.environ.copy()
    env["XHS_PUBLISH_CONFIG_PATH"] = str(payload_path)
    env["XHS_STORAGE_STATE_PATH"] = str(Path(args.storage_state_path))
    env["XHS_RESULT_PATH"] = str(result_path)
    env["XHS_SCREENSHOT_PATH"] = str(screenshot_path)
    env["XHS_PUBLISH_MODE"] = args.publish_mode
    env["XHS_HELPER_MODULE_PATH"] = str(RUNTIME_DIR / "publish_helpers.js")

    publish_script_path = RUNTIME_DIR / "publish_note_with_storage_state.js"
    run_js_path = Path(args.playwright_skill_dir) / "run.js"
    completed = subprocess.run(
        ["node", str(run_js_path), str(publish_script_path)],
        cwd=args.playwright_skill_dir,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.stdout:
        write_console_text(completed.stdout, stream=sys.stdout)
    if completed.stderr:
        write_console_text(completed.stderr, stream=sys.stderr)
    if completed.returncode != 0:
        return completed.returncode

    publish_result = json.loads(result_path.read_text(encoding="utf-8"))
    summary = render_summary(
        keyword=args.keyword,
        benchmark_markdown_path=benchmark_result["markdown_path"],
        payload=payload,
        images_result=images_result,
        publish_result=publish_result,
        summary_path=summary_path,
        screenshot_path=screenshot_path,
    )
    write_markdown(summary_path, summary)
    print(f"SUMMARY_PATH={summary_path}")
    return 0


def subprocess_run_async(awaitable: Any) -> Any:
    import asyncio

    return asyncio.run(awaitable)


if __name__ == "__main__":
    raise SystemExit(main())
