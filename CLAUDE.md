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

### 4.17 嵌套 .git 目录导致 Pages 构建全部失败（严重）
- **问题**: `sync_reports.sh` 报告"无变更"但站点不更新, 所有 GitHub Pages 构建失败 (duration=0, errored)
- **根因**: `spacex_space_economy_research/` 内含独立 `.git/` 目录, 被 git 记录为 **gitlink（子模块引用, mode 160000）**, 但仓库缺少 `.gitmodules` 文件定义其远程 URL
- **错误信息**: `fatal: No url found for submodule path 'spacex_space_economy_research' in .gitmodules`
- **影响**: GitHub Actions checkout 子模块时 fatal error, 连续 5 次构建全部失败
- **修复**:
  1. `git rm --cached <目录>` 移除 gitlink 引用
  2. 删除/移走目录内的 `.git/` 子目录
  3. `git add <目录>` 重新作为普通文件跟踪
  4. 将 `*.bak` / `*.bak_dark` 等备份模式加入 `.gitignore`
- **教训**:
  - **任何包含 `.git/` 的子目录都不能直接 `git add`**, 否则会被记录为 gitlink
  - 排查"站点不更新"时, 除检查 rsync 和 git status, **必须检查 GitHub Pages 构建状态**: `gh api repos/{owner}/{repo}/pages/builds/latest`
  - 构建 duration=0 + errored 通常意味着 Actions 调度失败或 checkout 阶段 fatal error
  - 用 `git ls-tree HEAD <目录>` 可检查是否被记录为 gitlink（mode 160000）

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

### ⚠️ 首页刷新强制规则

**每次新增/修改 post 或 research report 后，必须重新构建并推送首页。**

原因: `build_site.py` 生成的 `index.html` 包含:
- 顶部 "Recent Posts" 列表（最新 6 篇）
- "Survey by AI" 卡片网格（所有报告）
- 搜索数据库 `SEARCH_DB`（所有文章 + 报告）
- 报告数量统计（如 "20 AI survey projects"）

如果只同步报告 HTML 而未重建 `index.html`, 首页不会显示新内容, 搜索也找不到。

**正确流程:**
```bash
# 新增/修改 post 后:
cd ~/work/claude_workspace/backyes-site-toolkit
bash scripts/sync_reports.sh    # rsync 后自动调用 build_site.py 重建首页

# 或者手动:
cd backyes.github.io
python3 build_site.py
git add -A && git commit -m "refresh: update homepage" && git push origin main
```

## 七、任务经验记录

### 2026-08-16: 修复 GitHub Pages 构建全部失败（gitlink 子模块问题）

#### 任务概述
- **目标**: 站点"更新"后未生效, 排查根因并修复
- **产出**: 修复构建, 站点恢复正常 (HTTP 200)

#### 排查过程
1. `sync_reports.sh --dry-run` 显示 21 个项目全部 ~0 项变动 → 源文件无变更
2. `git status` 仅 `spacex_space_economy_research` 显示 modified → 发现嵌套仓库
3. `git diff HEAD origin/main` 为空 → 本地与远程一致, 不是 push 问题
4. **关键步骤**: `gh api repos/backyes/backyes.github.io/pages/builds/latest` → 发现 Status=building, duration=0
5. 查看最近 5 次构建: **全部 errored, duration=0**
6. `gh run view <id> --log-failed` → 定位到 Checkout 步骤报错: `fatal: No url found for submodule path 'spacex_space_economy_research' in .gitmodules`
7. `git ls-tree HEAD spacex_space_economy_research` → 确认为 `160000 commit`（gitlink）

#### 根因
`spacex_space_economy_research/` 内包含独立的 `.git/` 目录（嵌套仓库）, 被父仓库记录为 gitlink（子模块引用）, 但没有 `.gitmodules` 文件定义其 URL。GitHub Actions checkout 子模块时找不到 URL → fatal error → 构建失败。

#### 修复
```bash
git rm --cached spacex_space_economy_research          # 移除 gitlink
rm -rf spacex_space_economy_research/.git              # 删除嵌套 .git
git add spacex_space_economy_research/                 # 重新作为普通文件跟踪
echo "*.bak" >> .gitignore                             # 排除备份文件
git add .gitignore && git commit && git push
```

#### 教训
- **"sync 无变更"≠"站点最新"**: 必须检查 GitHub Pages 构建状态
- **排查站点不更新的三板斧**: ① rsync dry-run ② git status/diff ③ `gh api .../pages/builds/latest`
- **嵌套 .git 是定时炸弹**: 任何 `git add` 含 `.git/` 的子目录都会产生 gitlink, 必须提前排除
- **gh api 是诊断利器**: `pages/builds/latest` 的 status + duration 能快速区分"构建中/构建失败/调度失败"

#### 经验总结
- **Pages 构建状态诊断流程**: `gh api builds/latest` → 看 status → 若 errored 则 `gh run view <action_id> --log-failed` → 定位具体 step
- **duration=0 + errored** = 构建从未真正执行（调度或 checkout 阶段失败）, 不是代码逻辑问题

---

### 2026-08-12: UMDK Survey by AI 统一首页重构

#### 任务概述
- **目标**: 将 UMDK 的多份分析报告（CAM v1/v2 + URPC）合并为统一首页，参考 `deepep-dualpipe` 暖纸色学术风格
- **产出**: `umdk/index.html` 统一入口页 + 同步配置更新 + Essentials 区域刷新

#### 改动内容
1. **新建 umdk/index.html**: 暖纸色设计（Libre Baskerville + 墨绿主题），含报告卡片网格、架构总览 ASCII 图、核心发现、链接汇总
2. **同步配置**: `sync_reports.sh` 的 UMDK entry 从 `analysis/cam_v2/CAM深度分析报告_v2.html` 改为 `index.html`
3. **主站刷新**: main `index.html` 的 UMDK 卡片 + Essentials 区域卡片 + SEARCH_DB 三处同步更新
4. **CAM v2 报告**: 顶部添加 URPC 延伸阅读 banner（解决新报告在入口页无链接的问题）

#### 踩坑与教训
- **新报告同步后入口页找不到**: rsync 同步了 `urpc_architecture/` 但 CAM v2 报告里没有其链接 → 解决：在 CAM v2 顶部加 banner。**教训：新报告同步后必须检查入口页/导航页是否有对应链接**。
- **Essentials 区域未同步刷新**: 改了 Survey by AI 卡片和 SEARCH_DB，但遗漏了 Architecture & AI Essentials 区域的卡片 → **教训：站点内同一报告的链接可能出现在 3 处（Survey 卡片 + Essentials 卡片 + SEARCH_DB），必须全部检查**。
- **首页样式参考**: 参考 `deepep-dualpipe-synchronization-parallelization.html` 时，需复用其 CSS 变量（`--green`, `--paper-light`, `--font-serif` 等），保持全站视觉一致性。

#### 经验总结
- **多报告 Survey 首页模板**: Hero → 概览+blockquote → 卡片网格 → 架构图 → 核心发现 → 链接汇总
- **链接三处同步原则**: 任何报告入口变更必须同步更新：(1) Survey by AI 卡片 (2) Essentials 卡片 (3) SEARCH_DB
- **设计风格规范**: 已沉淀到 `backyes.github.io/CLAUDE.md` 的 "Survey by AI 报告首页规范" 章节

---

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

### 2026-08-07: 撰写 "DeepEP: From Expert Parallelization to Every Parallelization"

#### 方案
1. **核心论点**: DeepEP 从 EP 专用库扩展为 "Every Parallelization" 统一数据移动层，反映 AI infra 的 structural shift
2. **NCCL 平行对比**: NCCL 从 intra-node 扩展到 cluster-scale 的路径 vs DeepEP 从 EP 扩展到所有并行度的路径
3. **DeepEP V2 技术证据**: 引用 README 原文 — Engram (0 SM RDMA KV read)、PP primitives、AGRS (DP/TP)、NCCL Gin 后端 (SM 占用降低 4×)
4. **ICMS/CMX 定位**: NVIDIA 的 Inference Context Memory Storage（后改名 Context Memory eXtension），基于 BlueField-4 的 pod 级 KV-Cache 存储层

#### 踩坑与教训
- **两个 build_site.py 的陷阱**: `scripts/build_site.py` 是 toolkit 副本，`backyes.github.io/build_site.py` 才是 sync_reports.sh 实际调用的主脚本。`REPO = os.path.dirname(os.path.abspath(__file__))` 在 backyes.github.io/ 目录下运行才正确。**修改构建逻辑必须改 backyes.github.io/build_site.py**。
- **HTML 注释占位符被剥离**: 尝试用 `<!--HERO_ASIDE-->` 注释做动态内容占位符，但被外部进程（linter/HTML minifier）持续剥离。解决：直接匹配已有 HTML 结构 `<aside class="hero-aside"...>...</aside>` 做 regex 替换，不依赖注释占位符。
- **ICMS ≠ UCIe**: ICMS 是 NVIDIA 的 KV-Cache 存储平台（Inference Context Memory Storage），与 UCIe（Universal Chiplet Interconnect Express，芯粒互联标准）完全无关。References 里混淆两者是硬伤。
- **DeepEP README 可直接引用**: GitHub README 有项目自描述、V2 release notes、性能数据等权威原文，适合直接引用增强说服力。
- **争议性历史叙事可删**: NCCL 是否由百度先发明存在争议且不影响文章立意，删除更稳妥。
- **首页 aside 动态生成**: "Use This Page" 区域的最新文章链接和计数原来是硬编码，通过 `gen_hero_aside(posts)` 函数实现动态生成，每次 build 自动更新。

### 2026-08-08: 撰写 "Does Ultra-Long Context Exist? (1) — 16M and the Sparsity Dilution Wall"

#### 方案
1. **论文调研**: 并行 3 个 agent 分别研究 (a) HSA-UltraLong 论文 (b) DeepSeek V4 FlashMemory (c) 稀疏注意力架构
2. **核心论点**: Sparse attention 是 16M context 的模型架构必须路径，但 prefill 阶段稀疏被稀释 → 系统层级需要新存储介质
3. **数据驱动**: 从 FlashMemory-DS-V4 论文提取精确 KV cache 数据 (512K: 1.87GB, 1M: 3.73GB)
4. **带宽外推**: 512K→10M (20×), 20GB→400GB bandwidth, 证明当前存储层级断裂
5. **MRCR 失败案例**: 证明部分任务本质稠密 — 基础设施必须为尾部场景配置

#### 关键数据
- HSA-UltraLong: 8B MoE (1B activated), 8K 预训练 → 16M 推理 (500× 外推)
- HSA 机制: chunk size 64, top-k 64, NoPE 实现长度外推
- FlashMemory-DS-V4: 1M context KV cache 3.73GB → 0.37GB (90% reduction via LSA)
- 90% 请求只需要最近 8K tokens; MRCR 需要稠密全局内存

#### 踩坑与教训
- **PDF 读取**: `pdftoppm` 需要 `brew install poppler`，但 brew 可能被锁定。替代方案: Python `PyPDF2` 库直接提取文本，无需安装系统包
- **并行 agent 效率**: 3 个并行 agent 同时下载论文，总耗时 ~3 分钟完成全部研究素材收集
- **FlashMemory-DS-V4 论文**: 这是一篇独立的工作（非 DeepSeek 官方），描述在 DS-V4 上的 LSA 推理优化，提供了关键的 KV cache scaling 数据
- **带宽推算验证**: 用户提供的 "20GB@512K → 400GB@10M" 外推与论文数据一致 (1.87GB × 20 ≈ 37GB raw KV, 考虑多层多头和 chunk 开销 → ~400GB effective)

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
