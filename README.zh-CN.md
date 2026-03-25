[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

![License](https://img.shields.io/badge/license-MIT-green)
![OpenClaw-first](https://img.shields.io/badge/OpenClaw-first-4f46e5)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Workflow](https://img.shields.io/badge/type-workflow%20core-111827)

> 🧭 *把模糊论文需求推进成结构化、证据感知、图表感知、引用一致的可交付产物。*

`paper-intake-router` 是一个 **论文 workflow core**，不是普通 AI 论文写作器。

它解决的重点不是“多写几段字”，而是把论文任务里真正容易失控的那层流程收稳：需求归一化、任务单生成、图表规划、引用约束、产物组织，以及面向最终交付的渲染链路。

## ✨ 它适合做什么

当你需要 agent 或本地工作流去做这些事时，它就合适：

- 把模糊论文需求归一化成结构化 task sheet
- 在写正文前先决定下一阶段该做什么
- 在草稿漂掉之前先把 figure/table 规划好
- 保持图表编号和正文引用一致
- 用稳定规则渲染终稿引用
- 把中间产物收进一个任务工作区里

## 🚫 它不适合承诺什么

它 **不等于**：

- 没有官方模板原件也能 100% 满足学校规范
- 自动保证实验结果真实有效
- 不经人工复核就能直接投稿或送审
- 凭空生成可信参考文献和数据
- 一次性“完美写完整篇论文”

如果这些边界对你很关键，建议尽早看 [`references/capability-boundaries.md`](./references/capability-boundaries.md)。

## ⚡ 60 秒上手

**输入：** [`examples/intake.json`](./examples/intake.json)

**执行：**

```bash
python3 scripts/paper_router.py build-task -- \
  --input examples/intake.json \
  --out-json /tmp/task.json

python3 scripts/paper_router.py init-workspace -- \
  --base-dir /tmp/paper-runs \
  --task /tmp/task.json \
  --out-json /tmp/workspace.json

python3 scripts/paper_router.py build-figure-plan -- \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json

python3 scripts/paper_router.py smoke-test
```

**输出：**

- `/tmp/task.json`
- `/tmp/workspace.json`
- `/tmp/figure-plan.json`
- 一条可本地验活、最终能渲染出带引用草稿的 smoke test 链路

如果你更喜欢直接调用底层脚本，也可以继续用 `scripts/` 目录下的原始命令。

## 🧩 按使用环境进入

### For OpenClaw

这个仓库首先是为 OpenClaw 生态设计的。

如果你要的是一个放在 OpenClaw Skill 背后的论文工作流内核，而不是单纯的文本生成器，这就是它的目标定位。

### For local CLI

这套核心链路可以纯本地跑起来，依赖只是 Python。

本地链路覆盖 task normalize、task workspace init、figure/table planning、validation、autofix 和 citation rendering。

### For other agent runtimes

它可以迁移到 Claude Code、OpenCode 或类似 agent runtime，但 **不保证开箱即用**。

通常要自己适配：

- runtime 假设
- workspace / 路径约定
- 上游检索与证据后端
- 工具调用与命令编排方式

## 🗺 Workflow artifact map

核心产物流大致是这样：

```text
intake.json
  → task.json
  → workspace.json
  → figure-plan.json
  → fixed.md / validation.json
  → final.md
```

每个产物大致代表：

- `task.json`：归一化后的论文任务单、默认值和路由信息
- `workspace.json`：该任务的目录清单，统一管理 drafts、figures、tables、references 和 outputs
- `figure-plan.json`：图表规划、编号规则和 codegen 目标
- `validation.json`：草稿里的图表引用是否与 figure plan 一致
- `final.md`：内部引用标记被解析后的终稿草稿

## 🔧 核心能力

### Intake 和任务路由

- 把需求归一化成结构化 task sheet
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

## 🚀 安装

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

## 🛠 统一 CLI

仓库里现在带了一层薄封装 CLI，用来承接最常见的 workflow 命令：

```bash
python3 scripts/paper_router.py smoke-test
python3 scripts/paper_router.py build-task -- --input examples/intake.json --out-json /tmp/task.json
python3 scripts/paper_router.py init-workspace -- --base-dir /tmp/paper-runs --task /tmp/task.json --out-json /tmp/workspace.json
python3 scripts/paper_router.py build-figure-plan -- --task /tmp/task.json --out-json /tmp/figure-plan.json
```

它不替代底层脚本，只是让常用路径更容易发现，也更容易写进 README。

## 🧰 更详细的使用方法

### 生成标准 task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

### 初始化任务工作区

```bash
python3 scripts/init_task_workspace.py \
  --base-dir /tmp/paper-runs \
  --task /tmp/task.json \
  --out-json /tmp/workspace.json
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

## 🔑 外部服务

本地核心链本身 **不强制要求 API Key**，这些步骤可以纯本地运行：

- task sheet 生成
- 图表规划
- 本地图表校验与自动修正
- 引用渲染
- smoke test

但完整的文献检索 / evidence-building 链通常会受益于或依赖外部服务，比如：

- Semantic Scholar API
- OpenAlex
- Tavily / Exa / 其他检索服务

建议你在自己的部署文档里写清楚：用了哪些上游、哪些步骤依赖它们、是否需要 API Key。

## 🧪 示例与验活

仓库附带的最小示例：

- [`examples/intake.json`](./examples/intake.json)
- [`examples/draft.md`](./examples/draft.md)
- [`examples/reference-pack.json`](./examples/reference-pack.json)
- [`examples/layout-samples/README.md`](./examples/layout-samples/README.md)

最小验活入口：

```bash
python3 scripts/smoke_test_pipeline.py
python3 scripts/paper_router.py smoke-test
```

当前 smoke test 覆盖：

- task 归一化
- 任务工作区初始化
- 图表规划生成
- 图表引用自动修正
- 图表引用校验
- 终稿引用渲染

## 🗂 仓库结构

```text
paper-intake-router/
├── SKILL.md
├── scripts/
├── references/
├── paper-template-library/
├── examples/
├── paper_intake_router/
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## License

MIT
