---
name: paper-intake-router
description: 论文全流程入口路由器。先收集并分流需求（学位论文/课程论文），再基于可用生态自动选择最合适的写作与交付链路（paper-write、latex-thesis-zh、mineru、zotero-scholar、Quarto、Pandoc、Manubot 等）。适用于“我只给主题，其他你来做”“写论文”“课程论文”“学位论文”“按模板出 PDF”等场景。
---

# Paper Intake Router

把“用户一句话需求”转换为“可执行论文任务单 + 工具链方案 + 下一步动作”。

## Core Workflow

1. **识别类型**：学位论文 / 课程论文 / 未明确。
2. **收集必填项**（一次问全，少打扰）。
3. **评估交付目标**：仅正文 / 含图表 / 最终 PDF / 可复现工程。
4. **选择工具链**：从内置生态中选最稳方案（先可用、再高级）。
5. **选择排版模板**：
   - 用户提供学校模板 / 样例论文 / 官方规范 → 优先采用用户排版参考
   - 未提供 → 从 `paper-template-library/layout/defaults/` 解析默认模板
6. **规划图表与编号**：
   - 先生成 `figure-table-plan.json/.md`
   - 对可程序化图表自动生成代码脚手架、数据模板与输出路径
   - 图、表编号由模板或默认编号规则统一决定
7. **自动修正图表引用与标题**：
   - 对常见误引和标题行进行自动修正
   - 产出 `fixed-draft.md` 与修正报告
8. **校验图表引用一致性**：
   - 在正文草稿或终稿阶段运行图表校验
   - 检查缺失编号、正文误引、重复编号、连续性问题
9. **执行 final gate**：
   - 仅当图表校验通过时，才允许进入最终 PDF 渲染
10. **生成标准任务单**：
   - 人类可读版（Markdown）
   - 机器可读版（JSON）
11. **进入执行模式**：
   - 字段齐全 → 直接进入大纲、文献、图表规划阶段
   - 字段缺失 → 仅追问缺失项，不提前写正文

## Automation

### Step A：先把自然语言解析为 intake JSON

```bash
python3 scripts/parse_intake_text.py \
  --text "用户原始需求文本" \
  --out /tmp/intake-payload.json
```

### Step B：再标准化为任务单

```bash
python3 scripts/build_task_sheet.py \
  --input /tmp/intake-payload.json \
  --out-json /tmp/paper-task.json \
  --out-md /tmp/paper-task.md
```

### Step C：生成图表规划与代码脚手架

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/paper-task.json \
  --evidence-pack /tmp/writing-evidence-pack.json \
  --citation-plan /tmp/citation-plan.json \
  --out-json /tmp/figure-table-plan.json \
  --out-md /tmp/figure-table-plan.md

python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-table-plan.json \
  --base-dir /tmp/paper-artifacts
```

### Step D：自动修正草稿中的图表引用与标题

```bash
python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-table-plan.json \
  --draft /tmp/draft.md \
  --out /tmp/fixed-draft.md \
  --report /tmp/autofix-report.json \
  --citation-mode support-note  # or inline-marker / internal-anchor
```

### Step E：图表引用校验 + final gate

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-table-plan.json \
  --draft /tmp/fixed-draft.md \
  --out-json /tmp/figure-table-validation.json \
  --out-md /tmp/figure-table-validation.md

python3 scripts/enforce_final_gate.py \
  --validation /tmp/figure-table-validation.json \
  --out /tmp/final-gate.json
```

脚本能力：
- 自动补默认值（格式规范、字数、排版参考策略）
- 生成 `missingFields` 与 `readyToExecute`
- 自动推荐 Playbook（A/B/C）
- 自动解析默认排版模板并写入 `selectedLayoutTemplate`
- 自动生成图表规划 `figure-table-plan.json/.md`
- 图表规划可联动 `writing-evidence-pack` 与 `citation-plan`，为每个图表项补充 supportEvidence 与 citationHint
- 对可程序化图表自动生成 Python 脚手架、CSV 模板与产物路径
- 自动修正常见图表误引与标题行
- 支持 `support-note`、`inline-marker` 与 `internal-anchor` 三种引用输出模式
- 自动校验正文中的图表编号与规划是否一致
- 在 final PDF 前执行强制 gate（仅 `required` 缺失和结构性问题触发 hard block）
- 兼容中英混合输入（如“学位论文 / thesis”“硕士 / master”）
- 支持自然语言解析（主题/字数/规范/排版参考）
- 输出统一任务单格式，便于后续子流程接入

## Required Fields

### 学位论文（必填）
- 学位层级（本科 / 硕士 / 博士 / 其他）
- 学科方向
- 主题
- 格式规范（GB/T 7714 / APA / 学校模板）
- 字数

### 课程论文（必填）
- 课程名称
- 主题
- 格式规范
- 字数

### 排版参考（强烈建议）
- 权威论文样例（文件或链接）
- 若未提供：标记“使用默认模板”

## Rules

- 不提前写正文：必填项未齐时只做收集与补齐。
- 缺失项一次问全，避免轮询式碎问。
- 用户只给主题时，强制触发本技能。
- 用户说“你定”时，允许采用默认值并标记为“默认”。
- 任何“最终 PDF”请求都要明确排版基准（用户样例或默认模板）。
- 用户样例优先级高于默认模板。
- `paper-template-library/structure/` 只能作为结构参考，不可直接冒充默认排版模板。
- 若论文需要图表，不要只在正文中写占位句；应先产出图表规划，再决定是否生成代码和数据模板。
- 图、表编号必须由模板或默认编号规则统一决定，不允许写作阶段临场乱编号。
- 正文中出现的图表编号必须真实存在于 `figure-table-plan.json`。
- 自动修正器只修“高置信度”错误；拿不准的地方必须保留并交给校验报告。
- 若 final gate 未通过，不得直接进入终版 PDF 交付。
- `required` 图表缺失属于 hard block；`recommended` / `optional` 图表缺失只记 warning，不单独拦截 PDF。

## Defaults

- 中文格式规范默认：GB/T 7714
- 英文格式规范默认：APA 7
- 字数默认：课程论文 5000；学位论文 本科 15000 / 硕士 25000
- 排版默认：从 `paper-template-library/layout/defaults/` 中匹配
- 中文学位论文图表默认按章编号：`图 1-1` / `表 2-3`
- 英文论文图表默认全局编号：`Figure 1` / `Table 2`
- 图题默认在下，表题默认在上

## Execution Chain

当任务单 `readyToExecute=true` 时，先探测能力，再生成下一步执行链：

```bash
python3 scripts/detect_capabilities.py > /tmp/paper-caps.json
python3 scripts/build_reference_stage_paths.py \
  --base-dir /tmp/paper-references \
  --out-json /tmp/paper-reference-paths.json
python3 scripts/next_actions.py \
  --task /tmp/paper-task.json \
  --caps /tmp/paper-caps.json \
  --out /tmp/paper-next-actions.json
```

执行逻辑：
- Playbook A → 快速初稿链（outline → figure_table_plan → figure_table_codegen → draft → validate → autofix → revalidate）
- Playbook B → 标准交付链（outline → paper_search → reference_pack → evidence_pack → citation_plan → sample_parse → figure_table_plan → figure_table_codegen → write → validate → autofix → revalidate → final_gate → render_pdf）
- Playbook C → 可复现链（outline → paper_search → reference_pack → evidence_pack → citation_plan → figure_table_plan → figure_table_codegen → write → validate → autofix → revalidate → final_gate → reproducible-pipeline）

## References to Load On Demand

- 字段采集与问卷：`references/intake-checklist.md`
- 生态候选与优先级：`references/ecosystem-shortlist.md`
- 三档执行方案：`references/pipeline-playbooks.md`
- 质量门槛与交付检查：`references/quality-gates.md`
- 图表与编号规范：`references/figure-table-rules.md`
- 图表规划模板：`references/figure-table-plan-template.json`
- 图表规划生成脚本：`scripts/build_figure_table_plan.py`
- 图表代码脚手架生成脚本：`scripts/generate_figure_table_codegen.py`
- 图表引用校验脚本：`scripts/validate_figure_table_refs.py`
- 图表自动修正脚本：`scripts/autofix_figure_table_refs.py`
- final gate 脚本：`scripts/enforce_final_gate.py`
- 当前能力边界：`references/capability-boundaries.md`
- 排版模板库索引：`../../paper-template-library/index.md`
- 排版模板 schema：`../../paper-template-library/schemas/layout-template.schema.json`
