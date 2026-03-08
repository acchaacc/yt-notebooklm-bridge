---
name: yt-notebooklm-bridge
description: >
  NotebookLM 源制作工具。从 YouTube 频道提取所有视频地址，
  以空格分隔存储为 MD 文件，方便用户导入 NotebookLM 作为源文件。
  使用场景：当用户需要将 YouTube 频道内容批量导入 NotebookLM 时。
  关键词：NotebookLM、YouTube、源文件、source、频道提取、channel extract、做成源、制作源
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
model: claude-sonnet-4-5-20250514
---

# NotebookLM 源制作工具

> **Installation**: If you're installing this skill from GitHub, please refer to [README.md](README.md#installation) for installation instructions.

## 触发条件

当用户提到以下内容时触发此技能：

- "把 XX 频道做成源" / "把这个频道做成 NotebookLM 源"
- "提取 XX 频道的视频" / "提取频道视频地址"
- "XX 频道做成 NotebookLM 源文件"
- "帮我把这个 YouTube 频道导入 NotebookLM"
- "制作 NotebookLM 源" / "生成源文件"
- 分享 YouTube 频道链接并提到"源"、"NotebookLM"、"提取"
- "extract channel videos for NotebookLM"

## 功能说明

从 YouTube 频道提取所有视频 URL，以空格分隔存储为 Markdown 文件，用户可直接将该文件内容复制粘贴到 Google NotebookLM 的 YouTube 源导入中。

## 工作流程

你将按照以下 3 个阶段执行任务：

### 阶段 1: 环境检测

**目标**: 确保 yt-dlp 已安装

```bash
yt-dlp --version
```

**如果未安装**:
- macOS: `brew install yt-dlp`
- pip: `pip install yt-dlp`

---

### 阶段 2: 提取视频 URL

**目标**: 从 YouTube 频道提取所有视频地址

1. 询问用户提供 YouTube 频道 URL
   - 支持格式: `https://www.youtube.com/@ChannelName`
   - 支持格式: `https://www.youtube.com/channel/UCXXXXXX`
   - 支持格式: `https://www.youtube.com/c/ChannelName`

2. 询问用户是否限制提取数量（可选）

3. 执行提取脚本
   ```bash
   cd ~/.claude/skills/yt-notebooklm-bridge
   python3 scripts/extract_channel_urls.py "<channel_url>"
   ```

4. 如需限制数量：
   ```bash
   python3 scripts/extract_channel_urls.py "<channel_url>" --max-videos 50
   ```

5. 自定义输出路径：
   ```bash
   python3 scripts/extract_channel_urls.py "<channel_url>" --output ~/Desktop/my_channel.md
   ```

**注意**: 频道视频较多时提取可能需要几分钟，请耐心等待。

---

### 阶段 3: 输出结果

**目标**: 确认文件已生成并指导用户导入 NotebookLM

1. 确认文件保存位置（默认: `~/Desktop/<频道名>_notebooklm.md`）

2. 向用户展示结果：
   ```
   NotebookLM 源文件已生成！

   文件路径: ~/Desktop/<频道名>_notebooklm.md
   视频数量: X 个
   文件格式: URL 以空格分隔

   导入 NotebookLM 步骤:
   1. 打开桌面上生成的 .md 文件
   2. 复制文件中的视频 URL
   3. 打开 https://notebooklm.google.com
   4. 创建新笔记本或打开现有笔记本
   5. 点击 "Add source"（添加源）
   6. 选择 "YouTube"
   7. 将复制的 YouTube 视频 URL 粘贴到输入框中
   8. 逐条添加或批量添加视频链接

   注意: NotebookLM 的 YouTube 源导入是通过 YouTube 链接输入，
   每次粘贴一个视频 URL 进行添加。
   ```

3. 提醒用户从 .md 文件中复制 URL，再逐条粘贴到 NotebookLM 的 YouTube 视频导入中

---

## 输出文件格式

文件内容为所有视频 URL 以空格分隔的纯文本：

```
https://www.youtube.com/watch?v=VIDEO_ID_1 https://www.youtube.com/watch?v=VIDEO_ID_2 https://www.youtube.com/watch?v=VIDEO_ID_3 ...
```

文件扩展名为 `.md`，方便在 NotebookLM 中作为文本源导入。

---

## 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `channel_url` | YouTube 频道 URL（必须） | - |
| `--max-videos` | 最大提取数量 | 全部 |
| `--output` | 输出文件路径 | `~/Desktop/<频道名>_notebooklm.md` |

---

## 错误处理

| 问题 | 解决方案 |
|------|----------|
| yt-dlp 未安装 | `brew install yt-dlp` 或 `pip install yt-dlp` |
| 无效频道 URL | 检查 URL 格式，确保是频道页面而非单个视频 |
| 提取超时 | 使用 `--max-videos` 限制数量 |
| 无视频提取 | 确认频道有公开视频 |

---

## 开始执行

当用户触发这个 Skill 时：
1. 检测 yt-dlp 环境
2. 获取频道 URL
3. 提取所有视频地址
4. 保存为 MD 文件到桌面
5. 指导用户导入 NotebookLM
