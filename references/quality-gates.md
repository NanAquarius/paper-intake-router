# 质量门槛（Quality Gates）

## G1 结构完整性
- 章节结构与论文类型匹配（学位/课程）
- 目录层级清晰且前后一致

## G2 论证有效性
- 每章有明确目标、证据与结论
- 不出现“结论先行但无支撑”

## G3 参考文献可信度
- 关键观点有可追溯来源
- 不确定文献标注“需补充”，禁止编造
- 引用格式与用户规范一致（GB/T 或 APA）

## G4 图表可用性
- 写作前必须产出 `figure-table-plan.json` 与 `figure-table-plan.md`
- 对可程序化图表，必须进一步产出代码脚手架、数据模板或占位表数据
- 交付前必须运行图表引用一致性校验，至少产出 `figure-table-validation.json` 或等价报告
- 若能高置信修正，应进一步产出 `fixed-draft.md` 与 `autofix-report.json`
- 图表标题、编号、正文引用一致
- 图表可读（坐标、图例、单位齐全）
- 图表编号必须由模板或默认编号规则决定，不得在正文阶段临场猜编号
- 若使用按章编号，图表编号必须满足如 `图 1-1` / `表 2-3` 的形式，且同章内连续
- 若使用全局连续编号，图表编号必须满足如 `图 1` / `表 2` / `Figure 1` / `Table 2` 的形式
- 正文中引用的图表编号必须真实存在于 `figure-table-plan.json`
- 图题与表题位置必须符合模板约束；默认规则为“图下表上”

## G5 Final Gate
- final PDF 渲染前必须执行 gate
- 只有以下项可以触发 **hard block**：
  - `missingRequiredInBody`
  - `unexpectedInBody`
  - `duplicateInPlan`
  - `numberingIssues`
- 以下项只作为 **warning**，不单独阻塞 PDF：
  - `missingRecommendedInBody`
  - `missingOptionalInBody`
- 若 gate 阻塞，应先修正草稿，再重新校验，不得跳过

## G6 排版与交付
- PDF 可正常打开、目录跳转正常
- 与用户样例版式（如有）基本一致
- 同步交付可编辑源文件
- 图表产物文件、代码文件、数据文件路径可追溯且不混乱

## 交付前检查清单
- [ ] 必填字段齐全
- [ ] 缺失项已补齐或显式标注默认
- [ ] 引用与参考文献一致
- [ ] 图表文件已打包
- [ ] 图表编号与正文引用一致
- [ ] 图表自动修正已执行（如适用）
- [ ] `missingRequiredInBody` 已清零
- [ ] 无 `unexpectedInBody` / `duplicateInPlan` / `numberingIssues`
- [ ] recommended / optional 缺失已审阅
- [ ] final gate 通过
- [ ] 最终 PDF 生成成功
