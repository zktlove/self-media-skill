---
name: xiaohongshu-auto-publish
description: Use when building or running a complete Xiaohongshu auto-publishing workflow that must sequentially collect hot topics, generate copy, generate images, and upload the final post through browser automation.
---

# Xiaohongshu Auto Publish

## Overview

这个 skill 用来连续完成一条完整的小红书自动发布流程，不做分支，不做跳步，固定按以下四步执行：

1. 根据输入关键词，搜集小红书行业优秀对标作品
2. 生成小红书选题、标题和正文
3. 生成小红书配图并产出图片文件
4. 上传图文到小红书并发布

## Resource Loading

- 需要查看完整四步执行口径时，读取 `references/workflow.md`
- 需要确认 MCP 工具入参、返回值和默认规则时，读取 `references/mcp-tools.md`
- 需要执行第二步文案生成时，读取 `references/copywriting.md`
- 需要生成配图提示词框架时，读取 `references/小红书配图提示词框架.txt`
- 需要直接运行正式工作流时，执行 `runtime/run_full_workflow.py`
- 需要单独执行最后一步发布时，使用 `runtime/publish_note_with_storage_state.js`

## Execution Rules

- 必须严格按顺序执行四个步骤
- 上一步没有完成，不能进入下一步
- 任一步失败，立即停止并返回失败原因
- 不自行增删步骤
- 不自行改成别的平台发布
- 正式脚本写出的 JSON、Markdown、TXT 一律使用 UTF-8 无 BOM，避免 Node 和终端解析出错
- 正式发布脚本允许处理平台把关键词映射成近义正式话题，例如 `副业赚钱 -> 副业赚钱新途径`

## Step 1: 搜集小红书行业优秀对标作品

目标：
根据输入的关键词，收集当前可用于小红书创作的行业优秀对标作品和参考素材。

执行：
- 按 `references/workflow.md` 中的第一步顺序执行
- 工具调用和返回值定义以 `references/mcp-tools.md` 为准

运行这个 skill 前，至少准备以下输入：

- `benchmark_keyword`：用于搜集对标内容的小红书关键词
- `account_positioning`：账号定位
- `target_audience`：目标人群
- `content_direction`：内容方向，如 AI 工具、创业干货、效率提升
- `tone_style`：语气风格，如口语化、干货型、亲切型
- `publish_mode`：`draft` 或 `publish`
- `hot_source_config`：热点来源配置
- `image_style`：配图风格要求
- `max_topics`：候选选题数量，默认 3
- `title_count`：候选标题数量，默认 3

产出：
- 数据最优图文帖子列表(三条收集内容）
- 每条图文帖子的标题、正文、话题、链接
- MCP 生成的 Markdown 文件路径

## Step 2: 生成小红书选题、标题和正文

目标：
基于第一步搜集到的热点内容，生成符合小红书风格的选题、标题和正文。

执行：
- 读取第一步产出的 3 篇对标内容和 Markdown 汇总结果
- 按 `references/copywriting.md` 中的规则生成标题、正文和后续可复用的 `copy_text`
- 生成对应标题
- 生成对应正文

产出：
- 选题
- 标题
- 正文

## Step 3: 生成小红书配图

目标：
基于第二步产出的标题和正文，生成小红书风格图片，并拿到可上传的图片文件。

执行：
- 将第二步生成的标题和正文整理为 `copy_text`
- 从 `references/小红书配图提示词框架.txt` 读取风格骨架，整理为 `prompt_framework_text`
- `prompt_framework_text` 只保留风格骨架，不写死题材示例；具体主题、主体、动作全部由当前 `copy_text` 决定
- 按 `references/workflow.md` 中的第三步顺序执行
- 工具调用和返回值定义以 `references/mcp-tools.md` 为准
- 生成配图
- 返回最终图片文件路径或图片资源结果

产出：
- 最终用于生图的 3 条图片提示词
- 生成后的图片文件

## Step 4: 上传到小红书并发布

目标：
将第二步生成的标题和正文，以及第三步生成的图片，自动上传到小红书并完成发布。

执行：
- 调用 `playwright-skill`、`playwright-mcp`
- 打开小红书发布页面
- 上传图片
- 填写标题
- 填写正文
- 用 DOM Selection API 先把正文编辑器光标准确放到正文末尾
- 每次输入 `#话题关键词` 后，等待平台弹出话题建议列表，默认点击第一条建议项，不能只靠空格提交
- 话题插入完成后，建议由执行中的 AI 再检查一次编辑器结果，确认已经是平台识别的正式话题格式，而不是普通 `#文本`
- 这个检查属于 skill 执行说明，用于提升稳定性，不要求 MCP 层强制兜底
- 三个话题都选中后，再根据 `publish_mode` 执行发布或停在发布前
- 调用发布相关 MCP 完成发布动作
- 返回发布结果

涉及能力：
- Skill：`playwright-skill`
- MCP：`playwright-mcp`

产出：
- 发布结果
- 发布状态
- 作品链接或发布记录

## Final Output

执行完成后，统一返回以下结果并保存到程序目录：

- 收集内容结果
- 对标内容 Markdown 路径
- 最终标题
- 最终正文
- 最终图片
- 小红书发布结果

## Official Runtime Entry

- 完整工作流正式入口：
  `python runtime/run_full_workflow.py --keyword "AI副业" --publish-mode stop_before_publish`
- 直接发布：
  `python runtime/run_full_workflow.py --keyword "AI副业" --publish-mode publish`
- 单独跑最后一步时，由 `runtime/publish_note_with_storage_state.js` 读取 payload JSON、storage state 和图片路径执行上传/发布
