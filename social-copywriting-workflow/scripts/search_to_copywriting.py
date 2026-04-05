from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from common.media import extract_audio
from common.sensevoice import build_model, clean_transcript
from common.tikhub_client import TikHubSearchClient
from common.download import download_file
from common.utils import ensure_dir, sanitize_filename, now_string, write_json, write_text


SearchClientFactory = Callable[[], object]


def default_transcribe(audio_path: Path, output_path: Path, *, model: object, language: str, batch_size_s: int) -> Path:
    result = model.generate(
        input=str(audio_path),
        cache={},
        language=language,
        use_itn=True,
        batch_size_s=batch_size_s,
        merge_vad=True,
        merge_length_s=15,
        ban_emo_unk=True,
    )
    raw_text = ""
    if result and isinstance(result, list):
        raw_text = str(result[0].get("text", ""))
    text = clean_transcript(raw_text)
    write_text(output_path, text)
    return output_path


def build_package_markdown(
    *,
    keyword: str,
    package_json_path: Path,
    references: list[dict[str, object]],
) -> str:
    lines = [
        "# 搜索结果转仿写素材包",
        "",
        f"- 关键词：`{keyword}`",
        f"- 参考视频数：`{len(references)}`",
        f"- 素材包 JSON：`{package_json_path}`",
        "",
        "## 仿写执行要求",
        "",
        "1. 仿写前必须先完整拆解对标文案结构，至少看清开头钩子、主体分段、结尾收口、情绪推进和转化动作。",
        "2. 仿写时要严格对齐原文案的结构和大致字数，不能只改几个词就直接输出。",
        "3. 如果对标文案是口播型内容，先拆结构，再结合转写文本还原节奏，最后按相同结构重写。",
        "4. 输出仿写稿时，要保证内容原创、表达自然，但结构逻辑和篇幅控制要与对标样本一致。",
        "",
        "## 参考列表",
        "",
    ]
    for index, item in enumerate(references, start=1):
        lines.extend(
            [
                f"### 参考 {index}",
                "",
                f"- 标题：{item['title']}",
                f"- 作者：{item['author']}",
                f"- 点赞：{item['digg_count']}",
                f"- 视频路径：`{item['video_path']}`",
                f"- 音频路径：`{item['audio_path']}`",
                f"- 转写路径：`{item['transcript_path']}`",
                "",
                "#### 转写正文",
                "",
                item["transcript_text"] or "无转写内容",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def run_pipeline(
    *,
    keyword: str,
    output_dir: Path,
    limit: int = 3,
    pages: int = 1,
    platform: str = "抖音",
    topic: str = "",
    goal: str = "仿写同赛道参考",
    device: str = "auto",
    language: str = "auto",
    batch_size_s: int = 60,
    overwrite: bool = False,
    ffmpeg_bin: str = "ffmpeg",
    search_client_factory: SearchClientFactory | None = None,
    download_func: Callable[..., Path] = download_file,
    extract_audio_func: Callable[..., Path] = extract_audio,
    transcribe_func: Callable[..., Path] | None = None,
) -> dict[str, object]:
    ensure_dir(output_dir)
    videos_dir = ensure_dir(output_dir / "videos")
    audio_dir = ensure_dir(output_dir / "audio")
    transcripts_dir = ensure_dir(output_dir / "transcripts")
    search_output_path = output_dir / "search_results.json"
    package_json_path = output_dir / "copywriting_package.json"
    package_markdown_path = output_dir / "copywriting_package.md"

    client_factory = search_client_factory or TikHubSearchClient
    collected_items: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    cursor: int | None = None
    search_id = ""
    backtrace = ""
    with client_factory() as client:
        for page_index in range(max(1, pages)):
            summary = client.search_videos(
                keyword,
                cursor=cursor if page_index > 0 else None,
                search_id=search_id if page_index > 0 else "",
                backtrace=backtrace if page_index > 0 else "",
            )
            diagnostics.extend(summary.get("diagnostics", []))
            collected_items.extend(summary.get("items", []))
            if not summary.get("has_more"):
                break
            cursor = int(summary.get("next_cursor") or 0)
            search_id = str(summary.get("search_id") or "")
            backtrace = str(summary.get("backtrace") or "")
            if not cursor or not search_id or not backtrace:
                break

    unique_items: dict[str, dict[str, object]] = {}
    for item in collected_items:
        aweme_id = str(item.get("aweme_id", "")).strip()
        if not aweme_id or aweme_id in unique_items:
            continue
        unique_items[aweme_id] = item
    ranked_items = sorted(unique_items.values(), key=lambda item: int(item.get("digg_count", 0) or 0), reverse=True)
    selected_items = ranked_items[: max(1, limit)]

    model = None
    effective_transcribe = transcribe_func
    if effective_transcribe is None:
        model = build_model(Path(__file__).resolve().parent / "models", device=device)

        def effective_transcribe(audio_path: Path, output_path: Path, **_: object) -> Path:
            assert model is not None
            return default_transcribe(
                audio_path,
                output_path,
                model=model,
                language=language,
                batch_size_s=batch_size_s,
            )

    references: list[dict[str, object]] = []
    for index, item in enumerate(selected_items, start=1):
        stem = sanitize_filename(f"{index:02d}_{item.get('author', '')}_{item.get('title', '')}_{item.get('aweme_id', '')}")
        video_path = videos_dir / f"{stem}.mp4"
        audio_path = audio_dir / f"{stem}.wav"
        transcript_path = transcripts_dir / f"{stem}.txt"
        download_func(str(item.get("direct_download_url") or ""), video_path, overwrite=overwrite)
        extract_audio_func(video_path, audio_path, ffmpeg_bin=ffmpeg_bin, overwrite=overwrite)
        effective_transcribe(audio_path, transcript_path, overwrite=overwrite)
        transcript_text = transcript_path.read_text(encoding="utf-8").strip() if transcript_path.exists() else ""
        references.append(
            {
                **item,
                "video_path": str(video_path),
                "audio_path": str(audio_path),
                "transcript_path": str(transcript_path),
                "transcript_text": transcript_text,
            }
        )

    search_payload = {
        "keyword": keyword,
        "platform": platform,
        "topic": topic,
        "goal": goal,
        "count": len(ranked_items),
        "items": ranked_items,
        "diagnostics": diagnostics,
    }
    write_json(search_output_path, search_payload)

    package_payload = {
        "keyword": keyword,
        "platform": platform,
        "topic": topic,
        "goal": goal,
        "reference_count": len(references),
        "references": references,
        "search_results_path": str(search_output_path),
        "docs": {
            "structure_guide": str(Path(__file__).resolve().parent.parent / "04-copywriting" / "rewrite-structure-guide.md"),
            "generation_guide": str(Path(__file__).resolve().parent.parent / "04-copywriting" / "overview.md"),
            "generation_template": str(Path(__file__).resolve().parent.parent / "04-copywriting" / "generation-template.md"),
            "final_rules": str(Path(__file__).resolve().parent.parent / "04-copywriting" / "finalization-rules.md"),
        },
    }
    write_json(package_json_path, package_payload)
    write_text(
        package_markdown_path,
        build_package_markdown(
            keyword=keyword,
            package_json_path=package_json_path,
            references=references,
        ),
    )
    return {
        "search_results": str(search_output_path),
        "package_json": str(package_json_path),
        "package_markdown": str(package_markdown_path),
        "reference_count": len(references),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="把 TikHub 搜索结果直接转成可仿写的下载/转写素材包。")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--limit", type=int, default=3, help="最多处理前几条视频，默认 3")
    parser.add_argument("--pages", type=int, default=1, help="最多抓取页数，默认 1")
    parser.add_argument("--platform", default="抖音", help="创作平台，默认 抖音")
    parser.add_argument("--topic", default="", help="当前创作主题，可选")
    parser.add_argument("--goal", default="仿写同赛道参考", help="当前创作目标，可选")
    parser.add_argument("--device", default="auto", help="转写设备，auto、cpu、cuda:0 等")
    parser.add_argument("--language", default="auto", help="转写语言，默认 auto")
    parser.add_argument("--batch-size-s", type=int, default=60, help="转写动态 batch 秒数")
    parser.add_argument("--overwrite", action="store_true", help="已存在时覆盖")
    parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg 可执行文件名或路径")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / f"search_copywriting_{now_string()}",
        help="输出目录",
    )
    args = parser.parse_args()

    result = run_pipeline(
        keyword=args.keyword,
        output_dir=args.output_dir,
        limit=args.limit,
        pages=args.pages,
        platform=args.platform,
        topic=args.topic,
        goal=args.goal,
        device=args.device,
        language=args.language,
        batch_size_s=args.batch_size_s,
        overwrite=args.overwrite,
        ffmpeg_bin=args.ffmpeg_bin,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
