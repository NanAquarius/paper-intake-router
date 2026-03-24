[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

> 一个面向智能代理的论文工作流引擎，覆盖 intake、证据组织、图表规划、引用对齐与模板感知终稿渲染。

`paper-intake-router` 不是单纯的“论文文本生成器”，而是一个更偏工作流层的内核。
它适合那些不满足于“生成几段文字”，而希望代理真正管理整条论文生产流程的场景。

它重点处理这些问题：

- 把原始论文需求归一化成结构化任务单
- 组织文献、证据包和引用计划
- 在写正文前先规划图表
- 保持图表编号、正文引用和引用渲染的一致性
- 在不同模板和风格下稳定输出终稿引用格式

## 核心亮点

- **Intake → task sheet** 归一化
- **reference shortlist / screening / retry / reference pack** 工作流
- **writing evidence pack + citation plan** 生成
- **图表规划、校验与自动修正**
- **普通正文段与图表说明句统一走 citation layer**
- **模板感知的终稿引用渲染**

## 适合谁用

这个项目适合：

- academic writing agents
- thesis workflow assistants
- paper-production pipelines
- citation / figure automation systems

## 仓库结构

```text
paper-intake-router/
├── SKILL.md
├── scripts/
├── references/
├── paper-template-library/
├── examples/
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## 运行要求

### 基础环境

- Python 3.10+
- Linux / macOS / WSL 或 Windows PowerShell

### 可选依赖

按你使用的工作流不同，可能还需要：

- `quarto`
- `pandoc`
- `xelatex` 或其它 LaTeX 工具链
- `matplotlib`（用于本地图表脚手架渲染）

## 基础环境准备

### Linux / macOS / WSL

```bash
git clone https://github.com/NanAquarius/paper-intake-router.git
cd paper-intake-router
chmod +x scripts/install.sh
./scripts/install.sh
source .venv/bin/activate
```

### Windows PowerShell

```powershell
git clone https://github.com/NanAquarius/paper-intake-router.git
cd paper-intake-router
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
.\.venv\Scripts\Activate.ps1
```

### 手动安装（跨平台）

如果你不想用安装脚本，也可以手动安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
```

Windows 下对应：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-minimal.txt
```

### 安装脚本会做什么

安装脚本默认只做最小安装：

- 创建本地虚拟环境
- 升级 `pip`
- 安装 `requirements-minimal.txt`

这样可以保证本地的规划 / 校验 / 引用渲染链可以直接跑起来。

如果你还需要更完整的 PDF / 文档渲染能力，请额外安装 `quarto`、`pandoc`、LaTeX 工具链等可选依赖。

## API Key / 外部服务说明

这个仓库里的**本地核心流程**本身不强制要求 API Key。

也就是说，下面这些环节可以本地直接跑：

- task sheet 生成
- 图表规划
- 图表自动修正
- 引用渲染
- smoke test

但如果你要启用**文献检索、证据包构建、外部学术搜索**，就很可能依赖你自己的上游工具或 API：

例如：

- OpenAlex / Semantic Scholar / 论文搜索类 MCP
- Tavily / Exa / 其他搜索服务
- 外部 PDF / 文档解析服务

所以最稳的做法是：

- 在你自己的部署文档里明确写清楚用了哪套搜索后端
- 在需要外部凭据的步骤里，明确提醒使用者先完成配置

## 快速开始

### 1）生成 task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json
```

### 2）生成图表规划

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json
```

### 3）把图表说明句修成 internal anchor 模式

```bash
python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft examples/draft.md \
  --citation-mode internal-anchor \
  --out /tmp/fixed.md
```

### 4）渲染终稿引用

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --style 'GB/T 7714' \
  --out /tmp/final.md
```

## 更详细的使用方法

### A. Intake 归一化

如果你已经有一个规范化或半规范化的论文需求 JSON，可以直接用：

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

这一层会决定：

- 论文类型
- 学位层级
- 主题
- 引用风格
- 目标字数
- 默认版式模板选择

### B. 图表规划

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json \
  --out-md /tmp/figure-plan.md
```

可选输入：

- `--evidence-pack`
- `--citation-plan`

提供这些输入后，图表规划会变成：

- evidence-aware
- citation-aware

### C. 图表代码脚手架

```bash
python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-plan.json \
  --base-dir /tmp/paper-artifacts
```

这一层会生成：

- 代码脚手架
- 占位 CSV 数据
- 图表 / 表格输出路径

### D. 图表引用校验

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --out-json /tmp/figure-validation.json \
  --out-md /tmp/figure-validation.md
```

它会检查：

- 必需图表是否在正文出现
- 正文是否引用了计划外的图表
- 编号是否连续
- 图表标签是否重复

### E. 图表自动修正模式

`autofix_figure_table_refs.py` 支持三种引用输出模式：

- `support-note`
  - 更适合草稿阶段
  - 会生成“可结合 xxx 进一步支撑”这类说明

- `inline-marker`
  - 更适合半终稿阶段
  - 会直接写可见 marker，例如 `[2]`

- `internal-anchor`
  - 最适合完整自动化链
  - 会写成 `[CITE:baseline comparison|lee2024benchmark]`
  - 让图表说明句和普通正文共用同一套最终引用渲染链

示例：

```bash
python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --citation-mode internal-anchor \
  --out /tmp/fixed.md \
  --report /tmp/autofix-report.json
```

### F. 终稿引用渲染

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --style 'APA' \
  --out /tmp/final.md
```

可选输入：

- `--citation-plan`
- `--citation-profile-json`

如果你的版式模板里定义了 citation rendering profile，就应该把它传进来，这样最终引用层才能与模板风格保持一致。

## 典型输出产物

根据你跑的链路不同，项目可能会生成这些中间/最终文件：

- `task.json` / `task.md`
- `references-shortlist.json` / `.md`
- `reference-screening.json` / `.md`
- `reference-pack.json` / `.md`
- `writing-evidence-pack.json` / `.md`
- `citation-plan.json` / `.md`
- `figure-table-plan.json` / `.md`
- 代码 / CSV / 图表 / 表格产物
- fixed draft
- final rendered draft

## 示例

仓库里附带了最小示例：

- `examples/intake.json`
- `examples/draft.md`
- `examples/reference-pack.json`

如果你想快速验活，可以直接运行：

- `scripts/smoke_test_pipeline.py`

## 这个项目是什么

更准确地说，它是：

- **论文工作流引擎**
- **格式与引用稳定器**
- **面向智能代理的 draft-to-deliverable orchestration layer**

## 这个项目不是什么

它**不保证**：

- 在没有官方模板原件时完全符合学校 / 期刊规范
- 实验结果的真实性
- 无需人工复核即可直接投稿 / 送审
- 自动发明可信数据、结果或文献

当前能力边界见：

- `references/capability-boundaries.md`

## License

MIT
