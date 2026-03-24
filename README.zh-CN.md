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

## 核心概念

### Task sheet

用于统一描述论文任务，包括：

- 论文类型
- 学位层级
- 主题
- 引用风格
- 目标字数
- 版式模板选择

### Figure/table plan

用于提前决定：

- 需要哪些图表
- 编号规则
- 代码 / 数据 / 输出路径
- claim type
- 支撑证据与 citation hint

### 统一引用层

项目支持三种引用输出模式：

- `support-note`
- `inline-marker`
- `internal-anchor`

其中最关键的是 `internal-anchor`。因为它能让：

- 图表说明句
- 普通正文段
- 方法 / 实验结论句

最终都走同一套 citation rendering chain。

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

## 示例

仓库里附带了最小示例：

- `examples/intake.json`
- `examples/draft.md`
- `examples/reference-pack.json`

如果你想快速验活，可以直接看：

- `scripts/smoke_test_pipeline.py`

## License

MIT
