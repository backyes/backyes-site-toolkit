# Post 创建与更新指南

## 目录结构

```
backyes-site-toolkit/
├── backyes.github.io/            # Pages 仓库
│   ├── index.html                # 首页 (Hero + Survey + Posts + Tags)
│   ├── posts.html                # 博客列表页
│   ├── tags.html                 # 标签页
│   ├── assets/css/main.css       # 共享设计系统
│   ├── posts/                    # 手写文章
│   │   ├── 2026-07-21-kimi3-architecture-analysis.md
│   │   ├── 2026-07-21-kimi3-architecture-analysis.html  (自动生成)
│   │   └── assets/               # 文章图片/数据
│   └── [报告目录]/               # AI 调研报告
├── scripts/
│   ├── sync_reports.sh           # 同步 AI 报告
│   └── build_site.py             # 构建全部页面
├── posts/                        # 手写文章源 (可放在工作区根目录)
│   └── YYYY-MM-DD-title.md
└── CLAUDE.md                     # 项目经验
```

---

## 一、创建手写文章(Posts)

### 1.1 文件格式

在 `posts/` 目录下创建 `YYYY-MM-DD-title.md`:

```markdown
---
title: "文章标题"
date: 2026-07-21
tags: ["tag1", "tag2", "tag3"]
excerpt: "一句话摘要,显示在卡片和列表页"
---

# 文章标题

正文内容...
```

### 1.2 Frontmatter 字段

| 字段 | 必需 | 说明 |
|---|---|---|
| `title` | ✅ | 文章标题 |
| `date` | ✅ | 发布日期 (YYYY-MM-DD) |
| `tags` | ✅ | 标签列表 |
| `excerpt` | ✅ | 摘要(显示在卡片预览) |

### 1.3 支持的 Markdown 语法

| 语法 | 效果 |
|---|---|
| `==text==` | 渐变下划线高亮(关键结论) |
| `**text**` | 加粗 |
| `$number$` | 蓝色数字高亮 |
| ` ```code``` ` | 代码块 |
| `\| table \|` | 表格 |
| `> quote` | 引用块 |
| `[text](url)` | 链接 |
| `![alt](path)` | 图片 |

### 1.4 文章生成流程

```bash
# 1. 创建 markdown 源文件
vim posts/2026-07-22-my-new-post.md

# 2. 构建页面 (生成 HTML + 更新 posts.html + index.html)
python3 scripts/build_site.py

# 3. 推送
cd backyes.github.io && git add -A && git commit -m "add post: ..." && git push
```

---

## 二、创建 AI 调研报告(Survey by AI)

### 2.1 在工作区创建报告

```
workspace/
├── vllm_research/vllm_analysis/
│   ├── index.html          ← 报告入口
│   ├── report.html         ← 主报告
│   └── assets/             ← 图片/数据
```

### 2.2 注册到 build_site.py

编辑 `scripts/build_site.py` 的 `REPORTS` 数组,**第一个元素是最新报告**:

```python
REPORTS = [
    {"dst":"umdk","entry":"analysis/cam/CAM深度分析报告.html","visual":"UMDK",
     "title":"UMDK/CAM 深度分析",
     "desc":"Communication Acceleration for Matrix 架构深度分析 ...",
     "cat":"chip","priority":"p0",
     "tags":["UMDK","CAM","通信加速","矩阵计算"]},
    # ... 其他报告
]
```

### 2.3 注册到 sync_reports.sh

编辑 `scripts/sync_reports.sh` 的 `PROJECTS` 数组:

```bash
PROJECTS=(
  "umdk_research|umdk|analysis/cam/CAM深度分析报告.html|🔬|UMDK/CAM 深度分析|...|chip|p0"
  # ... 其他报告
)
```

### 2.4 字段说明

| 字段 | 说明 |
|---|---|
| `dst` | 仓库内目录名(URL 路径) |
| `entry` | 入口 HTML 文件名 |
| `visual` | 卡片上的大字标题 |
| `title` | 卡片标题 |
| `desc` | 卡片描述 |
| `cat` | 分类(inference/model/network/chip/storage/recsys/conference/space) |
| `priority` | p0=旗舰, p1=常规, p2=轻量 |
| `tags` | 标签列表 |

### 2.5 同步流程

```bash
# 预览
./scripts/sync_reports.sh --dry-run

# 同步 + 构建 + 推送
./scripts/sync_reports.sh

# 只同步特定项目
./scripts/sync_reports.sh umdk
```

---

## 三、更新已有文章/报告

### 3.1 更新手写文章

1. 编辑 `posts/YYYY-MM-DD-title.md`
2. 运行 `python3 scripts/build_site.py`
3. 推送

### 3.2 更新 AI 调研报告

1. 更新工作区源文件(如 `vllm_research/vllm_analysis/index.html`)
2. 运行 `./scripts/sync_reports.sh`
3. 推送

---

## 四、分类体系

| 分类 | 标签 | 颜色 |
|---|---|---|
| 推理引擎 | inference | 蓝色 |
| 模型架构 | model | 紫色 |
| 网络拓扑 | network | 绿色 |
| 芯片架构 | chip | 琥珀色 |
| 存储系统 | storage | — |
| 推荐系统 | recsys | — |
| 学术会议 | conference | — |
| 太空经济 | space | — |
| 交叉领域 | mixed | 粉色 |

---

## 五、完整工作流示例

### 场景:创建一篇新博客

```bash
cd ~/work/claude_workspace

# 1. 写文章
cat > posts/2026-07-22-my-insight.md << 'EOF'
---
title: "My Insight on AI Infrastructure"
date: 2026-07-22
tags: ["insight", "ai-infra"]
excerpt: "A brief summary of my thoughts..."
---

# My Insight

==Key conclusion== with data...

| Metric | Value |
|---|---|
| A | 100 |
| B | 200 |
EOF

# 2. 构建
python3 backyes-site-toolkit/scripts/build_site.py

# 3. 推送
cd backyes-site-toolkit/backyes.github.io
git add -A && git commit -m "add post: My Insight" && git push origin main
```

### 场景:添加一份新调研报告

```bash
cd ~/work/claude_workspace

# 1. 在工作区准备报告(假设已完成)
# my_research/report.html 已存在

# 2. 注册到 build_site.py 和 sync_reports.sh
# (编辑 REPORTS / PROJECTS 数组)

# 3. 同步 + 构建 + 推送
./backyes-site-toolkit/scripts/sync_reports.sh
```

---

## 六、注意事项

1. **build_site.py 和 sync_reports.sh 必须同步**: 两个数组的 `dst`/`entry`/`title`/`desc` 必须一致
2. **图片放在 `posts/assets/` 或报告目录下**: 不要用绝对路径
3. **推送前先 `--dry-run`**: 确认变更符合预期
4. **GitHub Pages 有 1-3 分钟延迟**: 推送后不会立即生效
