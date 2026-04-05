from __future__ import annotations

import argparse
import json

from common.cookies import COOKIE_DIR, COOKIE_JSON_PATH, COOKIE_META_PATH, COOKIE_TXT_PATH, load_cookie_context


def main() -> None:
    parser = argparse.ArgumentParser(description="检查 Skill 内抖音 Cookie 是否存在且完整。")
    parser.add_argument("--json", action="store_true", help="以 JSON 打印结果")
    args = parser.parse_args()

    cookie, ms_token, status = load_cookie_context()
    payload = {
        "exists": status.exists,
        "complete": status.complete,
        "source": status.source,
        "missing_keys": status.missing_keys,
        "cookie_count": status.cookie_count,
        "has_ms_token": status.has_ms_token,
        "has_nonce": status.has_nonce,
        "cookie_dir": str(COOKIE_DIR),
        "cookie_txt": str(COOKIE_TXT_PATH),
        "cookie_json": str(COOKIE_JSON_PATH),
        "cookie_meta": str(COOKIE_META_PATH),
        "effective_cookie_length": len(cookie),
        "effective_ms_token_length": len(ms_token),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"存在: {payload['exists']}")
    print(f"完整: {payload['complete']}")
    print(f"来源: {payload['source']}")
    print(f"缺少字段: {', '.join(payload['missing_keys']) if payload['missing_keys'] else '无'}")
    print(f"Cookie TXT: {payload['cookie_txt']}")
    print(f"Cookie JSON: {payload['cookie_json']}")
    print(f"Meta: {payload['cookie_meta']}")


if __name__ == "__main__":
    main()
