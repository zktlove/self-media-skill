# MCP Tools Reference

这个文件只讲这个 skill 会调用到的 MCP 工具，不重复写实现代码。

## 1. 对标内容采集 MCP

工具名：`collect_xiaohongshu_keyword_notes(keyword)`

### 输入

- `keyword`
  - 类型：字符串
  - 含义：要搜索的小红书关键词

### 固定行为

- 按点赞数从高到低筛选
- 只采集图文普通笔记
- 不够 3 篇自动翻页
- 最多翻 5 页

### 返回重点

- `keyword`
- `count`
- `markdown_path`
- `notes`

### `notes` 中每篇内容至少包含

- `title`
- `content`
- `topics`
- `link`

## 2. 小红书配图 MCP

工具名：`generate_xiaohongshu_images(copy_text, prompt_framework_text, image_count)`

### 输入

- `copy_text`
  - 类型：字符串
  - 含义：当前这次要发布的小红书标题和正文整理结果
- `prompt_framework_text`
  - 类型：字符串
  - 含义：风格框架文本，只保留固定风格骨架
- `image_count`
  - 类型：整数
  - 默认：`3`

### 固定行为

- 模型固定：`doubao-seedream-5-0-260128`
- 输出格式固定：PNG
- 默认生成 3 张竖版图片
- 三张图自动做差异化构图
- 不允许把历史示例主题混进最终 prompt

### 返回重点

- `count`
- `model`
- `prompts`
- `images`

### `images` 中每张内容至少包含

- `index`
- `path`
- `size`
- `prompt`
- `model`

## 使用提醒

1. skill 里只调用工具，不内嵌 MCP 实现代码。
2. skill 里如果要使用提示词框架，优先读取本目录下的 `小红书配图提示词框架.txt`。
3. 如果用户只给了主题，没有给完整文案，先补全标题和正文，再调用生图工具。
4. 正式完整入口是 `runtime/run_full_workflow.py`，它会顺序调用：
   - `collect_xiaohongshu_keyword_notes`
   - `build_publish_payload`
   - `generate_xiaohongshu_images`
   - `publish_note_with_storage_state.js`
5. 发布脚本读取 JSON 时必须去掉 BOM，否则 Node 直接 `JSON.parse` 会报错。
