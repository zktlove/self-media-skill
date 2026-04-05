# Self Media Skill

一个面向 AI 编码 Agent 的自媒体 skill 工作区。

这个仓库现在只保留 skill 本体，不再承载 npm 安装器源码。你在这里看到的内容，就是实际会被安装到各类 Agent skill 目录里的内容。

## 项目定位

这个项目解决的是两类高频工作流：

- 抖音/短视频方向的取材、检索、拆解、仿写与文案生产
- 小红书方向的选题、成稿、配图与自动发布

仓库根目录的 `SKILL.md` 是总入口，只负责做分流判断；真正执行能力在两个子 skill 目录里。

## 当前包含的 Skill

### `self-media-skill`

总入口 skill。

作用很简单：

- 用户要做抖音文案、短视频取材、热点检索时，转到 `social-copywriting-workflow`
- 用户要做小红书图文生成、配图、自动发布时，转到 `xiaohongshu-auto-publish`

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

推荐用 npm 作为安装入口，但 npm 只是安装通道，不是这个项目的主体。

### 1. 全局安装

```bash
npm install -g @zktlove/self-media-skill
```

### 2. 查看可识别的 Agent

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

## 安装机制

当前安装流程是：

1. 先从 GitHub 上拉取这个 skill 仓库的最新内容
2. 自动扫描仓库根目录和一级子目录中的 `SKILL.md`
3. 自动识别本机已经存在的 Agent
4. 先写入 canonical skill 目录
5. 再分发到各个 Agent 的 skill 目录
6. 优先使用 symlink，失败时回退为 copy

也就是说，安装器不是把 skill 路径写死到某个包内资源目录，而是固定安装规则、动态发现本机工具路径，再把这个 skill 仓库内容发过去。

## 使用建议

- 想改总入口分流逻辑，修改根目录 `SKILL.md`
- 想改抖音文案工作流，改 `social-copywriting-workflow/`
- 想改小红书自动发布工作流，改 `xiaohongshu-auto-publish/`
- npm 安装器代码已独立拆到另一个工程，不在这个仓库维护

## License

MIT
