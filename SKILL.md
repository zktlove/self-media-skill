---
name: self-media-skill
description: Use when the user asks about self-media workflows across Chinese and global platforms, including copywriting, topic research, platform data queries, atomic API calls, content collection, Xiaohongshu publishing, Douyin/Bilibili/WeChat/Xiaohongshu operations, or choosing the right self-media sub-skill.
---

# Self Media Skill

这个目录是自媒体能力总入口，只负责分流和索引，不重复维护子 Skill 的内部规则。

## 当前发布范围

当前 npm 包只发布以下内容：

- 根目录这一份 `SKILL.md`
- `social-copywriting-workflow/`
- `xiaohongshu-auto-publish/`
- `yuan-social-cli/`

## 分流规则

### 1. 走 `social-copywriting-workflow`

遇到下面这些需求，直接进入这个子 Skill：

- 对标视频仿写
- 给主题或想法生成抖音/小红书/视频号文案
- 抖音搜索
- 抖音主页抓取
- 视频解析下载
- 音频抽取
- 音频转文字
- 热榜查询

适合的典型输入：

- 对标视频 URL
- 用户主页 URL
- 搜索关键词
- 文案结构
- 主题、想法、方向

子 Skill 名称：

- `social-copywriting-workflow`

### 2. 走 `xiaohongshu-auto-publish`

遇到下面这些需求，直接进入这个子 Skill：

- 搜集小红书对标内容
- 生成小红书标题和正文
- 生成配图
- 浏览器自动上传并发布小红书内容

子 Skill 名称：

- `xiaohongshu-auto-publish`

### 3. 走 `yuan-social-cli`

遇到下面这些需求，直接进入这个子 Skill：

- 调用自媒体平台原子级 API
- 查询接口列表、命令列表、schema、帮助命令
- 获取抖音、小红书、B站、微信视频号、微信公众号等平台数据
- 查询作品详情、作者主页、评论、搜索结果、热榜、文章详情
- 使用 `yuan-social-cli`、`yuan-social` 或 `yuan-social-cli` npm 包
- 需要稳定 JSON 输出给 Agent 继续处理

适合的典型输入：

- 平台名和数据查询目标
- 作品 URL、笔记 ID、BV 号、公众号文章 URL
- API 路径或 endpoint 名称
- “查一下有哪些接口可以用”
- “帮我用 CLI 调这个接口”

子 Skill 名称：

- `yuan-social-cli`

## 多需求时怎么处理

如果用户一次提了多段流程，不要强行塞进一个子 Skill，按阶段拆开：

1. 先判断目标平台
2. 再判断当前处于数据查询、取材、写作还是发布阶段
3. 把每一段交给对应的子 Skill

例如：

- “先抓抖音对标，再写文案”：
  走 `social-copywriting-workflow`
- “先找小红书对标，再生成图文并发布”：
  走 `xiaohongshu-auto-publish`
- “查抖音作品详情、评论、热榜，或者列出可用 API”：
  走 `yuan-social-cli`

## 维护规则

- 这个总 Skill 只维护分流逻辑
- 子 Skill 内部内容保持各自独立
- 子 Skill 自己升级时，只改子 Skill 目录
- 总 Skill 不复制子 Skill 的脚本细节
- 只要子 Skill 名称保持不变，这个总入口就可以继续工作
