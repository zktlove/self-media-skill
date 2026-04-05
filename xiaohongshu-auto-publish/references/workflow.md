# Xiaohongshu Auto Publish Workflow

这个文件专门给 skill 读完整流程，避免把所有细节都堆进 `SKILL.md`。

## 固定执行顺序

1. 收集对标内容
2. 生成选题、标题和正文
3. 生成配图
4. 上传并发布

任一步失败就停止，不能跳步，也不能换平台。

## 第一步：收集对标内容

- 输入：`benchmark_keyword`
- 调用工具：`collect_xiaohongshu_keyword_notes(keyword)`
- 固定规则：
  - 只采集图文笔记
  - 只采集“普通笔记”
  - 按点赞数从高到低
  - 默认 `page=1`
  - 默认 `time_filter=不限`
  - 默认 `source=explore_feed`
  - 默认 `ai_mode=0`
  - 不够 3 篇就自动翻页
  - 最多翻 5 页
- 产出：
  - 3 篇对标内容
  - 每篇包含：标题、正文、话题、链接
  - 1 个 Markdown 汇总文件
  - 正式脚本里由 `mcp/xiaohongshu_keyword_mcp/service.py` 执行

## 第二步：生成标题和正文

- 输入：
  - 第一步产出的 3 篇对标内容
  - 账号定位
  - 目标人群
  - 内容方向
  - 语气风格
- 目标：
  - 生成 1 组可直接发布的小红书图文文案
- 产出：
  - 最终标题
  - 最终正文
  - 正式脚本里由 `mcp/xiaohongshu_keyword_mcp/publish_payload_service.py` 执行

## 第三步：生成配图

- 输入：
  - `copy_text`
  - `prompt_framework_text`
  - `image_count`
- `copy_text` 由标题和正文组成
- `prompt_framework_text` 只允许使用风格骨架，不能把示例主题写死
- 调用工具：`generate_xiaohongshu_images(copy_text, prompt_framework_text, image_count)`
- 固定规则：
  - 模型固定：`doubao-seedream-5-0-260128`
  - 输出格式固定：PNG
  - 默认输出 3 张
  - 三张图定位分别是：封面主视觉、信息拆解图、氛围场景图
- 产出：
  - 3 条最终生图 prompt
  - 3 张图片文件
  - 正式脚本里由 `mcp/xiaohongshu_keyword_mcp/image_service.py` 执行

## 第四步：上传并发布

- 输入：
  - 第二步的标题
  - 第二步的正文
  - 第三步生成的图片
- 操作方式：
  - 通过浏览器自动化进入小红书发布页
  - 上传图片
  - 填写标题和正文
  - 用 DOM Selection API 把正文编辑器光标准确放到正文末尾
  - 每次输入 `#话题关键词` 后，等平台自动弹出话题列表，默认点击第一条建议项
  - 三个话题都处理完后，再进入发布或草稿分支
  - 完成发布或保存草稿
  - 正式脚本先走键盘选中话题建议，再兜底用 DOM click，最后校验是否变成 `.tiptap-topic`
  - `publish-mode=stop_before_publish/preview` 时停在发布前
  - `publish-mode=publish` 时直接点击发布并记录结果
- 产出：
  - 发布状态
  - 发布结果
  - 发布链接或记录
