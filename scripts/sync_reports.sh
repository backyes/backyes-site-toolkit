#!/usr/bin/env bash
# =============================================================================
# sync_reports.sh — 增量同步工作区研究报告到 backyes.github.io (GitHub Pages)
#
# 设计:
#   - 数据驱动: 下方 PROJECTS 数组是唯一的"项目清单", 增删项目只改这里
#   - rsync 白名单: 只带 HTML + 展示性资源 (css/png/jpg/svg...), 排除原始素材
#   - 自动重写 index.html 的项目卡片区 (按 <!--PROJECT_CARDS--> 标记)
#   - 幂等: 多次运行结果一致, 无变更时不会空提交
#
# 用法:
#   ./sync_reports.sh              # 同步全部项目 + 提交 + 推送
#   ./sync_reports.sh --dry-run    # 仅预览, 不写盘不提交
#   ./sync_reports.sh --no-push    # 同步 + 提交到本地, 不推送 (批量调完再手动 push)
#   ./sync_reports.sh pd-separation moe-clos   # 只同步指定项目 (按仓库内目录名匹配)
# =============================================================================
set -euo pipefail

# ------- 运行配置 -------
WORKSPACE="$( cd "$( dirname "$0" )/.." && pwd )"  # 工作区根 (脚本所在目录的上一级)
REPO="$WORKSPACE/backyes.github.io"                # Pages 仓库克隆位置
SRC_ROOT="$( cd "$WORKSPACE/.." && pwd )"           # 研究报告源根目录 (claude_workspace/)
PROXY="http://127.0.0.1:7897"                       # 本机代理 (push 走这里)
FORCE_GIT=0                                        # 设 1 则无变更也提交
TARGETS=()                                         # 空 = 全部; 否则只同步指定目录名

# ------- 解析参数 -------
DRY_RUN=0
DO_PUSH=1
for a in "$@"; do
  case "$a" in
    --dry-run)   DRY_RUN=1 ;;
    --no-push)   DO_PUSH=0 ;;
    -h|--help)   head -12 "$0" | sed 's/^# \?//'; exit 0 ;;
    *)           TARGETS+=("$a") ;;
  esac
done

# ------- rsync 白名单 (顺序很重要: 先 include 想要的, 最后 exclude * ) -------
# 展示性资源之外的全部排除: .md .txt .pdf .py .js .json .log .sh .rst .crx 等
# ⚠️ 顺序极重要: 排除目录的规则必须在 --include=*/ 之前,
# 否则 --include=*/ 会先匹配并进入 raw/ 目录, 后面再 exclude 就失效了。
RSYNC_FILTER=(
  # 先排除原始素材目录 (即使里面含 html 也不发布)
  "--exclude=raw" "--exclude=raw_material" "--exclude=_raw"
  "--exclude=logs" "--exclude=log" "--exclude=cache" "--exclude=tmp"
  "--exclude=.git" "--exclude=.DS_Store" "--exclude=__pycache__"
  # 再包含想要的
  "--include=*/"
  "--include=*.html" "--include=*.HTML"
  "--include=*.css"
  "--include=*.png" "--include=*.jpg" "--include=*.jpeg" "--include=*.gif"
  "--include=*.svg" "--include=*.webp" "--include=*.ico"
  "--exclude=*"
)

# ======================= 项目清单 (唯一的增删入口) =======================
# 字段 (pipe 分隔):
#   源相对路径 | 仓库内目录名 | 入口html | emoji | 标题 | 描述 | 分类 | 优先级
#   分类: inference / system / network / chip / mixed
#   优先级: p0=旗舰 / p1=常规 / p2=轻量
# ------------------------------------------------------------------------------
PROJECTS=(
  "umdk_research|umdk|analysis/index.html|🔬|UMDK 深度分析文档索引|3 份主报告 + 16 篇 CAM Agent 深挖 + 10 篇 URPC 专题文档 · CAM v2 (8章) / URPC (11篇) / CAM v1 · 21K+ 分析行数|chip|p0"
  "amd-latest-tech-2026|amd-latest-tech-2026|index.html|🔴|AMD 全栈 AI 基础设施调研|CDNA 5 GPU · Helios 机架 · UALink 总线 · ROCm.ai · EPYC Venice · Gorgon Halo · 16 章 50+ 引用|chip|p0"
  "vllm_research/vllm_analysis|vllm_research/vllm_analysis|index.html|📘|vLLM 架构统一分析|12 章统一分析 (第一性原理 / 热路径 / KV-Cache 4 层 / 分布式 / Ascend Overlay / Perf Handbook) · 合并 spine+L4 agent+源码+社区 90d pulse · 每节 source 溯源锚点|inference|p0"
  "pd-separation-kvcache-research|pd-separation|report.html|🔀|P/D 分离 KVCache 流通|vLLM / SGLang / LMCache / Mooncake / Dynamo 五大框架的 Prefill-Decode 分离 + KV Cache 路由内部实现源码级拆解 · BootstrapQueue→WaitingQueue→InflightQueue 全生命周期|inference|p0"
  "mlsys2026_report|mlsys2026|index.html|🎓|MLSys 2026 深度综合|Keynote + 19 篇论文逐篇深度解读后的跨论文战略综合 · 6 条主轴: 同步税 / 存储层级重定义 / P2P 转移 / Superchip 冲击 / 批判性转向 / 训练路线分叉|mixed|p0"
  "deepseek_mtp_research|deepseek-mtp|index.html|⚡|DeepSeek MTP 算力影响|dspark MTP 算法对算力与总线系统行业的深度影响分析 · 算法设计者视角的范式推演|inference|p1"
  "moe_clos_research|moe-clos|report.html|🕸|Sparse CLOS × MoE 推理|MoE 专家并行推理在 Sparse CLOS 网络上的效率与成本收益深度分析 · MegaScale / MixNet / UBEP / SpecMoE 多篇对比|network|p1"
  "generative_recommendation_research/report|generative-rec|generative_recommendation_report.html|🎯|生成式推荐研究热点|2026 年 Generative Recommendation 最新研究热点调查报告 · 算法 + 系统 + 工业落地|mixed|p1"
  "sparse_clos_research|sparse-clos|sparse_clos_report.html|🌐|Sparse Clos 组网深度调研|Sparse Clos / SlimFly / Jupiter 等无阻塞组网技术的深度调研 · 来源: 论文 + 厂商 + 学术会议|network|p1"
  "ai_supernode_bus_research|ai-supernode-bus|report.html|🔗|AI 超节点总线调研|2026H1 AI 超节点总线技术市场调研 · NVLink / UALink / PCIe 6 / 光互联 + 产业格局|chip|p1"
  "supernode_metrics_research|supernode-metrics|supernode_metrics_report.html|📐|超节点指标定义|超节点行业指标定义深度调研 · 制造商(NVIDIA/华为/Google) / 云商 / 学术 三视角 + 量化指标体系|mixed|p1"
  "mtp_survey/report|mtp-survey|MTP_DSpark_Survey.html|🧭|MTP 算法 Survey|大模型推理 MTP (Multi-Token Prediction) 算法 Survey · 围绕 DeepSeek DSpark 的全景调研|inference|p1"
  "3DLS|3dls|3DLS_analysis_report.html|🧊|3DLS 论文深度分析|3DLS 论文深度分析报告 · 芯片 / 系统 / AI 推理架构 交叉视角|chip|p2"
  "space_ecom/research|space-ecom|report.html|🚀|太空经济联盟调研|联盟首批意向成员 + 初创企业调研报告 · 含 306 家深度分析|mixed|p2"
  "pd_routing_research|pd-routing|report.html|🔀|PD 分离 Request Routing|PD 分离请求路由源码级拆解 · SGLang / Mooncake / LMCache 内部队列|inference|p1"
  "trillium_nvidia_analysis|trillium|Trillium_vs_NVIDIA_LPX_架構分析.html|🧊|Trillium vs LPX|Groq Trillium 与 NVIDIA LPX 微架构 / 集群架构深度对比|chip|p1"
  "spacex_space_economy_research|spacex|太空经济与SpaceX深度分析报告.html|🛰|SpaceX 深度分析|SpaceX 全版图深度分析 · 产品/财务/合同/技术 · 中国对比 · AI算力视角|space|p0"
  "hbm_cxl_memory_research|hbm-cxl|report.html|💾|HBM/CXL/Memory|HBM CXL NAND 内存层级市场深度调研 · 三星/SK海力士/美光|storage|p1"
  "inference-community-2026|inference-community|report.html|🌐|vLLM vs SGLang|vLLM vs SGLang 推理引擎社区调研 · Benchmark / 架构演进 / PD Disagg / KV Cache 设计哲学|inference|p1"
  "DeepEP_research|deep-ep|index.html|⚙️|DeepEP 深度分析索引|源码级深度分析索引 · 主报告 + 三视角分报告 + 交叉讨论 + 专题深潜 · MoE 专家并行 AllToAll / NVLink+RDMA / Low-Latency / 性能基准|network|p0"
  "deepgemm_research/docs|deepepv2|html/index.html|🔬|DeepGEMM & DeepEP Survey by AI (审核中)|49 篇深度分析报告（架构4篇 + 博客↔DeepGEMM 10篇 + 三向对比9篇 + DeepEP独立分析11篇 + 测试分析7篇 + 对称内存4篇 + V2弹性架构4篇）· 博客理论 ⇌ DeepEP源码 ⇌ DeepGEMM源码 · 核心发现：同步范式 Barrier→mbarrier FIFO / 通信模型 消息传递→Load-Store 对称内存直传|chip|p0"
)
# ==============================================================================

# ------- 辅助函数 -------
log()  { printf "\033[1;36m▶ %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m⚠ %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m✓ %s\033[0m\n" "$*"; }
dim()  { printf "\033[2m  %s\033[0m\n" "$*"; }

# 解析单个项目行: 设置 P_SRC P_DST P_ENTRY P_EMOJI P_TITLE P_DESC P_CAT P_TAG
parse_project() {
  IFS='|' read -r P_SRC P_DST P_ENTRY P_EMOJI P_TITLE P_DESC P_CAT P_TAG <<< "$1"
}

# 检查是否被 TARGETS 过滤
targeted() {
  [ ${#TARGETS[@]} -eq 0 ] && return 0
  for t in "${TARGETS[@]}"; do
    [[ "$P_DST" == *"$t"* ]] && return 0
  done
  return 1
}

# 检测站点仓库中的 gitlink（mode 160000 = 子模块引用, 无 .gitmodules 则 Pages 构建 fatal）
check_gitlinks() {
  local found=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local path=$(echo "$line" | awk '{print $4}')
    warn "检测到 gitlink(子模块引用): $path"
    warn "  → 若无 .gitmodules 定义, GitHub Pages 构建会 fatal:"
    warn "     fatal: No url found for submodule path '$path' in .gitmodules"
    warn "  → 修复: git rm --cached $path && rm -rf $path/.git && git add $path"
    found=1
  done < <(git ls-tree HEAD | grep '^160000')
  return $found
}

# ======================= 主流程 =======================
[ -d "$REPO/.git" ] || { echo "ERROR: $REPO 不是 git 仓库, 请先 clone backyes.github.io"; exit 1; }

# 预检: 检测站点仓库中的 gitlink（防止 Pages 构建 fatal）
log "预检: 扫描 gitlink(子模块引用) ..."
if check_gitlinks; then
  ok "预检通过: 未发现 gitlink"
fi

cd "$REPO"
export GIT_AUTHOR_NAME="backyes"; export GIT_AUTHOR_EMAIL="backyes@gmail.com"
export GIT_COMMITTER_NAME="backyes"; export GIT_COMMITTER_EMAIL="backyes@gmail.com"
git -c http.proxy="$PROXY" -c https.proxy="$PROXY" pull --rebase 2>/dev/null || warn "pull 失败, 继续以本地为准"

log "项目清单: ${#PROJECTS[@]} 个 (过滤后: $( for p in "${PROJECTS[@]}"; do parse_project "$p"; targeted && echo x; done | wc -l | tr -d ' ') 个)"
[ "$DRY_RUN" = 1 ] && warn "DRY-RUN 模式, 不写盘不提交"

# ------- 1) 逐个 rsync -------
SYNCED=0
for proj in "${PROJECTS[@]}"; do
  parse_project "$proj"
  targeted || continue
  SRC="$SRC_ROOT/$P_SRC"
  [ -d "$SRC" ] || { warn "源目录不存在, 跳过: $SRC"; continue; }

  if [ "$DRY_RUN" = 1 ]; then
    n=$(rsync -avni "${RSYNC_FILTER[@]}" "$SRC/" "$REPO/$P_DST/" 2>/dev/null | grep -cE '^(send|del|<>|[<>][cf])' || true)
    dim "[dry-run] $P_SRC → $P_DST/  (~$n 项变动)"
    continue
  fi

  mkdir -p "$REPO/$P_DST"
  log "同步: $P_SRC → $P_DST/"
  dim "  入口: $P_DST/$P_ENTRY  |  白名单: html+css+png+jpg+svg+webp+ico"
  # --delete-excluded: 把目标端被排除的目录(raw/logs/.git等)主动清掉
  # (仅 --exclude 不够, 因为被 exclude 的路径 rsync 既不复也不删)
  rsync -a --delete --delete-excluded "${RSYNC_FILTER[@]}" "$SRC/" "$REPO/$P_DST/"
  SYNCED=$((SYNCED+1))
done

# 手写文章源直接存放在 backyes.github.io/posts/ 中, 不再从 toolkit 同步
# build_site.py 会读取 repo 自身的 posts/*.md 并生成 HTML

[ "$DRY_RUN" = 1 ] && { log "dry-run 完成"; exit 0; }

# ------- 2) 构建全部页面 (index/posts/tags + 单篇文章) -------
log "构建全部静态页面 (cards + posts + tags + search) ..."
python3 "$REPO/build_site.py" 2>&1 | sed 's/^/  /'

# ------- 3) 提交 + 推送 -------
cd "$REPO"
git -c http.proxy="$PROXY" -c https.proxy="$PROXY" add -A

CHANGE_COUNT=$(git diff --cached --stat 2>/dev/null | tail -1 | awk '{print $1+$2+$4}' || echo 0)
if [ "$(git diff --cached --stat)" = "" ] && [ "$FORCE_GIT" != 1 ]; then
  ok "无变更, 无需提交 (已同步 $SYNCED 个项目)"
  exit 0
fi

 git -c http.proxy="$PROXY" -c https.proxy="$PROXY" commit -m "sync: 同步研究报告 + Posts/Tags/Search 全页重建 ($SYNCED 个项目)

- 同步源: claude_workspace/* → backyes.github.io/
- 白名单: html + css + png/jpg/svg/webp/io (排除 md/txt/pdf/log/py 等原始素材)
- build_site.py: 重建 index / posts / tags / 单篇文章 / search DB
- Posts 源: posts/*.md (手写洞察)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

ok "已提交 ($CHANGE_COUNT 处变动)"

if [ "$DO_PUSH" = 1 ]; then
  log "推送 origin main ..."
  git -c http.proxy="$PROXY" -c https.proxy="$PROXY" push origin main 2>&1 | tail -3
  ok "推送完成 → https://backyes.github.io"
  dim "(GitHub Pages 首次构建约 1-3 分钟生效)"
else
  dim "--no-push: 尚未推送, 可之后手动 git push origin main"
fi
