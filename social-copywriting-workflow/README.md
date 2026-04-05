# Social Copywriting Workflow

这个目录现在分成两层：

1. Skill 本体
2. npm CLI 分发骨架

## Skill 本体

下面这些目录和文件，负责实际的 Skill 说明、记忆和资料组织：

- `SKILL.md`
- `memory.md`
- `01-account-positioning/`
- `02-asset-library/`
- `03-research/`
- `04-copywriting/`
- `scripts/`

本地直接使用时，核心入口仍然是：

- `SKILL.md`
- `scripts/README.md`

## npm CLI 分发骨架

参考 `larksuite/cli` 的做法，这里先固定成：

- `package.json`
- `npm/install.js`
- `npm/run.js`
- `npm/cli-manifest.json`

采用的思路是：

1. npm 包只负责分发入口和安装逻辑
2. CLI 真正运行时，优先走后续发布的独立运行时产物
3. `postinstall` 阶段负责准备运行时
4. `bin` 命令只做转发，不在入口脚本里堆业务逻辑

和 `larksuite/cli` 不同的地方只有一个：

- 由于当前目录里已经有 Python 的 `scripts/`，所以 npm 包装器改放在 `npm/`，避免和现有脚本目录冲突

## 当前状态

当前这套 npm CLI 还是骨架，不假装已经实现完整命令。

已经固定好的只有：

- 包结构
- 版本入口
- 安装入口
- 命令入口
- 后续下载配置位置

还没真正落地的部分：

- 发布到 GitHub Release 的平台产物
- 真正的命令实现
- 安装器里的远程下载
- 自动更新到具体运行时文件

## 后续怎么补全

要把这套骨架升级成可公开分发的 CLI，按这个顺序补：

1. 先确定仓库地址并替换 `package.json` 和 `npm/cli-manifest.json` 里的占位字段
2. 再确定最终 CLI 产物形式：
   - Node CLI
   - Python 打包产物
   - 独立二进制
3. 把每个版本的产物发布到 GitHub Release
4. 打开 `npm/install.js` 里的下载开关
5. 让 `npm/run.js` 直接转发到真实产物
6. 最后再发布 npm 包

## 未来安装与更新口径

等仓库和发布产物补齐后，外部用户就按下面方式使用：

```bash
npm install -g social-copywriting-workflow
social-copywriting doctor
```

更新时：

```bash
npm update -g social-copywriting-workflow
```
