# NotebookLM Bridge

> 多平台内容一键制作 NotebookLM 源文件 — 支持 YouTube 频道 + Apple Podcasts 播客。

基于 [Agent Skills](https://agentskills.io/) 开放规范构建的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能 — 可命令行独立运行，也可作为 AI Agent 技能直接调用。

## 功能特性

**YouTube 频道**
- 自动提取频道内所有视频 URL，空格分隔存储为 `.md` 文件
- 支持 `--filter` 按关键词筛选视频标题
- 支持 `--max-videos` 限制提取数量

**Apple Podcasts 播客**
- 从 Apple Podcasts URL 或 RSS 源自动提取全部节目
- 支持 `--filter` 按关键词筛选节目标题和描述
- 直接下载音频文件，可上传到 NotebookLM 作为音频源
- 零外部依赖（仅需 Python 标准库）

## 环境要求

- [Python 3.8+](https://www.python.org/)
- YouTube 模式需要 [yt-dlp](https://github.com/yt-dlp/yt-dlp)（`brew install yt-dlp` 或 `pip install yt-dlp`）
- 播客模式无额外依赖

## 快速开始

### YouTube 频道

```bash
# 提取全部视频
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName"

# 按关键词筛选
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName" --filter "AI,科技"

# 限制数量
python3 scripts/extract_channel_urls.py "https://www.youtube.com/@ChannelName" --max-videos 50
```

### Apple Podcasts

```bash
# 列出全部节目
python3 scripts/extract_podcast_episodes.py "https://podcasts.apple.com/us/podcast/xxx/id123456" --list

# 按关键词筛选并列出
python3 scripts/extract_podcast_episodes.py "https://podcasts.apple.com/us/podcast/xxx/id123456" --filter "地缘,战争,中东" --list

# 下载筛选后的节目
python3 scripts/extract_podcast_episodes.py "https://podcasts.apple.com/us/podcast/xxx/id123456" --filter "地缘,战争" --max-episodes 10

# 也支持直接 RSS 源 URL
python3 scripts/extract_podcast_episodes.py "https://feed.example.com/podcast.xml"
```

## CLI 选项

### YouTube (`extract_channel_urls.py`)

| 选项 | 说明 |
|------|------|
| `<channel_url>` | YouTube 频道 URL（必须） |
| `--max-videos <数量>` | 最大提取视频数（默认：全部） |
| `--filter <关键词>` | 逗号分隔的关键词，按视频标题筛选 |
| `--output <路径>` | 输出文件路径（默认：`~/Desktop/<频道名>_notebooklm.md`） |

### Apple Podcasts (`extract_podcast_episodes.py`)

| 选项 | 说明 |
|------|------|
| `<podcast_url>` | Apple Podcasts URL 或 RSS 源 URL（必须） |
| `--filter <关键词>` | 逗号分隔的关键词，按标题和描述筛选 |
| `--max-episodes <数量>` | 最大下载节目数（默认：全部） |
| `--list` | 仅列出匹配节目，不下载 |
| `--output <目录>` | 输出目录（默认：`~/Desktop/<播客名>/`） |

## 导入 NotebookLM

**YouTube 视频**
1. 打开桌面上生成的 `.md` 文件
2. 复制视频 URL
3. 打开 [notebooklm.google.com](https://notebooklm.google.com) → **Add source** → **YouTube**
4. 逐条粘贴视频 URL

**播客音频**
1. 打开 [notebooklm.google.com](https://notebooklm.google.com) → **Add source** → 选择音频文件
2. 从桌面文件夹上传下载的音频文件
3. 限制：单文件最大 200MB，每个笔记本最多 50 个源

## Claude Code 技能

### 安装

```bash
git clone https://github.com/acchaacc/notebooklm-bridge ~/.claude/skills/notebooklm-bridge
```

### 触发关键词

安装后，在 Claude Code 中直接说：

- "把这个频道做成源：https://www.youtube.com/@ChannelName"
- "把 XX 播客做成 NotebookLM 源"
- "下载这个播客的节目：https://podcasts.apple.com/..."
- "提取 XX 频道关于 AI 的视频"
- "制作 NotebookLM 源文件"

## 项目结构

```
~/.claude/skills/notebooklm-bridge/
  SKILL.md                                ← Claude Code 技能指令
  README.md                               ← 本文件
  scripts/
    extract_channel_urls.py               ← YouTube URL 提取
    extract_podcast_episodes.py           ← 播客节目下载
```

## 常见问题

**播客下载需要多长时间？**
取决于节目数量和网络速度，单集通常 30-60 秒。

**支持哪些播客平台？**
支持 Apple Podcasts URL 和任何标准 RSS 源 URL。

**音频文件太大怎么办？**
NotebookLM 限制单文件 200MB，超出时脚本会发出警告。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| yt-dlp 未找到 | `brew install yt-dlp` 或 `pip install yt-dlp` |
| 未提取到视频 | 检查 URL 是频道页面而非单个视频 |
| 播客 RSS 获取失败 | 尝试直接使用 RSS 源 URL |
| 音频下载超时 | 检查网络连接，重新运行（已下载的文件会自动跳过） |

## License

MIT License - 详见 [LICENSE](LICENSE)。
