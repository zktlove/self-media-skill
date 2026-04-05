from __future__ import annotations

import argparse
from pathlib import Path

from common.sensevoice import build_model, clean_transcript
from common.utils import ensure_dir, iter_audio_files, write_text


def main() -> None:
    parser = argparse.ArgumentParser(description="用 SenseVoice 把音频转成纯文本。")
    parser.add_argument("input_path", type=Path, help="音频文件或目录")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "transcripts",
        help="TXT 输出目录",
    )
    parser.add_argument(
        "--models-root",
        type=Path,
        default=Path(__file__).resolve().parent / "models",
        help="Skill 自己的模型目录",
    )
    parser.add_argument("--recursive", action="store_true", help="目录模式下递归扫描")
    parser.add_argument("--device", default="auto", help="auto、cpu、cuda:0 等")
    parser.add_argument("--language", default="auto", help="zh、en、yue、ja、ko、auto")
    parser.add_argument("--batch-size-s", type=int, default=60, help="动态 batch 秒数")
    args = parser.parse_args()

    ensure_dir(args.output_dir)
    files = list(iter_audio_files(args.input_path, recursive=args.recursive))
    if not files:
        raise SystemExit("没有找到可处理的音频文件。")

    try:
        model = build_model(args.models_root, device=args.device)
    except ImportError as exc:
        raise SystemExit(
            "缺少 FunASR 或 ModelScope 依赖。请先在 scripts/.venv 里安装 requirements-transcribe.txt。"
        ) from exc

    for audio_file in files:
        result = model.generate(
            input=str(audio_file),
            cache={},
            language=args.language,
            use_itn=True,
            batch_size_s=args.batch_size_s,
            merge_vad=True,
            merge_length_s=15,
            ban_emo_unk=True,
        )
        raw_text = ""
        if result and isinstance(result, list):
            raw_text = str(result[0].get("text", ""))
        text = clean_transcript(raw_text)
        output_path = args.output_dir / f"{audio_file.stem}.txt"
        write_text(output_path, text)
        print(f"已输出: {output_path}")


if __name__ == "__main__":
    main()
