# Self Media Skill

一个给 AI 编码 Agent 用的自媒体 skill 。


## 这套 Skill 是干什么的

它主要解决两类事：

- 抖音 / 短视频方向：搜素材、看热点、下视频、抽音频、转写、拆结构、出文案
- 小红书方向：找对标、写标题正文、生成配图、自动上传发布

根目录 `SKILL.md` 只负责分流：

- 抖音文案、视频取材、热点检索，走 `social-copywriting-workflow`
- 小红书成稿、配图、自动发布，走 `xiaohongshu-auto-publish`

## 提前准备：

如果你只想看最实用的部分，看这一节就够了。

| 平台 / 能力 | 用在什么地方 | 你要准备什么 | 地址 |
| --- | --- | --- | --- |
| TikHub | 抖音视频搜索、小红书对标内容采集 | 注册账号、验证邮箱、创建 API Token / Key | [官网](https://www.tikhub.io) / [用户后台](https://user.tikhub.io) / [接口文档](https://docs.tikhub.io) / [API](https://api.tikhub.io) |
| 火山方舟 / 豆包生图 | 小红书配图生成 | 如果你沿用当前默认的豆包生图链路，需要你自己的模型调用权限和 Key | [火山方舟产品页](https://www.volcengine.com/product/ark) / [方舟控制台]

### 解释

- 跑“视频搜索”，核心是先有 `TikHub Key`
- 跑“生图”，如果沿用当前这套默认实现，核心是先有豆包 / 火山方舟那边的图像生成能力


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


## 平台申请和配置怎么落到项目里

### 1. TikHub：视频搜索和对标采集最先要配

这个项目里，TikHub 主要用在两块：

- `social-copywriting-workflow/scripts/search_videos.py`
- `social-copywriting-workflow/scripts/search_to_copywriting.py`
- 小红书完整工作流里的对标内容采集

配置方式：

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


### 3. 抖音登录态：主页抓取和热榜会用到

这部分不是先去买接口，而是先准备登录态。

你需要：

- 一个可正常登录的抖音账号
- Cookie / `msToken`

建议流程：

1. 先跑 `check_cookie_status.py`
2. 再跑 `validate_douyin_session.py`
3. 缺登录态时，用 Playwright 走一次登录
4. 最后把 Cookie 保存到 `scripts/cookies/`

### 4. SenseVoice：本地转写不用买 API

这一块是本地模型方案，不是接口方案。

你要做的是：

1. 建 Python 虚拟环境
2. 安装 `requirements-base.txt` 和 `requirements-transcribe.txt`
3. 跑 `ensure_models.py`
4. 再跑 `transcribe_audio.py`

## 使用方式

### 路线 A：文案仿写

准备一个视频URL并发送AI：“根据这个视频帮我仿写一篇文案”

### 路线 B：对标视频直链 -> 本地转写

准备一个视频URL并发送AI：“把视频文案转为本地文本”

### 路线 C：小红书完整工作流

发送AI：“帮我写一篇关于【AI副业】的小红书帖子并进行发布”


## 使用建议

- 想改总入口分流逻辑，修改根目录 `SKILL.md`
- 想改抖音文案工作流，改 `social-copywriting-workflow/`
- 想改小红书自动发布工作流，改 `xiaohongshu-auto-publish/`

## License

MIT
