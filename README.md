# 🎬 YT NotebookLM Bridge

> 一键提取 YouTube 频道全部视频地址，生成可直接导入 NotebookLM 的源文件。

基于 [Agent Skills](https://agentskills.io/) 开放规范构建的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能 — 可命令行独立运行，也可作为 AI Agent 技能直接调用。

## ✨ 功能特性

- 🔗 **频道全量提取** — 自动获取 YouTube 频道内所有视频 URL
- 📄 **MD 格式输出** — URL 以空格分隔存储为 `.md` 文件，方便复制粘贴
- 📝 **智能命名** — 自动识别频道名称作为文件名
- 🎯 **NotebookLM 适配** — 输出格式专为 NotebookLM YouTube 源导入优化
- ⚡ **数量控制** — 支持 `--max-videos` 限制提取数量
- 📂 **自定义路径** — 支持 `--output` 指定输出位置

## 📋 环境要求

- [Python 3.8+](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)（`brew install yt-dlp` 或 `pip install yt-dlp`）

## 🚀 快速开始

### 提取频道全部视频

```bash
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName"
```

### 限制提取数量

```bash
# 只提取最近 50 个视频
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName" --max-videos 50
```

### 指定输出路径

```bash
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName" --output ~/Desktop/my_channel.md
```

## 📖 CLI 选项

| 选项 | 说明 |
|------|------|
| `<channel_url>` | YouTube 频道 URL（必须） |
| `--max-videos <数量>` | 🔢 最大提取视频数（默认：全部） |
| `--output <路径>` | 📂 输出文件路径（默认：`~/Desktop/<频道名>_notebooklm.md`） |

## 🔗 支持的 URL 格式

| 格式 | 示例 |
|------|------|
| Handle | `https://www.youtube.com/@ChannelName` |
| Channel ID | `https://www.youtube.com/channel/UCXXXXXXX` |
| 自定义 URL | `https://www.youtube.com/c/ChannelName` |

## 📂 输出格式

所有视频 URL 以空格分隔存储在 `.md` 文件中：

```
https://www.youtube.com/watch?v=VIDEO_1 https://www.youtube.com/watch?v=VIDEO_2 https://www.youtube.com/watch?v=VIDEO_3 ...
```

## 📥 导入 NotebookLM

1. 打开桌面上生成的 `.md` 文件
2. 复制文件中的视频 URL
3. 打开 [notebooklm.google.com](https://notebooklm.google.com)
4. 创建新笔记本或打开现有笔记本
5. 点击 **"Add source"**（添加源）
6. 选择 **"YouTube"**
7. 将复制的 YouTube 视频 URL 粘贴到输入框中
8. 逐条添加视频链接

> **提示**：NotebookLM 的 YouTube 源导入为逐条粘贴，`.md` 文件作为 URL 汇总方便快速复制。

## 🤖 Claude Code 技能

### 安装

```bash
# 克隆到技能目录
git clone https://github.com/acchaacc/yt-notebooklm-bridge ~/.claude/skills/yt-notebooklm-bridge
```

### 触发关键词

安装后，在 Claude Code 中直接说：

- 💬 "把这个频道做成源：https://www.youtube.com/@ChannelName"
- 💬 "把 XX 频道做成 NotebookLM 源"
- 💬 "帮我把这个 YouTube 频道导入 NotebookLM"
- 💬 "提取 XX 频道的所有视频地址"
- 💬 "制作 NotebookLM 源文件"
- 💬 "获取频道最近 50 个视频用于 NotebookLM"

## 🔧 工作原理

```
频道 URL → 🔍 yt-dlp 提取全部视频 URL → 📄 空格分隔写入 .md 文件 → 📥 用户复制粘贴到 NotebookLM
```

### 项目结构

```
~/.claude/skills/yt-notebooklm-bridge/
  📄 SKILL.md                          ← Claude Code 技能指令
  📄 README.md                         ← 本文件
  📁 scripts/
      🐍 extract_channel_urls.py       ← URL 提取脚本
```

## ❓ 常见问题

**提取需要多长时间？**
取决于频道大小，大部分频道（< 500 个视频）在 1-2 分钟内完成。

**有提取数量限制吗？**
工具本身无限制，使用 `--max-videos` 可自行控制数量。

**支持播放列表吗？**
本技能为频道设计，但 yt-dlp 也支持播放列表 URL，直接传入即可。

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| yt-dlp 未找到 | `brew install yt-dlp` 或 `pip install yt-dlp` |
| 未提取到视频 | 检查 URL 是频道页面而非单个视频 |
| 提取超时 | 使用 `--max-videos` 限制数量 |
| 权限被拒绝 | 检查桌面文件写入权限 |

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)。
