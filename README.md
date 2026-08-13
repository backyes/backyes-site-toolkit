# backyes-site-toolkit

backyes.github.io 站点管理工具包。

## 目录结构

```
backyes-site-toolkit/
├── backyes.github.io/          # Pages 仓库克隆(发布目标)
├── scripts/
│   ├── sync_reports.sh         # rsync 同步 + git 提交
│   └── build_site.py           # 全页构建
├── CLAUDE.md                   # 建站经验(项目根目录)
├── POST_CREATION_GUIDE.md      # 文章/报告创建指南
└── README.md                   # 本文件
```

## 快速开始

```bash
cd backyes-site-toolkit

# 同步 AI 报告 + 构建页面 + 推送
./scripts/sync_reports.sh

# 预览(不推送)
./scripts/sync_reports.sh --dry-run

# 只同步特定项目
./scripts/sync_reports.sh umdk
```

## 创建新文章/报告

详见 [POST_CREATION_GUIDE.md](POST_CREATION_GUIDE.md)

## 前置条件

- GitHub Pages 仓库已创建: backyes/backyes.github.io
- fine-grained PAT 有 Contents 写权限
- 本机代理: 127.0.0.1:7897
- Python 3.9+ / matplotlib(图表生成)
