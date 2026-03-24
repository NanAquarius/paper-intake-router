# 论文生态候选清单（基于近期检索）

> 说明：以下为已检索到且可用于组合的候选，不等于全部自动安装。优先采用“可用且稳”的组合。

## 1) SkillHub / ClawHub 侧（Skill 级）

### 核心写作
- `xstongxue/best-skills/paper-write`
  - 用途：大纲审核、章节仿写、润色、去 AI、翻译、结构化提取
  - 观察：在论文写作类中活跃度高（SkillHub 星标较高）

### 中文学位论文排版
- `bahayonghang/academic-writing-skills/latex-thesis-zh`
  - 用途：中文学位论文 LaTeX 规范化

### 文档解析 / 文献管理
- `openclaw/skills/mineru`
  - 用途：PDF/Word/PPT/图片解析到结构化文本
- `openclaw/skills/zotero-scholar`
  - 用途：文献入 Zotero 库，便于引用管理

### 备选（按需）
- `majiayu000/claude-skill-registry/latex-document-writer`
- `WILLOSCAR/research-units-pipeline-skills/thesis-source-role-mapper`

## 2) GitHub 工具链侧（工程级）

### 强推荐
- `academic-paper-search`
  - 作用：参考论文检索；按 OpenAlex / Semantic Scholar / Research Papers MCP 分工返回 DOI、arXiv、PDF、citation 元数据
- `jgm/pandoc`
  - 作用：多格式转换、最终文档编译基石
- `quarto-dev/quarto-cli`
  - 作用：可复现文档（代码 + 图 + 文）与科学写作发布
- `manubot/manubot`
  - 作用：自动化手稿、引用与科研协作流程

### 方法参考
- `Wookai/paper-tips-and-tricks`
  - 作用：LaTeX + 图表生产实践与组织方式参考

## 路由原则

1. 用户要“快” → `paper-write` + 快速模板导出
2. 用户要“规范 PDF + 图表” → `paper-write + mineru + zotero-scholar + Quarto/Pandoc`
3. 用户要“可复现 + 长线维护” → 在 2 的基础上加入 Manubot/CI

## 注意

- 优先使用当前环境已安装、已可执行的组件。
- 对用户透明说明：哪些是已启用，哪些是可选增强。
