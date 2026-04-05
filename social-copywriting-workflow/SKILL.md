---
name: social-copywriting-workflow
description: 当用户要基于对标视频 URL、文案结构，或仅凭主题想法生成抖音/小红书/视频号文案时使用；也适用于需要在 Skill 内调用抖音搜索、主页抓取、视频解析下载、音频抽取、转写和热榜查询脚本的场景。
---

# Social Copywriting Workflow

这个 Skill 现在按用户输入走分流，不再走固定单一路径。

## 先判断用户给了什么

只看三类入口，优先级从高到低如下：

1. 给了对标视频 URL
2. 没给对标视频，但给了明确的文案结构
3. 既没给对标视频，也没给结构，只有主题、想法、方向

如果同时给了多个输入，优先走更具体的入口。

## 入口一：给了对标视频 URL

这是“直接模仿”链路，按顺序执行，不跳步。

### 1. 先做视频侧取材

优先使用 Skill 自带脚本：

- `scripts/download_video.py`
- `scripts/extract_audio.py`
- `scripts/transcribe_audio.py`

调用顺序：

1. 用 `download_video.py` 解析并下载对标视频到本地
2. 用 `extract_audio.py` 从视频中抽出音频
3. 用 `transcribe_audio.py` 将音频转成纯文本文案

转写要求：

- 使用 Skill 目录自己的 SenseVoice 模型
- 不复用外部现成模型目录
- 不要情绪标签
- 不要 emoji 符号转换
- 输出结果按纯文本理解和仿写

### 2. 再做文案拆解

读取并使用：

- `04-copywriting/rewrite-structure-guide.md`
- `04-copywriting/overview.md`
- `04-copywriting/generation-template.md`
- 对应平台规则文件

拆解重点：

- 骨架结构
- 论证逻辑
- 情绪触发点
- 人群与场景
- 结尾引导方式

### 3. 最后输出仿写结果

输出时坚持：

- 结构可借
- 逻辑可复用
- 内容必须重写
- 案例和表达要换成当前账号/当前主题语境

## 入口二：给了文案结构

这是“结构驱动原创”链路。

按顺序执行：

1. 拆解与理解文案结构
2. 梳理这个结构的适用场景、风险点、注意事项
3. 基于当前主题和账号定位输出原创文案

需要优先读取：

- `01-account-positioning/account-profile.md`
- `01-account-positioning/notes.md`
- `02-asset-library/viral-structures/`
- `02-asset-library/hooks/`
- `04-copywriting/overview.md`
- `04-copywriting/generation-template.md`

如果用户给的结构过于抽象，只补问最关键的 1 到 3 个问题，不要把问题问散。

## 入口三：只有主题、想法、方向

这是“预设结构选型”链路。

按顺序执行：

1. 拆解与理解用户主题
2. 从现有素材中挑适配的预设文案结构
3. 用选中的结构输出文案

优先读取：

- `01-account-positioning/account-profile.md`
- `01-account-positioning/notes.md`
- `02-asset-library/viral-structures/`
- `02-asset-library/hooks/`
- `02-asset-library/case-library/`
- `04-copywriting/overview.md`
- `04-copywriting/generation-template.md`

没有把握时，不要硬写成万能废话，要先把用户真实诉求、人群、口吻和目标拉清楚。

## 抖音脚本能力

脚本目录：

- `scripts/`

脚本能力只保留当前 Skill 真正要用到的部分，来源于 TikTokDownloader 的必要模块拆分，不整仓复制。

### 可直接调用的脚本

- `scripts/search_videos.py`
  - 关键词搜抖音视频
- `scripts/search_to_copywriting.py`
  - 关键词搜索后，直接下载视频、抽音频、转写，并输出仿写素材包
- `scripts/fetch_homepage_videos.py`
  - 根据主页 URL 抓取主页作品
- `scripts/download_video.py`
  - 根据视频 URL 解析详情并直接下载视频
- `scripts/query_hotlist.py`
  - 查询抖音热榜
- `scripts/extract_audio.py`
  - 从本地视频抽音频
- `scripts/transcribe_audio.py`
  - 用 SenseVoice 把音频转成纯文本
- `scripts/ensure_models.py`
  - 检查并下载 Skill 自己目录里的 SenseVoice 和 VAD 模型

### 搜索和登录态分开处理

不要再把搜索和浏览器登录态绑死。

规则分成两类：

1. TikHub 搜索链路
2. 抖音登录态链路

#### TikHub 搜索链路

- `scripts/search_videos.py`
- `scripts/search_to_copywriting.py`

这两条默认读取：

- 由 `scripts/.env.example` 复制出来的 `scripts/.env` 里的 `TIKHUB_KEY`

默认不依赖 Cookie，也不依赖浏览器。

#### 抖音登录态链路

- `scripts/fetch_homepage_videos.py`
- `scripts/download_video.py`
- `scripts/query_hotlist.py`

这些默认读取 Skill 自己目录里的 Cookie。

Cookie 目录：

- `scripts/cookies/`

执行前先运行：

- `scripts/check_cookie_status.py`
- `scripts/validate_douyin_session.py`

判断逻辑：

1. Cookie 存在且完整：继续执行登录态相关脚本
2. Cookie 不存在或不完整：先走 Playwright MCP 登录采集流程
3. 浏览器只用于登录和验证，不再参与搜索结果抓取

完整性最低要求：

- `msToken`
- `__ac_nonce`

只要缺一个，都算不完整。

### Playwright MCP 检测与登录采集流程

先确认当前会话能否直接使用 Playwright MCP。

如果当前会话没有可用的 Playwright 浏览器自动化能力，就先读取并使用：

- `C:\Users\zktst\.codex\skills\playwright-skill\SKILL.md`

并按里面的首次安装方式执行：

```powershell
cd C:\Users\zktst\.codex\skills\playwright-skill
npm run setup
```

然后按下面顺序执行：

1. 先运行 `scripts/validate_douyin_session.py`，确认当前是 `ready` 还是 `need_login`
2. 如果不是 `ready`，再运行 `scripts/detect_browser_for_login.py`
3. 本地有 Chrome，优先用 Chrome 登录抖音
4. 本地没有 Chrome，就退回设备默认浏览器
5. 打开 `https://www.douyin.com/`
6. 明确提示用户在浏览器中完成登录校验
7. 等用户确认“已登录”
8. 导出当前浏览器上下文 Cookie 或 storage state JSON
9. 用 `scripts/save_playwright_cookies.py <导出的 JSON 路径>` 保存到 Skill 目录
10. 保存到：
   - `scripts/cookies/douyin_cookie.json`
   - `scripts/cookies/douyin_cookie.txt`
   - `scripts/cookies/douyin_cookie_meta.json`
11. 再重新执行 `scripts/validate_douyin_session.py`
12. 只有状态变成 `ready`，才继续执行依赖登录态的抖音脚本

### 抖音接口补充

`search_videos.py` 和 `search_to_copywriting.py` 会先读 `scripts/.env` 里的 `TIKHUB_KEY`。

`fetch_homepage_videos.py`、`download_video.py`、`query_hotlist.py` 会先读 `scripts/cookies/` 下的 Cookie 文件。

其中登录态链路建议固定先跑：

- `scripts/validate_douyin_session.py`

如果需要临时覆盖登录态，也支持下面两种方式补浏览器态：

- 直接传 `--cookie`、`--ms-token`
- 或设置环境变量 `DOUYIN_COOKIE`、`DOUYIN_MS_TOKEN`

如果脚本提示 Cookie 不完整，就不要继续请求依赖登录态的接口，先完成 Playwright MCP 登录采集。

### 什么时候调用这些脚本

- 用户给了对标视频 URL：优先用 `download_video.py`、`extract_audio.py`、`transcribe_audio.py`
- 用户要搜同赛道参考并直接进入仿写取材：优先用 `search_to_copywriting.py`
- 用户只要搜索结果列表：用 `search_videos.py`
- 用户给了主页 URL 想看作品：用 `fetch_homepage_videos.py`
- 用户要看近期热点：用 `query_hotlist.py`

## 模型与依赖规则

### 模型存放位置

模型只放在 Skill 自己目录下：

- `scripts/models/SenseVoiceSmall`
- `scripts/models/fsmn-vad`

### 首次下载逻辑

当需要音频转文字时，先检查上述目录是否存在。

- 已存在：直接复用
- 不存在：先运行 `scripts/ensure_models.py`

`ensure_models.py` 的职责：

1. 先检查 Skill 内模型目录
2. 缺失时，按 FunASR / SenseVoice 官方仓库说明，从模型仓库下载
3. 下载完成后再给 `transcribe_audio.py` 使用

注意：

- 不要默认复用 `D:\AI_project\douyin_wenan_zhuanhuan\models`
- 不要把模型文件直接打包进 Skill
- 不要把情绪和 emoji 丰富化后再交给文案流程

## Python 执行约定

这是 Python 脚本型 Skill，安装依赖时必须先建虚拟环境，禁止全局安装。

建议虚拟环境位置：

- `scripts/.venv`

依赖文件：

- `scripts/requirements-base.txt`
- `scripts/requirements-transcribe.txt`

## 查询结果落位建议

按用途写回现有资料目录：

- 搜索结果：`03-research/peer-content/`
- 搜索转仿写素材包：`03-research/peer-content/copywriting-packages/`
- 主页抓取：`03-research/benchmark-accounts/`
- 热榜结果：`03-research/hot-trends/`
- 仿写结构说明：`04-copywriting/rewrite-structure-guide.md`

## NPM CLI 分发架构

这个 Skill 现在额外保留一套 npm CLI 分发骨架，但不把本地 Python 脚本硬改成 Node。

分工固定如下：

- `SKILL.md`、`memory.md`、资料目录：负责 Skill 本体
- `scripts/`：负责本地 Python 执行能力
- `package.json`：负责 npm 包元数据
- `npm/install.js`：负责 npm 安装后的运行时准备
- `npm/run.js`：负责 npm 命令入口
- `npm/cli-manifest.json`：负责后续 GitHub Release / 二进制下载配置
- `README.md`：负责对外安装、更新、发布说明

当前阶段先固定架构，不伪造完整 CLI 功能。

也就是说：

- 可以先按 npm 包方式组织目录
- 可以先约定安装、更新、版本和发布路径
- 真实平台二进制或完整 Node CLI 没补齐前，只保留占位安装器和入口包装器

后续如果要正式像 `larksuite/cli` 一样分发，直接在这个骨架上补：

1. 发布产物
2. release 下载地址
3. 命令转发逻辑

## 最终输出要求

文案输出前仍要做一次自检，读取：

- `04-copywriting/finalization-rules.md`

最终默认只给用户：

- 标题
- 正文
- 话题
