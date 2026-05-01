---
name: yuan-social-cli
description: Use when the user needs atomic API calls for self-media and social platforms through the yuan-social CLI, including Douyin, Xiaohongshu, Bilibili, WeChat Channels, WeChat MP, TikTok, YouTube, Weibo, Zhihu, Instagram, Twitter/X, Reddit and other platform data queries, command discovery, schema lookup, dry-run validation, or stable agent-json output.
---

# Yuan Social CLI

这个 Skill 用于调用 `yuan-social-cli` 这个 npm 包。它适合做原子级 API 调用：查作品详情、下载地址、作者主页、评论、搜索结果、热榜、公众号文章、视频号内容等。

## 先判断是否要用

遇到下面这类需求，优先使用本 Skill：

- 用户要查某个平台的数据，而不是写文案或发布内容
- 用户要调用抖音、小红书、B站、微信视频号、微信公众号等接口
- 用户要看可用接口、命令列表、schema、请求参数
- 用户要用 CLI 调接口并保存 JSON
- 用户要让 Agent 稳定解析调用结果

如果用户要写文案，走 `social-copywriting-workflow`。如果用户要生成并发布小红书图文，走 `xiaohongshu-auto-publish`。

## 安装和更新

要求 Node.js 20 或更高版本。

```powershell
npm install -g yuan-social-cli
```

更新到最新版：

```powershell
npm update -g yuan-social-cli
```

查看已安装版本：

```powershell
npm list -g yuan-social-cli --depth=0
npm view yuan-social-cli version
```

命令入口：

```powershell
yuan-social --help
```

## 配置

保存 Yuan API 令牌和服务地址：

```powershell
yuan-social config set-token <你的令牌>
yuan-social config set-base-url https://open.yuanchuangai.com
yuan-social config show
```

也可以临时传参，不写入配置文件：

```powershell
yuan-social douyin video-detail "https://v.douyin.com/xxx/" --token <你的令牌>
```

或用环境变量：

```powershell
$env:YUAN_SOCIAL_TOKEN="<你的令牌>"
yuan-social douyin hot-search
```

## Agent 调用规则

给 AI Agent 使用时，先查命令和 schema，再调用接口。

```powershell
yuan-social commands list
yuan-social commands describe douyin.video-detail
yuan-social schema douyin.video-detail
```

业务调用建议加 `--format agent-json`，输出会固定成：

```json
{
  "success": true,
  "command": "douyin video-detail",
  "data": {},
  "warnings": [],
  "error": null,
  "meta": {}
}
```

失败时读取 `error.code` 和 `error.message`。常见错误码：

| 错误码 | 含义 |
| --- | --- |
| `TOKEN_MISSING` | 没有配置 Yuan API token |
| `BAD_ARGUMENT` | 参数或命令写错 |
| `AUTH_INVALID` | token 无效或权限不足 |
| `UPSTREAM_ERROR` | 上游平台或服务报错 |
| `NETWORK_ERROR` | 网络或超时错误 |
| `INTERNAL_ERROR` | 未分类错误 |

## 命令发现

这个 CLI 有两类命令：

- 高频快捷命令：更适合日常使用，例如 `douyin video-detail`
- 自动生成 endpoint 命令：覆盖完整接口，例如 `douyin app v3 fetch-multi-video-v2`

常用发现命令：

```powershell
yuan-social shortcuts
yuan-social shortcuts douyin
yuan-social list douyin
yuan-social commands list
yuan-social commands describe xiaohongshu.search-notes
yuan-social schema xiaohongshu.search-notes
```

当前 registry 覆盖的平台包括：

`bilibili`、`douyin`、`instagram`、`kuaishou`、`lemon8`、`linkedin`、`pipixia`、`reddit`、`threads`、`tiktok`、`toutiao`、`twitter`、`wechat`、`weibo`、`xiaohongshu`、`xigua`、`youtube`、`zhihu`。

## 通用透传调用

快捷命令没有覆盖到的接口，用 `call` 直接传 `/social` 后面的路径。

```powershell
yuan-social call /douyin/app/v3/fetch_multi_video_v2 --json "{\"url\":\"https://v.douyin.com/xxx/\"}"
```

如果要核对请求但不真正发起请求，用 `--dry-run`：

```powershell
yuan-social douyin user-posts sec_user_id --count 20 --dry-run
```

保存结果到文件：

```powershell
yuan-social bilibili video-detail "https://www.bilibili.com/video/BVxxx" -o bilibili-video.json
```

## 高频快捷命令

### 抖音

| 需求 | 命令 |
| --- | --- |
| 作品详情 | `yuan-social douyin video-detail "https://v.douyin.com/xxx/" --format agent-json` |
| 视频播放/下载地址 | `yuan-social douyin video-download "https://v.douyin.com/xxx/" --region CN --format agent-json` |
| 作者主页资料 | `yuan-social douyin user-profile <sec_user_id> --format agent-json` |
| 作者作品列表 | `yuan-social douyin user-posts <sec_user_id> --count 20 --cursor 0 --format agent-json` |
| 作品评论 | `yuan-social douyin comments <aweme_id> --count 20 --cursor 0 --format agent-json` |
| 抖音热榜 | `yuan-social douyin hot-search --format agent-json` |

### 小红书

| 需求 | 命令 |
| --- | --- |
| 笔记详情 | `yuan-social xiaohongshu note-detail <note_id> --xsec-token <xsec_token> --format agent-json` |
| 笔记评论 | `yuan-social xiaohongshu note-comments <note_id> --cursor <cursor> --format agent-json` |
| 搜索笔记 | `yuan-social xiaohongshu search-notes "关键词" --page 1 --sort general --note-type 0 --format agent-json` |
| 搜索用户 | `yuan-social xiaohongshu search-users "关键词" --page 1 --format agent-json` |
| 作者笔记 | `yuan-social xiaohongshu user-notes <user_id> --cursor <cursor> --format agent-json` |

### Bilibili

| 需求 | 命令 |
| --- | --- |
| 视频详情 | `yuan-social bilibili video-detail "https://www.bilibili.com/video/BVxxx" --format agent-json` |
| 视频播放信息 | `yuan-social bilibili video-download "https://www.bilibili.com/video/BVxxx" --format agent-json` |
| 按 BV 和 cid 获取视频流 | `yuan-social bilibili video-playurl <bv_id> <cid> --format agent-json` |
| UP 主资料 | `yuan-social bilibili user-profile <uid> --format agent-json` |
| UP 主投稿 | `yuan-social bilibili user-posts <uid> --page 1 --order pubdate --format agent-json` |
| 综合搜索 | `yuan-social bilibili search "关键词" --page 1 --page-size 20 --order totalrank --format agent-json` |
| 视频评论 | `yuan-social bilibili comments <bv_id> --page 1 --format agent-json` |

### 微信视频号

| 需求 | 命令 |
| --- | --- |
| 综合搜索 | `yuan-social wechat channels-search "关键词" --format agent-json` |
| 最新视频搜索 | `yuan-social wechat channels-latest "关键词" --format agent-json` |
| 用户搜索 | `yuan-social wechat channels-user-search "关键词" --page 1 --format agent-json` |
| 视频详情 | `yuan-social wechat channels-video-detail <id> --export-id <exportId> --format agent-json` |
| 主页采集 | `yuan-social wechat channels-home --json "{...}" --format agent-json` |

### 微信公众号

| 需求 | 命令 |
| --- | --- |
| 文章详情 JSON | `yuan-social wechat mp-article-detail "https://mp.weixin.qq.com/s/xxx" --format agent-json` |
| 文章 HTML | `yuan-social wechat mp-article-html "https://mp.weixin.qq.com/s/xxx" --format agent-json` |
| 文章列表 | `yuan-social wechat mp-article-list <ghid> --offset 0 --format agent-json` |
| 文章评论 | `yuan-social wechat mp-comments "https://mp.weixin.qq.com/s/xxx" --comment-id <comment_id> --buffer <buffer> --format agent-json` |

## 使用习惯

- 不确定命令时，先执行 `yuan-social shortcuts <platform>`。
- 不确定参数时，执行 `yuan-social schema <command-key>`。
- 不确定完整接口名时，执行 `yuan-social list <platform>`。
- 调真实接口前，先用 `--dry-run` 核对 URL、method、headers 和 body。
- Agent 自动处理结果时，统一加 `--format agent-json`。
- 不要把 token 写进文档、日志或最终回复。
