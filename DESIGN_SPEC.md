# backyes.github.io 重构设计规格书

> 目标：以 Vikas Goyal (vikasgoyal.github.io) 博客风格为基底，融合现有 Posts 的 Lil'Log 阅读体验和 Survey by AI 的 astrofy 卡片风格，重构整个站点。

---

## 一、设计哲学

### 1.1 三种风格的定位

| 风格 | 来源 | 角色 | 核心特征 |
|---|---|---|---|
| **Vikas Goyal** | vikasgoyal.github.io | **主导风格** — 整站视觉语言 | 暖色纸张底色、玻璃拟态卡片、Libre Baskerville 衬线标题 + Manrope 无衬线正文、绿/金/蓝三色强调 |
| **Lil'Log (Posts)** | 现有 posts 样式 | **文章阅读体验** — 保留并适配到浅色主题 | Source Serif Pro 正文、左侧 TOC、`$number$` 蓝色高亮、`==text==` 下划线标记、数据驱动写作 |
| **astrofy (Survey)** | 现有 report cards | **报告卡片** — 保留并适配到浅色主题 | 大字号 visual placeholder、分类标签、悬停上浮、网格布局 |

### 1.2 设计原则
- **暖色纸张感**：告别深色模式，全文统一浅色暖调
- **玻璃拟态**：卡片使用 `backdrop-filter: blur()` + 半透明白色背景
- **大留白**：区块间距 26px，内衬 24-44px
- **圆角统一**：大卡片 28-36px，中卡片 20-24px，标签/按钮 999px (pill)
- **三色强调**：绿色(#0f5d44)为主强调 + 金色(#bf8b2c)为辅助高亮 + 蓝色(#163e7a)为链接

---

## 二、色彩系统

### 2.1 核心色板

```css
:root {
  /* 纸张底色系 */
  --paper: #f6f3ec;           /* 主背景 — 暖米黄 */
  --paper-light: #fcfaf6;     /* 渐变起始 — 近白 */
  --surface: rgba(255,255,255,0.86);   /* 卡片背景 — 半透明白 */
  --surface-strong: #ffffff;  /* 纯色卡片 */

  /* 墨水系 */
  --ink: #111111;             /* 主文字 — 近黑 */
  --ink-soft: #4d4d4d;        /* 次要文字 — 深灰 */
  --ink-mute: #6a6a6a;        /* 弱化文字 */
  --line: rgba(17,17,17,0.12); /* 边框 */

  /* 强调色 */
  --green: #0f5d44;           /* 主强调 — 深青绿 */
  --green-deep: #0a3f30;      /* 深绿 — 小标签文字 */
  --green-soft: rgba(15,93,68,0.10);  /* 淡绿背景 */
  --gold: #bf8b2c;            /* 辅助高亮 — 琥珀金 */
  --gold-soft: rgba(191,139,44,0.14); /* 淡金背景 */
  --blue: #163e7a;            /* 链接 — 深蓝 */

  /* 报告卡片灰阶 (替代原深色) */
  --card-chip: #2e333e;
  --card-network: #2b303a;
  --card-inference: #2a2f38;
  --card-cluster: #2d323c;
  --card-model: #2c313b;
  --card-storage: #2a3038;
  --card-recsys: #2b3138;
  --card-conference: #2d3038;
  --card-space: #2e3138;

  /* 功能色 */
  --shadow: 0 24px 60px rgba(17,17,17,0.10);
  --radius-lg: 28px;
  --radius-md: 18px;
  --radius-sm: 12px;
  --content-width: 1200px;
}
```

### 2.2 背景渐变

```css
body {
  background:
    radial-gradient(circle at top left, rgba(15,93,68,0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(191,139,44,0.14), transparent 24%),
    linear-gradient(180deg, #fcfaf6 0%, #f6f3ec 42%, #ffffff 100%);
}
```

---

## 三、字体系统

### 3.1 字体族

```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --font-serif: 'Libre Baskerville', Georgia, serif;        /* 标题 + 文章正文 */
  --font-sans: 'Manrope', 'Segoe UI', sans-serif;           /* UI + 卡片 + 标签 */
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;    /* 代码 + 日期 */
}
```

### 3.2 字号层级

| 用途 | 字号 | 字重 | 行高 | 字母间距 |
|---|---|---|---|---|
| Hero H1 | clamp(2.3rem, 4.8vw, 4.35rem) | 700 (serif) | 1.08 | -0.04em |
| Section H2 | clamp(1.7rem, 2.2vw, 2.35rem) | 700 (serif) | 1.2 | -0.03em |
| Card H3 | 1.08-1.25rem | 600-700 | 1.35 | -0.01em |
| Body | 1rem | 400-500 | 1.7-1.8 | 0 |
| Article body | 1.1rem | 400 (serif) | 1.8 | 0 |
| Meta/Tag | 0.78-0.92rem | 600-800 | 1.5 | 0.04-0.06em |

---

## 四、布局结构

### 4.1 整站外壳

```css
.page-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px 72px;
}
```

### 4.2 页面结构 ( Homepage )

```
┌─────────────────────────────────────────────────┐
│ .topbar                                         │
│   .brand (左)          .topnav (右，pill 标签)   │
├─────────────────────────────────────────────────┤
│ .hero (grid 1.45fr + 0.85fr)                    │
│   .hero-panel (左)      .hero-aside (右)         │
│   - eyebrow             - aside-kicker           │
│   - H1                  - aside-title            │
│   - hero-copy           - aside-text             │
│   - hero-actions        - aside-list             │
│   - hero-metrics (3列)                           │
├─────────────────────────────────────────────────┤
│ .signal-grid (4列卡片)                            │
├─────────────────────────────────────────────────┤
│ .section-card #essential-reads                   │
│   .section-heading (标题 + 描述)                   │
│   .featured-grid (3列 article-card)               │
├─────────────────────────────────────────────────┤
│ .two-up (grid 1.15fr + 0.85fr)                   │
│   .section-card (Posts 预览)                      │
│   .section-card (分类索引)                         │
├─────────────────────────────────────────────────┤
│ .paths-grid (4列 path-card)                      │
├─────────────────────────────────────────────────┤
│ .section-card #latest                            │
│   .latest-grid (3列 latest-card)                  │
├─────────────────────────────────────────────────┤
│ .footer-grid (2列 footer-card)                    │
└─────────────────────────────────────────────────┘
```

### 4.3 响应式断点

| 断点 | 宽度 | 调整 |
|---|---|---|
| Desktop | > 1080px | 全宽度多列 |
| Tablet | ≤ 1080px | hero/two-up/newsletter → 单列; grid → 2列 |
| Mobile | ≤ 720px | 全部单列; topbar 纵向堆叠; 字号缩小 |

---

## 五、组件规格

### 5.1 Topbar

```
.topbar: flex, justify-content: space-between
.brand:
  .brand-name: Libre Baskerville 1.7rem, 700, letter-spacing -0.03em
    内含 SVG 图标链接 (LinkedIn/GitHub 等)
  .brand-tagline: Manrope 0.95rem, ink-soft
.topnav:
  a: pill (999px), 10px 14px, 0.92rem, 半透明白色背景, 细边框
  a:hover: 边框加深, translateY(-1px)
  a.nav-accent: 绿色渐变背景 + 白色文字 (主 CTA)
```

### 5.2 Hero

```
.hero: grid 1.45fr + 0.85fr, gap 24px
.hero-panel:
  border-radius: 36px, padding 44px
  背景: 玻璃拟态 + 微绿/金色渐变叠加
  .eyebrow: pill 标签, 绿色小字, uppercase
  H1: Libre Baskerville, clamp(2.3-4.35rem), 12ch max-width
  .hero-copy: 1.08rem, line-height 1.8, ink-soft
  .hero-actions: flex, pill 按钮
    .button-primary: 绿色渐变, 白色文字
    .button-secondary: 白色背景 + 细边框
  .hero-metrics: 3列 grid, 每个 metric 卡片
.hero-aside:
  border-radius: 30px, 玻璃拟态
  内含 aside-kicker / aside-title / aside-text / aside-list
```

### 5.3 Signal Grid

```
.signal-grid: 4列 grid, gap 20px
.signal-card:
  border-radius: 22px, 玻璃拟态
  strong: 1.1rem, block, margin-bottom 8px
  p: ink-soft, 0.95rem
```

### 5.4 Section Card

```
.section-card:
  border-radius: 32px, padding 30px, 玻璃拟态
  margin-bottom: 26px
.section-heading:
  flex, justify-content: space-between
  H2: Libre Baskerville, clamp(1.7-2.35rem)
  p: ink-soft, max-width 55ch
```

### 5.5 Article Card (Featured Reports)

```
.featured-grid: 3列 grid, gap 20px
.article-card:
  flex column, border-radius 24px, padding 24px, 玻璃拟态
  min-height: 100%
  .article-tag: pill, 绿色背景, uppercase, 0.78rem
  H3: 1.25rem, line-height 1.35
  p: ink-soft
  .article-link: margin-top auto, 蓝色加粗, "Read →"
```

### 5.6 Path Card (Browse by Need)

```
.paths-grid: 4列 grid, gap 20px
.path-card:
  border-radius 22px, padding 22px, 玻璃拟态
  H3: 1.15rem
  p: ink-soft, 0.95rem
  .path-links: grid, gap 10px
    a: 蓝色加粗
```

### 5.7 Latest Card (Recent Posts)

```
.latest-grid: 3列 grid, gap 20px
.latest-card:
  border-radius 20px, padding 20px, min-height 220px, 玻璃拟态
  time: 0.82rem, uppercase,  mono
  H3: 1.08rem, line-height 1.45
  p: ink-soft
```

### 5.8 Report Cards (Survey by AI)

```
.grid: auto-fill, minmax(340px, 1fr), gap 22px
.card:
  flex column, border-radius 18px
  背景: 玻璃拟态 (保留原有卡片深色 visual 区域)
  .card-img: height 200px, 深色灰底
    .visual: 大字标题 (保留原有风格)
    .tag: pill 分类标签
  .card-body: padding 18-22px
    H3: 1.08rem
    p: ink-soft
    .card-foot: "阅读 →" 链接
```

### 5.9 Footer

```
.footer-grid: 2列 grid
.footer-card:
  border-radius 26px, padding 24px, 玻璃拟态
  .footer-links: flex, wrap, pill 链接
```

---

## 六、页面模板规格

### 6.1 index.html (Homepage)

**顺序**：
1. Topbar (brand + nav)
2. Hero (headline + metrics + aside)
3. Signal Grid (4 cards — 站点覆盖领域)
4. Essential Reads (Featured Reports, 6 篇 p0)
5. Two-up (Posts 预览 6 篇 + 分类索引)
6. Browse by Need (4 path cards)
7. Latest Writing (6 latest posts)
8. Footer

**Hero 内容**：
- eyebrow: "For AI Infrastructure Researchers"
- H1: "How to think clearly about AI system design, chip architecture, and infrastructure leverage."
- copy: 关于站点定位的 1-2 句描述
- metrics: 3 个 (系统架构 / 芯片设计 / 产业洞察)

### 6.2 posts.html (Posts List)

**风格**：保留 Lil'Log 阅读体验，适配浅色主题
- 顶部：page标题 + 简短描述
- 列表：保留 date-left / content-right grid
- 卡片化：每篇 post 用玻璃拟态卡片包裹
- TOC、正文样式不变（article 页面）

### 6.3 post article page

**保留**：
- 左侧 TOC sidebar (sticky)
- 正文 Source Serif Pro / Libre Baskerville 衬线
- `$number$` 蓝色高亮
- `==text==` 下划线标记
- 表格样式、代码块、引用
- KaTeX 数学公式

**变更**：
- 深色 → 浅色（纸张背景）
- 导航栏 → 新 topbar 风格
- 字体 → Libre Baskerville + Manrope

### 6.4 tags.html

**保留**：标签聚合功能
**变更**：
- 深色 → 浅色玻璃拟态
- 侧边栏 → 新风格

---

## 七、build_site.py 修改规格

### 7.1 新增生成函数

| 函数 | 用途 |
|---|---|
| `gen_hero()` | 生成 hero 面板 (eyebrow + H1 + copy + actions + metrics) |
| `gen_hero_aside()` | 生成 hero 侧栏 |
| `gen_signal_grid()` | 生成 4 个 signal-card |
| `gen_featured_reports()` | 生成 6 篇 p0 report 卡片 |
| `gen_two_up()` | 生成 Posts + 分类双栏 |
| `gen_paths_grid()` | 生成 4 个 path-card |
| `gen_latest_posts()` | 生成最新文章卡片 |
| `gen_footer()` | 生成 footer 网格 |

### 7.2 保留函数

| 函数 | 用途 |
|---|---|
| `gen_cards()` | Survey by AI 报告卡片 (不变) |
| `gen_search_db()` | 搜索数据 (不变) |
| `gen_posts_list()` | 文章列表 (适配浅色) |
| `gen_post_page()` | 单篇文章 HTML (适配浅色) |
| `md_to_html()` | Markdown 渲染 (不变) |

### 7.3 模板占位符 (index.html)

```html
<!--HERO-->...<!--/HERO-->
<!--SIGNAL_GRID-->...<!--/SIGNAL_GRID-->
<!--FEATURED_REPORTS-->...<!--/FEATURED_REPORTS-->
<!--TWO_UP-->...<!--/TWO_UP-->
<!--PATHS_GRID-->......<!--/PATHS_GRID-->
<!--LATEST_POSTS-->...<!--/LATEST_POSTS-->
<!--FOOTER-->...<!--/FOOTER-->
<!--PROJECT_CARDS-->...<!--/PROJECT_CARDS-->  (Survey by AI, 保留)
const SEARCH_DB=...;
<!--TAG_CLOUD-->...<!--/TAG_CLOUD-->
```

---

## 八、实施步骤

### Phase 1: 备份 ✅
- [x] 复制 backyes.github.io 到 _backup_20260731_093750/
- [x] git bundle 创建

### Phase 2: CSS 重构
- [ ] 写新 `assets/css/main.css` (暖色主题 + 玻璃拟态 + 全部组件)
- [ ] 保留 `assets/report-theme.css` (报告页面独立主题，不改)

### Phase 3: build_site.py 重构
- [ ] 新增 7 个生成函数
- [ ] 修改 index.html 模板结构
- [ ] 适配 posts.html / tags.html 到浅色
- [ ] 适配 gen_post_page() 到浅色
- [ ] 更新 placeholder 匹配逻辑

### Phase 4: 模板 HTML 重写
- [ ] 写新 index.html (含完整 Vikas 风格骨架)
- [ ] 写新 posts.html
- [ ] 写新 tags.html

### Phase 5: 构建验证
- [ ] 运行 build_site.py
- [ ] 本地预览 (python3 -m http.server)
- [ ] 检查所有页面、链接、搜索
- [ ] 移动端响应式

### Phase 6: 部署
- [ ] git commit
- [ ] git push
- [ ] 验证 GitHub Pages 构建

---

## 九、文件变更清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `assets/css/main.css` | **重写** | 暖色主题设计系统 |
| `assets/report-theme.css` | 不改 | 报告页面独立 CSS |
| `build_site.py` | **重写** | 新增 7 个生成函数 |
| `index.html` / `index.template.html` | **重写** | Vikas 风格首页骨架 |
| `posts.html` / `posts.template.html` | **重写** | 浅色文章列表 |
| `tags.html` / `tags.template.html` | **重写** | 浅色标签页 |
| `posts/*.html` (生成) | 重新生成 | 新浅色文章页 |
| `posts/*.md` (源) | 不改 | 文章源文件保留 |
| `reports/*/` (目录) | 不改 | 报告目录保留 |
| `DESIGN_SPEC.md` | **新建** | 本规格书 |

---

## 十、关键决策记录

### D1: 为什么选 Vikas Goyal 风格为主导？
- 专业感强：暖色纸张 + 衬线字体 = 学术/技术写作可信度
- 可读性优：浅色背景适合长文阅读 (Posts 的核心场景)
- 差异化：深色 AI 博客泛滥，暖色独树一帜

### D2: 深色报告卡片如何处理？
- 保留原有 `.card-img` 深色灰底 + 大字 visual
- 仅将卡片外框改为玻璃拟态风格
- 报告内容页面 (DeepEP, vLLM 等) 保持原有深色主题

### D3: 字体替换
- Inter → Manrope (更圆润，更"出版感")
- Source Serif Pro → Libre Baskerville (更经典衬线)
- JetBrains Mono 保留 (代码)

### D4: 导航栏
- 不再使用 sticky 顶部栏
- 改为 Vikas 风格：品牌名左侧 + pill 导航右侧
- 滚动时保持静态 (不吸顶)
