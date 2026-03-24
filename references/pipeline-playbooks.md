# 执行手册（Playbooks）

## Playbook A：快速初稿（当日可交）

适用：时间紧，只要结构完整、表达规范的初稿。

步骤：
1. 采集字段并生成任务单
2. 先出三级大纲（按学位/课程类型）
3. 分章写作（先方法/案例，再绪论与摘要）
4. 一轮润色 + 去 AI 痕
5. 导出可编辑文稿（必要时转 PDF）

交付：
- 初稿正文
- 参考文献草单
- 待补证据点列表

---

## Playbook B：标准交付（推荐）

适用：要“像模像样”的完整论文包。

步骤：
1. 采集字段并锁定格式规范
2. 解析用户样例论文（若提供）提取版式特征
3. 使用 `academic-paper-search` 做文献检索与清单整理（主题词、核心文献、近三年增量；尽量带 DOI / arXiv / PDF）
4. 产出 `references-shortlist.json/.md`
5. 做一次 paper screening：筛掉重复、弱匹配、低相关结果，产出 `reference-screening.json/.md`
   - 默认最低门槛：核心文献目标 8 篇；近三年文献至少 3 篇；survey 至少 1 篇；method 至少 1 篇；若全是预印本需显式告警；若存在经典论文可用，优先保留 canonical 项
6. 若 screening 告警未清除，生成 `query-reformulation.json`，给出下一轮更宽/更窄/补 survey/补 recent 的检索建议
7. 基于 `query-reformulation.json` 生成 `retry-plan.json`；若 `retryNeeded=true`，执行一次补检索并重新进入 screening
   - 产出：`references-shortlist-round2.json/.md`
   - 若二轮后仍有 `survey count below minimum`，停止自动重搜，转入 `survey-gap-handling` 记录与人工确认分支
8. 使用 `zotero-scholar` 做入库与引用管理（若可用）
9. 分章写作 + 图表位点设计
10. 图表生成（数据表、对比图、流程图）
11. 统一引用与格式（GB/T 或 APA）
12. Quarto/Pandoc 编译 PDF

交付：
- `paper.pdf`
- 可编辑源文件（md/tex/docx）
- 图表资源（png/svg/csv）
- 参考文献文件（bib 或格式化列表）

---

## Playbook C：可复现科研版

适用：需要可复现实验、可追踪迭代和长期维护。

步骤：
1. 在 Playbook B 基础上建立项目结构
2. 固化数据处理与出图脚本
3. 引入 Manubot/CI 自动构建
4. 每次更新自动重编译 PDF 与版本归档

交付：
- 标准交付包 + 可复现脚本 + 构建配置

---

## 最小追问模板（字段未齐时）

请一次性补齐以下信息：
1) 论文类型（学位/课程）
2) 学位层级或课程名称
3) 学科方向（学位论文必填）
4) 主题
5) 格式规范（GB/T 7714 或 APA 或学校模板）
6) 字数
7) 是否有权威论文样例用于排版（有请上传）
