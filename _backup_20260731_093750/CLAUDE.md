# 建站经验沉淀

> backyes.github.io — LLM Infrastructure Insights (Research Hub)

## 一、技术栈选型

| 层 | 选择 | 原因 |
|---|---|---|
| 托管 | GitHub Pages | 免费、与 repo 原生集成、自动 HTTPS |
| 仓库名 | `backyes.github.io` | 用户站点强制命名规则(仓库名 = 域名) |
| 发布源 | main 分支根目录 | 用户站点默认配置 |
| 构建 | 纯静态 HTML + Python 脚本 | 无 Jekyll / 无 Actions 依赖 |
| 同步 | rsync + git push | 增量同步、幂等 |

## 二、项目架构

```
backyes-site-toolkit/           # 管理工具仓库 (只放脚本, 不放内容)
├── scripts/
│   ├── sync_reports.sh         # rsync 同步研究报告 + git 提交的入口
│   └── build_site.py           # 全页构建 (cards + posts + tags + search)
├── backyes.github.io/          # Pages 仓库克隆 (发布目标 + 所有文章源)
│   └── posts/                  # 手写文章源 (*.md, 与生成的 .html 同目录)
├── experience.md               # 经验沉淀
└── CLAUDE.md                   # 本文件

⚠️ 架构原则:
- 文章源文件(.md)只存在于 backyes.github.io/posts/, 不从 toolkit 同步
- toolkit 只包含构建/同步脚本, 不存储文章内容
- build_site.py 读取的是 backyes.github.io/posts/*.md
```

## 三、关键设计决策

### 3.1 数据驱动
- `build_site.py` 的 `REPORTS` 数组是唯一真相源
- 每份报告: `{dst, entry, visual, title, desc, cat, priority, tags}`
- `sync_reports.sh` 的 `PROJECTS` 数组负责 rsync 源路径
- 两者保持同步

### 3.2 增量同步策略
```bash
rsync -a --delete --delete-excluded \
  --include="*/" --include="*.html" --include="*.css" \
  --include="*.png" --include="*.jpg" --exclude="*" \
  "$SRC/" "$REPO/$DST/"
```
- 白名单: html + css + png/jpg/svg/webp/ico
- 排除原始素材: md / txt / pdf / py / js / json / log
- 排除目录: raw/ / raw_material/ / _raw/ / logs/ / cache/

### 3.3 rsync 排除目录不删目标的修复
仅 `--exclude=raw` 不够 — 被 exclude 的路径 rsync 既不复也不删。
需要加 `--delete-excluded` 让目标端被排除的目录被主动清掉。

### 3.4 卡片视觉
- 早期: emoji (📘 🔀) → 不具备辨识度
- 中期: SVG + 固定 px 字号 → 不自适应
- 当前: HTML div + `clamp(2rem,4vw,3rem)` → 匹配首页 hero 字体风格,响应式

### 3.5 配色哲学 (Lil'Log-inspired)
- 整体: 黑白灰 + 单蓝色链接
- 去渐变、去多彩色
- `--bg:#111317` `--fg:#d7dbe0` `--accent:#4a8fe0`
- 标签统一灰色,仅 active 时用蓝色

### 3.6 文章结构
- **宏观→微观:** 先场景(图表)→量化(表格)→结论→展望
- **每日分析:** 每行含计算公式,便于核查
- **对比分析:** 投影到未来规模(1B/10B),不只看当前数据

## 四、踩过的坑

### 4.1 GitHub Pages 开关
- 用户站点 main 根目录自动发布,无需手动开 Pages
- `gh api PUT /repos/.../pages` 会 403 (fine-grained token 缺 pages scope)
- **解决:** 推送到 main 后 Pages 自动激活,等 1-3 分钟构建

### 4.2 fine-grained PAT 权限
- `github_pat_` 前缀 = fine-grained token
- 缺 Contents 写权限 → push 403
- **解决:** 编辑 token → Contents = Read and Write

### 4.3 GitHub 网络需要代理
- ping 通 github.com 但 HTTPS 443 被拦截
- **解决:** `git config http.proxy http://127.0.0.1:7897`

### 4.4 GitHub Actions 部分中断
- Pages build 依赖 Actions 基础设施
- Actions 部分中断时 build 作业调度不上 (duration=0 持续几分钟)
- **解决:** 等恢复,通常几十分钟内

### 4.5 rsync filter 顺序
- 排除目录规则**必须**放在 `--include=*/` 之前
- 否则 `--include=*/` 先匹配并进入 raw/ 目录,后面 exclude 失效

### 4.6 SEARCH_DB 双重括号
- template 有 `[]` + JSON.stringify 又加 `[]` → `[[...]]`
- **解决:** regex 改为 `const SEARCH_DB=(?:\[.*?\]|<!--SEARCH_DB-->);`

### 4.7 仓库改名
- 用户站点仓库**必须**等于 `<username>.github.io`
- 只改仓库名不能改站点域名
- 真正迁移需要新建 GitHub 账号

### 4.8 CSS 在 f-string 中
- 单 `{` `}` 必须写成 `{{` `}}`,否则 SyntaxError

### 4.9 双 `</style>` 标签
- CSS 内联在 f-string 中只能有一个 `<style>...</style>` 对
- 多余 CSS 放到 `</style>` 后会被当文字渲染成乱码

### 4.10 Markdown `$` 符号
- `$number$` 会被正则匹配,需转义或避免在公式中使用

### 4.11 导航响应式
- JS 动态测量: 先全部显示、隐藏 `⋯`,放不下才折叠
- 桌面端空间够时全展示,不够才折叠
- **手机端:** 直接 `.nav-more{display:none!important}`,不用 JS 计算

### 4.12 文章列表移动端
- 手机改为上下排列 (`display:block`),不要左右 grid
- 充分利用屏幕宽度,摘要不再被截断

### 4.13 rsync --delete 误删文章（严重）
- **问题**: sync_reports.sh 从 toolkit/posts/ 同步到 repo/posts/ 时带 `--delete`
- **根因**: toolkit posts/ 只有新文章, rsync 删掉了 repo 里所有其他文章
- **解决**: 文章直接在 `backyes.github.io/posts/` 管理, 删除了 posts 同步逻辑
- **教训**: **rsync --delete 只用于单向同步的素材文件, 不适用于双向管理的内容**

### 4.14 文章源文件存放位置
- **决策**: .md 源文件只存在于 `backyes.github.io/posts/`, 与生成的 .html 同目录
- **原因**: 文章是网站内容的一部分, 不是外部素材; 避免双向同步数据丢失
- **toolkit 只放工具**: `backyes-site-toolkit/` 不存储任何文章内容

### 4.15 CSS Grid 布局溢出
- **问题**: `grid-template-columns: 130px 1fr` 中长内容溢出容器
- **根因**: Grid 的 `1fr` 列默认 `min-width: auto`, 内容可撑开容器
- **解决**: `.posts-item { min-width: 0; }` + `.posts-content { min-width: 0; overflow: hidden; }`
- **教训**: **Grid/Flex 子容器必须显式 `min-width: 0`** 才能正确约束内容溢出

### 4.16 跨文章链接应指向具体章节
- **问题**: `[2](#ref-2)` 只跳到文末参考文献, 不直接链接到被引用的文章
- **解决**: 使用 `article.html#section-anchor` 直接定位到具体章节
- **教训**: **引用链接应直接指向目标内容**, 不通过文末参考文献中转

## 五、写文章经验

### 数据驱动型写作
- **先定结论** → 一句话锚点,所有数据为它服务
- **骨架优先** → 读者 30 秒扫完全文(标题+表格+图表)
- **能用表格不用文字** → 让读者自己算,不替读者做判断
- **控制字数** → 删比写更重要,去掉不影响结论的段落
- **主观判断必须有数据兜底** → 无数据支撑的结论不说
- **迭代修改** → v0.1 数据堆砌 → v2.0 精简核心

### 数据核实
- 所有报价必须来自官方文档,标注来源链接
- 计算过程要展示,让读者可验证
- 价格/数据更新时,全文所有相关数字都要同步修改
- **每次改价格后,全文搜索所有相关数字并更新**

### 可视化增强
- 图表是文章的核心证据,放在每日分析表格之前
- 图表加水印(`backyes.github.io`)防止盗用
- 关键数字用 `$number$` 蓝色高亮
- 关键结论用 `==text==` 下划线标记
- 对比表格用柱状图 + 倍数曲线(双 Y 轴)
- **手机端:** 图表宽度 `max-width:100%`,表格可横向滚动

### 配色哲学
- Lil'Log 风格: 黑白灰 + 单蓝色链接
- 去渐变、去多彩色
- 标签统一灰色,仅 active 时用蓝色

### 文章结构
- **宏观→微观:** 先场景(图表)→量化(表格)→结论→展望
- **每日分析:** 每行含计算公式,便于核查
- **对比分析:** 投影到未来规模(1B/10B),不只看当前数据

## 六、维护命令

```bash
# 研究报告同步 (从 claude_workspace/ 同步到 backyes.github.io/)
cd ~/work/claude_workspace/backyes-site-toolkit
bash scripts/sync_reports.sh              # 全量同步 + 提交 + 推送
bash scripts/sync_reports.sh --dry-run    # 预览
bash scripts/sync_reports.sh --no-push    # 本地试
bash scripts/sync_reports.sh umdk         # 只同步某项目

# 文章发布 (直接在 backyes.github.io/ 里操作)
cd ~/work/claude_workspace/backyes-site-toolkit/backyes.github.io
# 1. 编辑或新增 posts/*.md
# 2. 构建页面
python3 build_site.py
# 3. 提交并推送
git add -A && git commit -m "add post: xxx" && git push origin main
```

## 七、任务经验记录

### 2026-07-28: 文章发布流程重构 + 误删事故

#### rsync --delete 误删所有文章（严重）
- **问题**: `sync_reports.sh` 中有一段从 `backyes-site-toolkit/posts/` 同步到 `backyes.github.io/posts/` 的逻辑，带 `--delete` 标志。当 toolkit 的 posts/ 目录只有新文章时，rsync 会删除目标端所有其他文章。
- **根因**: 文章源文件被放在两个地方（toolkit + repo），rsync 以源端为准删除目标端多余文件。
- **解决**: 文章直接在 `backyes.github.io/posts/` 管理，删除 sync_reports.sh 中的 posts 同步逻辑，toolkit 只保留工具脚本。
- **教训**: **rsync --delete 是危险的**，特别是当源端和目标端内容不完全相同时。对于需要双向管理的文件（如文章源文件），不应使用 rsync 同步，应选择单一管理位置。

#### 文章源文件应存放在网站仓库内
- **决策**: 所有 `.md` 源文件只存放在 `backyes.github.io/posts/`，与生成的 HTML 同目录。`build_site.py` 直接读取 repo 自身的 posts/ 目录。
- **原因**: 文章是网站内容的一部分，不是"外部素材"；避免双向同步导致的数据丢失；简化发布流程：编辑 .md → build → commit → push

#### CSS Grid 布局溢出问题
- **问题**: 文章列表页 `posts-item` 使用 `grid-template-columns: 130px 1fr`，长内容（摘要、标签）溢出容器超出屏幕右边界。
- **根因**: Grid 的 `1fr` 列默认 `min-width: auto`，内容可以撑开容器。
- **解决**: `.posts-item { min-width: 0; }` + `.posts-content { min-width: 0; overflow: hidden; }` + `.posts-excerpt { overflow-wrap: break-word; }`
- **教训**: **Grid/Flex 子容器必须显式设置 `min-width: 0`** 才能正确约束内容溢出。

#### 跨文章链接应指向具体章节
- **问题**: 文中引用 `[2](#ref-2)` 只跳到文末参考文献列表，而非直接链接到被引用的文章。
- **解决**: 直接使用文章的章节锚点链接，如 `ai-supernode-unified-addressing-first-principles.html#12-the-rdma-analogy-...`。
- **教训**: **引用链接应直接指向目标内容**，而非通过文末参考文献中转。

### 2026-07-28: 撰写 "When Do We Need a Global Address Service" 文章

#### 方案
1. **结构**: 按用户要求的三段式：地址服务分类 → 地址服务不只是易用性（Engram 案例）→ AI 系统中的时延分类法
2. **核心论点提升**: 将用户的直觉洞察提炼为"摊销通信管道建立成本"（amortizing the cost of establishing communication pipes）
3. **Engram 分析**: 从五个矛盾特性（大容量/小带宽/细粒度/高IOPS/低时延）推导出共享需求，进而推导出需要独立地址服务
4. **时延分类法**: 从 Redis(ms) → RDMA(百µs) → NVLink(十µs) 的完整地址服务谱系
5. **引用**: 补充了 RDMA programming manual、CXL spec、Parameter Server (Li et al.)、vLLM PagedAttention、DeepRec 等学术/工业参考

#### 踩坑
- **build_site.py 路径**: 脚本的 REPO 指向 `scripts/` 目录，但实际应在 `backyes.github.io/` 目录运行。正确做法：`cd backyes.github.io && python3 build_site.py`
- **Markdown 引用格式**: 使用 `<a id="ref-N"></a>[N](#ref-N)` 格式，与现有文章一致

### 2026-07-28: 统一报告主题 + 系统深色/浅色模式

#### 方案
1. **KaTeX 渲染公式**: 引入 KaTeX 0.16.11 CDN，配置 `$...$` / `$$...$$` 分隔符
2. **共享 CSS 文件**: 创建 `assets/report-theme.css`，包含：Light/Dark 双模式、185 个 CSS 类名、main.css 额外变量兼容
3. **批量替换**: Python 脚本将 29 个报告的 `<style>` 块替换为 `<link>` 引用
4. **Posts 特殊处理**: 恢复文章专属样式（.article-layout, .toc-sidebar），三层 CSS 叠加

#### 踩坑
- **Posts 样式丢失**: 初次批量替换时，posts 的 article-specific 样式被误删。解决：从 git 恢复原始 `<style>` 块，再插入到 `</head>` 前
- **CSS 变量覆盖**: report-theme.css 的 `:root` 后加载会覆盖 main.css 变量，但 main.css 有额外变量需要补全
- **价格符号 vs LaTeX**: 大部分报告的 `$` 是价格（`$5M/机架`），不是数学公式。只有 DeepEP 有真正的 LaTeX
