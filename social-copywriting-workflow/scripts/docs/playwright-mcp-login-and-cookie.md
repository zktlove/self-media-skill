# Playwright MCP 登录与 Cookie 流程

这个文档只负责一件事：

- 当抖音登录态缺失或不完整时，怎么补齐 Skill 需要的 Cookie

## 什么时候需要执行

先运行：

```powershell
python validate_douyin_session.py
```

如果结果不是 `ready`，再继续下面的补齐流程。

## 执行顺序

1. 运行 `python detect_browser_for_login.py`
2. 优先使用本地 Chrome
3. 如果没有 Chrome，就退回默认浏览器
4. 打开抖音登录页，让用户手动完成登录
5. 用户确认“已登录”后，导出浏览器上下文 Cookie 或 storage state
6. 执行：

```powershell
python save_playwright_cookies.py 路径\\playwright-storage-state.json --browser-name chrome
```

7. 再运行：

```powershell
python validate_douyin_session.py
```

## 结果文件

Cookie 会保存到：

- `scripts/cookies/douyin_cookie.json`
- `scripts/cookies/douyin_cookie.txt`
- `scripts/cookies/douyin_cookie_meta.json`

## 最低完整性要求

至少要有：

- `msToken`
- `__ac_nonce`

缺任何一个，都不要继续执行依赖登录态的抖音脚本。
