from __future__ import annotations

import argparse
from pathlib import Path

from common.sensevoice import ensure_models


def main() -> None:
    parser = argparse.ArgumentParser(description="检查并下载 Skill 自己目录里的 SenseVoice 和 VAD 模型。")
    parser.add_argument(
        "--models-root",
        type=Path,
        default=Path(__file__).resolve().parent / "models",
        help="模型保存目录，默认保存到 scripts/models",
    )
    args = parser.parse_args()

    try:
        sensevoice_dir, vad_dir = ensure_models(args.models_root)
    except ImportError as exc:
        raise SystemExit(
            "缺少 modelscope 依赖。请先在 scripts/.venv 中安装 requirements-transcribe.txt。"
        ) from exc

    print(f"SenseVoice 模型目录: {sensevoice_dir}")
    print(f"VAD 模型目录: {vad_dir}")


if __name__ == "__main__":
    main()
