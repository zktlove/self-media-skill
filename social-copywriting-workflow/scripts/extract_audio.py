from __future__ import annotations

import argparse
from pathlib import Path

from common.media import extract_audio
from common.utils import ensure_dir, iter_video_files


def main() -> None:
    parser = argparse.ArgumentParser(description="从本地视频中提取音频。")
    parser.add_argument("input_path", type=Path, help="视频文件或目录")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "audio",
        help="音频输出目录",
    )
    parser.add_argument("--recursive", action="store_true", help="目录模式下递归扫描")
    parser.add_argument("--overwrite", action="store_true", help="已存在时覆盖")
    parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg 可执行文件名或路径")
    args = parser.parse_args()

    ensure_dir(args.output_dir)
    files = list(iter_video_files(args.input_path, recursive=args.recursive))
    if not files:
        raise SystemExit("没有找到可处理的视频文件。")

    for video_file in files:
        output_path = args.output_dir / f"{video_file.stem}.wav"
        extract_audio(
            video_file,
            output_path,
            ffmpeg_bin=args.ffmpeg_bin,
            overwrite=args.overwrite,
        )
        print(f"已输出: {output_path}")


if __name__ == "__main__":
    main()
