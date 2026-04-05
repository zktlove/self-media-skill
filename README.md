# Self Media Skill

一个给 AI 编码 Agent 用的自媒体 skill 工作区。

这个仓库现在只放 skill 本体，不放 npm 安装器源码。npm 只是安装入口，真正被安装到各类 Agent 里的内容，就是这里这套目录。

## 这套 Skill 是干什么的

它主要解决两类事：

- 抖音 / 短视频方向：搜素材、看热点、下视频、抽音频、转写、拆结构、出文案
- 小红书方向：找对标、写标题正文、生成配图、自动上传发布

根目录 `SKILL.md` 只负责分流：

- 抖音文案、视频取材、热点检索，走 `social-copywriting-workflow`
- 小红书成稿、配图、自动发布，走 `xiaohongshu-auto-publish`

## 先看这个：你提前要准备什么

如果你只想看最实用的部分，看这一节就够了。

| 平台 / 能力 | 用在什么地方 | 你要准备什么 | 地址 |
| --- | --- | --- | --- |
| TikHub | 抖音视频搜索、小红书对标内容采集 | 注册账号、验证邮箱、创建 API Token / Key | [官网](https://www.tikhub.io) / [用户后台](https://user.tikhub.io) / [接口文档](https://docs.tikhub.io) / [API](https://api.tikhub.io) |
| 火山方舟 / 豆包生图 | 小红书配图生成 | 如果你沿用当前默认的豆包生图链路，需要你自己的模型调用权限和 Key | [火山方舟产品页](https://www.volcengine.com/product/ark) / [方舟控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/model?vendor=Bytedance&view=DEFAULT_VIEW) |
| 小红书创作服务平台 | 自动上传和发布图文 | 准备一个可登录的小红书账号，并导出浏览器 `storage state` | [发布页](https://creator.xiaohongshu.com/publish/publish) |
| 抖音网页版 | 主页抓取、热榜、部分依赖登录态的接口 | 准备一个可登录的抖音账号，采集 Cookie / `msToken` | [抖音网页版](https://www.douyin.com/) |
| SenseVoice / ModelScope | 本地音频转文字 | 不需要付费接口，但要装依赖并下载模型 | [SenseVoice GitHub](https://github.com/FunAudioLLM/SenseVoice) / [ModelScope 模型页](https://www.modelscope.cn/models/iic/SenseVoiceSmall) |
| Playwright | 浏览器自动登录、发布、状态校验 | 本地安装 Playwright 运行时 | [Playwright](https://playwright.dev/) |

### 大白话解释一下

- 你要跑“视频搜索”，核心是先有 `TikHub Key`
- 你要跑“生图”，如果沿用当前这套默认实现，核心是先有豆包 / 火山方舟那边的图像生成能力
- 你要跑“小红书自动发布”，核心是先有小红书账号登录态，也就是 `storage state`
- 你要跑“抖音主页抓取 / 热榜”，核心是先有抖音 Cookie
- 你要跑“本地转写”，核心不是去买 API，而是把 `SenseVoice` 模型和 Python 依赖装好

## 当前包含的 Skill

### `self-media-skill`

总入口 skill，只负责分流，不负责展开内部细节。

### `social-copywriting-workflow`

偏抖音和短视频文案生产链路，覆盖这些环节：

- 对标账号和视频研究
- 热榜与搜索结果采集
- 视频下载、音频抽取、转写
- 仿写素材沉淀
- 文案生成与结构整理

### `xiaohongshu-auto-publish`

偏小红书图文发布链路，覆盖这些环节：

- 对标内容收集
- 标题和正文生成
- 配图提示词与图片产出
- 浏览器自动上传与发布

## 仓库结构

```text
self-media-skill/
├─ SKILL.md
├─ README.md
├─ LICENSE
├─ social-copywriting-workflow/
│  ├─ SKILL.md
│  ├─ README.md
│  ├─ 01-account-positioning/
│  ├─ 02-asset-library/
│  ├─ 03-research/
│  ├─ 04-copywriting/
│  └─ scripts/
└─ xiaohongshu-auto-publish/
   ├─ SKILL.md
   ├─ references/
   └─ runtime/
```

## 安装方式

推荐用 npm 安装，但 npm 只是入口，不是项目主体。

### 1. 全局安装

```bash
npm install -g @zktlove/self-media-skill
```

### 2. 查看当前机器能识别哪些 Agent

```bash
self-media-skill list-agents
```

### 3. 安装 skill

```bash
self-media-skill install
```

常用变体：

```bash
self-media-skill install --agent codex,cursor,qoder
self-media-skill install --project
self-media-skill install --dry-run
self-media-skill update
self-media-skill uninstall --agent codex
```

## 当前兼容的工具

安装器会自动探测这些工具的 skill 目录并写入：

| Tool | 标识 |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude-code` |
| Cursor | `cursor` |
| Trae | `trae` |
| OpenCode | `opencode` |
| GitHub Copilot | `github-copilot` |
| Gemini CLI | `gemini-cli` |
| Kimi Code CLI | `kimi-cli` |
| Windsurf | `windsurf` |
| OpenClaw | `openclaw` |
| Trae CN | `trae-cn` |
| Qoder | `qoder` |
| Qwen Code | `qwen-code` |

## 这套安装器怎么发现路径

不是靠“扫盘乱猜”，也不是完全靠“写死单一路径”。

当前逻辑更像是“兼容表 + 本地发现”：

1. 每个 Agent 预先定义一套全局路径、项目路径和标记目录
2. 安装时先判断你机器上哪些工具真的存在
3. 再把这个 skill 仓库内容安装到对应的 skill 目录
4. 优先 symlink，失败就回退 copy

所以它不是盲扫全盘，但也不是只支持一种固定目录。它是按不同工具的既有约定路径做兼容发现。

## 平台申请和配置怎么落到项目里

### 1. TikHub：视频搜索和对标采集最先要配

这个项目里，TikHub 主要用在两块：

- `social-copywriting-workflow/scripts/search_videos.py`
- `social-copywriting-workflow/scripts/search_to_copywriting.py`
- 小红书完整工作流里的对标内容采集

实际配置方式很简单：

1. 去 TikHub 注册账号
2. 验证邮箱
3. 在用户后台创建 API Token / Key
4. 把 `social-copywriting-workflow/scripts/.env.example` 复制成 `social-copywriting-workflow/scripts/.env`
5. 填入：

```env
TIKHUB_KEY=你的真实Key
```

### 2. 火山方舟 / 豆包生图：小红书配图默认会用到

当前小红书 workflow 的参考说明里，默认生图模型是 `doubao-seedream-5-0-260128`。

这意味着如果你沿用这套默认实现，通常要提前准备：

- 火山引擎账号
- 火山方舟相关模型调用权限
- 你自己的 API Key 或你自己的 MCP 封装

这里要特别说明一句：

- 这个仓库里放的是 skill 和 workflow
- 真正的生图服务实现，不在这个仓库里
- 也就是说，README 这里说明的是“默认依赖方向”
- 你完全可以把它替换成你自己的图像服务，只要 workflow 对接保持一致

### 3. 小红书发布：核心不是 Key，而是登录态

自动发布走的是浏览器自动化，不是开放 API。

你真正要提前准备的是：

- 一个可正常登录的小红书账号
- 浏览器导出的 `storage state`

当前发布脚本目标地址就是：

- `https://creator.xiaohongshu.com/publish/publish`

### 4. 抖音登录态：主页抓取和热榜会用到

这部分不是先去买接口，而是先准备登录态。

你需要：

- 一个可正常登录的抖音账号
- Cookie / `msToken`

建议流程：

1. 先跑 `check_cookie_status.py`
2. 再跑 `validate_douyin_session.py`
3. 缺登录态时，用 Playwright 走一次登录
4. 最后把 Cookie 保存到 `scripts/cookies/`

### 5. SenseVoice：本地转写不用买 API

这一块是本地模型方案，不是 SaaS 接口方案。

你要做的是：

1. 建 Python 虚拟环境
2. 安装 `requirements-base.txt` 和 `requirements-transcribe.txt`
3. 跑 `ensure_models.py`
4. 再跑 `transcribe_audio.py`

## 使用方式

### 路线 A：抖音搜索 -> 下载 -> 抽音频 -> 转写 -> 仿写

先准备 Python 环境：

```powershell
cd social-copywriting-workflow\scripts
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-base.txt
pip install -r requirements-transcribe.txt
```

然后填好 `scripts/.env` 里的 `TIKHUB_KEY`。

搜索视频：

```powershell
python search_videos.py 女装穿搭 --pages 1
```

直接生成仿写素材包：

```powershell
python search_to_copywriting.py 女装穿搭 --limit 3
```

### 路线 B：对标视频直链 -> 本地转写

```powershell
python download_video.py "你的对标视频URL"
python extract_audio.py "本地视频文件路径"
python ensure_models.py
python transcribe_audio.py "本地音频文件路径"
```

### 路线 C：小红书完整工作流

先准备这三样：

- TikHub Key
- 生图服务能力
- 小红书 `storage state`

然后再执行：

```powershell
python runtime/run_full_workflow.py --keyword "AI副业" --publish-mode stop_before_publish
```

如果你要直接发：

```powershell
python runtime/run_full_workflow.py --keyword "AI副业" --publish-mode publish
```

## 两个非常重要的提醒

### 1. 小红书完整工作流依赖外部 MCP 实现

当前 `xiaohongshu-auto-publish/runtime/run_full_workflow.py` 会去找外部的 `mcp` 目录和对应服务实现。

换句话说：

- 这个仓库不是一个“把所有服务都塞满”的大杂烩
- 它更像是一套 skill + workflow 规范层
- 真正的采集、生图、payload 组装服务，可以由你自己的 MCP 工程提供

### 2. 抖音搜索和抖音登录态不是一回事

这个仓库已经把这两件事拆开了：

- 搜索：优先走 TikHub
- 登录态链路：主页抓取、热榜、部分详情接口走 Cookie

这能让你的使用更稳，不用什么都绑在浏览器上。

## 使用建议

- 想改总入口分流逻辑，修改根目录 `SKILL.md`
- 想改抖音文案工作流，改 `social-copywriting-workflow/`
- 想改小红书自动发布工作流，改 `xiaohongshu-auto-publish/`
- npm 安装器代码已经拆到独立工程，不在这个仓库维护

## License

MIT
