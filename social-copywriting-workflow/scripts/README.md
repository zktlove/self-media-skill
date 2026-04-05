# 脚本目录说明

这个目录只保留当前 Skill 需要的脚本能力，不整仓复制 TikTokDownloader。

## 能力清单

- `search_videos.py`
  - 通过 TikHub 接口关键词搜索抖音视频
- `search_to_copywriting.py`
  - 把 TikHub 搜索结果直接串到视频下载、抽音频、转写，并输出可仿写素材包
- `fetch_homepage_videos.py`
  - 通过主页 URL 或 `sec_user_id` 抓主页作品
- `download_video.py`
  - 通过视频 URL 解析并下载视频
- `query_hotlist.py`
  - 查询抖音热榜
- `extract_audio.py`
  - 从本地视频提取音频
- `transcribe_audio.py`
  - 用 SenseVoice 把音频转成纯文本
- `ensure_models.py`
  - 首次缺模型时，按官方仓库方式下载模型到本 Skill 目录
- `check_cookie_status.py`
  - 检查 Skill 内抖音 Cookie 是否存在且完整
- `detect_browser_for_login.py`
  - 检测登录时优先使用 Chrome 还是默认浏览器，同时检查 Playwright 运行时是否可用
- `validate_douyin_session.py`
  - 一次性检查 Cookie 完整性、浏览器优先级、Playwright 安装状态、登录态是否可用
- `save_playwright_cookies.py`
  - 把 Playwright 导出的 Cookie JSON / storage state 保存到 Skill 的 Cookie 目录

## 依赖安装约定

先创建虚拟环境，再安装依赖，禁止全局安装。

PowerShell 示例：

```powershell
cd D:\AI_Skill\self-media-skill\social-copywriting-workflow\scripts
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-base.txt
```

如果需要音频转文字，再补：

```powershell
pip install -r requirements-transcribe.txt
```

`requirements-transcribe.txt` 默认不替你选 `torch` 的 CUDA 版本，先按本机环境装好合适的 `torch`，再装其余依赖。

## TikHub Key 规则

搜索相关脚本默认读取：

- `scripts/.env`

最低要求：

- `TIKHUB_KEY=<你的 key>`

对外分发目录中默认只保留：

- `scripts/.env.example`

首次使用时，先复制成 `scripts/.env`，再填写真实 key。

当前直接依赖 TikHub 的脚本：

- `search_videos.py`
- `search_to_copywriting.py`

这两个脚本默认不走浏览器，不走 Cookie。

## Cookie 执行规则

后续所有依赖登录态的抖音脚本默认都从 `scripts/cookies/` 读取 Cookie。

Cookie 目录：

- `scripts/cookies/`

关键文件：

- `scripts/cookies/douyin_cookie.json`
- `scripts/cookies/douyin_cookie.txt`
- `scripts/cookies/douyin_cookie_meta.json`

每次执行前先检查：

```powershell
python check_cookie_status.py
```

如果是主页抓取、直链补全、热榜这类需要登录态的流程，建议先跑完整校验：

```powershell
python validate_douyin_session.py
```

如果不存在或不完整，先不要继续执行依赖登录态的脚本，先按下面的 Playwright MCP 流程补齐 Cookie。

## Playwright MCP 检测与安装说明

详细流程文档：

- `scripts/docs/playwright-mcp-login-and-cookie.md`

如果当前会话没有可用的 Playwright 浏览器自动化能力，就先参考：

- `C:\Users\zktst\.codex\skills\playwright-skill\SKILL.md`

首次安装：

```powershell
cd C:\Users\zktst\.codex\skills\playwright-skill
npm run setup
```

浏览器检测：

```powershell
python detect_browser_for_login.py
```

完整可用性校验：

```powershell
python validate_douyin_session.py --output output\session_check.json
```

规则：

1. 本地有 Chrome，优先 Chrome
2. 没有 Chrome，回退设备默认浏览器

## 搜索脚本默认参数

`search_videos.py` 默认走 TikHub 搜索接口，不再使用浏览器搜索，也不依赖本地 Cookie。

默认值：

- `sort_type=1`，最多点赞
- `publish_time=180`，最近半年
- `filter_duration=0`，时长不限
- `content_type=1`，只取视频
- 第一页默认不传 `search_id`、`cursor`、`backtrace`

如果显式把 `--pages` 设为大于 1，脚本才会自动使用上一页返回的分页参数继续翻页。

## 搜索结果直连仿写素材包

如果你要直接把搜索结果接到下载、抽音频、转写，再交给后续仿写流程，优先使用：

```powershell
python search_to_copywriting.py 女装穿搭 --limit 3
```

这个脚本会自动完成：

1. 用 TikHub 搜索视频
2. 按点赞数从高到低排序
3. 下载前 N 条视频
4. 提取音频
5. 转成纯文本
6. 输出 `copywriting_package.json` 和 `copywriting_package.md`

## 接口参数补充

抖音主页作品、视频详情、热榜现在默认都走 Cookie。

脚本支持两种补法：

- 直接传 `--cookie`、`--ms-token`
- 或提前设置环境变量 `DOUYIN_COOKIE`、`DOUYIN_MS_TOKEN`

但默认优先级更高的是 `scripts/cookies/` 里的本地 Cookie 存档。

如果脚本提示 Cookie 不完整，先补 Cookie，不要继续裸跑。

如果是通过 Playwright MCP 导出了浏览器 Cookie JSON，再执行：

```powershell
python save_playwright_cookies.py 路径\playwright-storage-state.json --browser-name chrome
```
