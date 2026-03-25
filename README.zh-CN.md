[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

> OpenClaw 优先的论文工作流内核，用来把论文需求推进成结构化、证据感知、图表感知、引用一致的可交付产物。

`paper-intake-router` 是一个 **面向 OpenClaw 的论文工作流 Skill / engine**。
它的重点不是“帮你多写几段字”，而是把学术写作里真正容易失控的那一层流程稳定下来。

## 为什么做这个项目

很多 AI 写作工具能生成段落，但在论文任务里，真正难的是这些环节：

- 把模糊需求 intake 成结构化任务单
- 分清原始材料和弱二手材料
- 在写作前组织 evidence 与 citation
- 在正文写完前先把图表规划好
- 让图表编号、正文引用、终稿引用层保持一致
- 让最终输出跟模板 / citation rendering profile 对齐

这个项目重点补的，就是这层“论文工作流引擎”。

## 它能做什么

### Intake 和任务路由
- 把需求归一化成 task sheet
- 推断论文类型、语言、风格、交付模式等默认值
- 在没有官方模板时选择默认版式模板

### 文献与引用工作流
- reference shortlist
- screening 和 retry 检索链
- reference pack
- writing evidence pack
- 按章节 / claim type 组织 citation plan

### 图表工作流
- 在写作前先生成 figure/table plan
- 从模板逻辑推导编号规则
- 生成代码 / CSV / 产物脚手架
- 校验图表引用与编号一致性
- 自动修正图表说明句与引用模式

### 统一引用层
- 普通正文段和图表说明句共用同一套 citation layer
- 支持 `support-note`、`inline-marker`、`internal-anchor`
- 支持 GB/T 7714 与 APA 风格渲染
- 支持模板感知的 citation rendering profile

## OpenClaw 优先兼容说明

这个仓库首先是为 **OpenClaw** 生态设计的。

它也可以被迁移到其它 agent / CLI 环境，比如 **Claude Code**、**OpenCode** 或类似 coding-agent runtime，但**不保证开箱即用**。

如果你要迁移到这些环境，通常需要自己调整：

- runtime 假设
- 工作区 / 路径约定
- 上游检索与证据后端
- 工具调用和命令编排方式

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

## 安装

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

### 手动安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
```

## API Key / 外部服务说明

本地核心链本身**不强制要求 API Key**。例如这些步骤可以纯本地运行：

- task sheet 生成
- 图表规划
- 本地图表校验与自动修正
- 引用渲染
- smoke test

但如果你要跑完整的文献检索 / evidence-building 流水线，通常会受益于或依赖外部服务。常见例子包括：

- Semantic Scholar API
  - 官方入口：<https://www.semanticscholar.org/product/api>
  - 教程：<https://www.semanticscholar.org/product/api/tutorial>
  - 文档：<https://api.semanticscholar.org/api-docs/>
- OpenAlex
- Tavily / Exa / 其他检索服务

建议在你自己的部署文档里明确写清楚：

- 用了哪个上游提供方
- 是否要求 API Key
- 应该去哪里申请
- 哪些步骤依赖这些外部凭据

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

### 3）把图表说明句转成 internal anchor

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

### 生成标准 task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

### 生成图表规划

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json \
  --out-md /tmp/figure-plan.md
```

可选输入：

- `--evidence-pack`
- `--citation-plan`

### 生成图表代码脚手架

```bash
python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-plan.json \
  --base-dir /tmp/paper-artifacts
```

### 校验图表引用

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --out-json /tmp/figure-validation.json \
  --out-md /tmp/figure-validation.md
```

### 按 profile 渲染最终引用

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --citation-profile-json /tmp/profile.json \
  --style 'APA' \
  --out /tmp/final.md
```

## 典型产物

根据你走的链路不同，项目会生成这些中间 / 最终文件：

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

## 示例与验活

仓库附带的最小示例：

- `examples/intake.json`
- `examples/draft.md`
- `examples/reference-pack.json`
- `examples/layout-samples/README.md`

最小验活入口：

- `scripts/smoke_test_pipeline.py`

## 它是什么

更准确地说，它是：

- **论文工作流引擎**
- **格式与引用稳定器**
- **面向 Agent 的 draft-to-deliverable orchestration layer**

## 它不是什么

它**不保证**：

- 在没有官方模板原件时完全符合学校 / 期刊规范
- 实验结果的真实性
- 无需人工复核即可直接投稿 / 送审
- 自动发明可信数据、结果或参考文献
- 默认附带可再分发的论文 PDF 排版样张

当前边界见：

- `references/capability-boundaries.md`

## License

MIT
