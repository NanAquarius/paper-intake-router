#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def _load_caps(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _skill_ok(caps: dict, key: str) -> bool:
    return bool(caps.get("skills", {}).get(key))


def _tool_ok(caps: dict, key: str) -> bool:
    return bool(caps.get("toolchains", {}).get(key))


def build_actions(task: dict, caps: dict | None = None) -> dict:
    caps = caps or {}
    ready = bool(task.get("readyToExecute"))
    playbook = task.get("recommendedPlaybook", "A")
    paper_type = task.get("paperType", "unknown")

    if not ready:
        missing = task.get("missingFields", [])
        ask = "请一次性补齐以下信息：" + "、".join(missing) if missing else "请补齐必要信息。"
        return {
            "mode": "intake",
            "readyToExecute": False,
            "assistantMessage": ask,
            "actions": [
                {"step": 1, "type": "ask_user", "name": "collect_missing_fields", "missingFields": missing}
            ]
        }

    writer_skill = "paper-write" if _skill_ok(caps, "paper_write") else "paper-intake-router"
    paper_search_skill = "academic-paper-search" if _skill_ok(caps, "academic_paper_search") else ("zotero-scholar" if _skill_ok(caps, "zotero_scholar") else "manual-paper-search")
    ref_skill = "zotero-scholar" if _skill_ok(caps, "zotero_scholar") else "manual-reference-pack"
    parse_skill = "mineru" if _skill_ok(caps, "mineru") else "manual-sample-parse"

    pdf_chain = "quarto+pandoc" if (_tool_ok(caps, "quarto") and _tool_ok(caps, "pandoc")) else (
        "pandoc" if _tool_ok(caps, "pandoc") else (
            "xelatex" if _tool_ok(caps, "xelatex") else "manual"
        )
    )

    repro_chain = "manubot+quarto+pandoc" if (_tool_ok(caps, "manubot") and _tool_ok(caps, "quarto") and _tool_ok(caps, "pandoc")) else pdf_chain

    validation_tail = [
        {"step": None, "type": "route", "name": "validate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": "读取 figure-table-plan.json 与草稿正文；检查缺失编号、正文误引、重复编号与连续性问题，产出 figure-table-validation.json/.md"},
        {"step": None, "type": "route", "name": "autofix_figure_table_refs", "targetSkill": "paper-intake-router", "notes": "读取 figure-table-plan.json 与草稿正文；自动修正一部分图表编号引用和标题行，产出 fixed-draft.md 与 autofix-report.json"},
        {"step": None, "type": "route", "name": "revalidate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": "对 fixed-draft.md 再次运行图表校验；若仍有 unexpectedInBody / duplicateInPlan / numberingIssues，则视为阻塞项"},
        {"step": None, "type": "route", "name": "enforce_final_gate", "targetSkill": "paper-intake-router", "notes": "读取 figure-table-validation.json；若存在阻塞项则禁止进入 final PDF 渲染"},
    ]

    if playbook == "A":
        chain = [
            {"step": 1, "type": "route", "name": "outline", "targetSkill": writer_skill, "notes": "先出三级大纲并确认"},
            {"step": 2, "type": "route", "name": "figure_table_plan", "targetSkill": "paper-intake-router", "notes": "根据任务单生成 figure-table-plan.json/.md，预先锁定图表需求与编号规则"},
            {"step": 3, "type": "route", "name": "figure_table_codegen", "targetSkill": "paper-intake-router", "notes": "对可程序化图表生成代码脚手架、CSV 模板与输出路径"},
            {"step": 4, "type": "route", "name": "draft_chapters", "targetSkill": writer_skill, "notes": "按章节产出初稿，正文引用图表时必须使用规划中的编号"},
            {"step": 5, "type": "route", "name": "validate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[0]["notes"]},
            {"step": 6, "type": "route", "name": "autofix_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[1]["notes"]},
            {"step": 7, "type": "route", "name": "revalidate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[2]["notes"]},
            {"step": 8, "type": "route", "name": "polish_anti_aigc", "targetSkill": writer_skill, "notes": "润色+去AI痕"}
        ]
    elif playbook == "B":
        chain = [
            {"step": 1, "type": "route", "name": "outline", "targetSkill": writer_skill, "notes": "先出三级大纲并确认"},
            {"step": 2, "type": "route", "name": "paper_search", "targetSkill": paper_search_skill, "notes": "检索核心参考论文；读取 task sheet，写出 references-shortlist.json 与 references-shortlist.md"},
            {"step": 3, "type": "route", "name": "paper_screen", "targetSkill": "paper-intake-router", "notes": "读取 references-shortlist.json；筛掉弱匹配/重复/低相关结果；写出 reference-screening.json 与 reference-screening.md"},
            {"step": 4, "type": "route", "name": "query_reformulation", "targetSkill": "paper-intake-router", "notes": "若 screening 出现 core/recent/survey/method 不达标告警，则生成 query-reformulation.json"},
            {"step": 5, "type": "route", "name": "retry_plan", "targetSkill": "paper-intake-router", "notes": "读取 query-reformulation.json；生成 retry-plan.json，决定是否需要二次检索"},
            {"step": 6, "type": "route", "name": "paper_search_retry", "targetSkill": paper_search_skill, "notes": "若 retry-plan.json 中 retryNeeded=true，则按 queries 执行一次补检索，再回到 screening"},
            {"step": 7, "type": "route", "name": "reference_pack", "targetSkill": ref_skill, "notes": "读取 reference-screening.json；将筛选后的核心文献入库/格式化，并写出 reference-pack.json/.md"},
            {"step": 8, "type": "route", "name": "evidence_pack", "targetSkill": "paper-intake-router", "notes": "读取 reference-pack.json；生成 writing-evidence-pack.json/.md，按章节与论点整理写作证据"},
            {"step": 9, "type": "route", "name": "citation_plan", "targetSkill": "paper-intake-router", "notes": "读取 writing-evidence-pack.json；生成 citation-plan.json/.md，按章节与 claimType 规划推荐引用与 inline marker"},
            {"step": 10, "type": "route", "name": "sample_parse", "targetSkill": parse_skill, "notes": "解析用户排版样例并提取版式特征"},
            {"step": 11, "type": "route", "name": "figure_table_plan", "targetSkill": "paper-intake-router", "notes": "读取任务单与 writing-evidence-pack.json；生成 figure-table-plan.json/.md，严格锁定图表编号与正文引用格式"},
            {"step": 12, "type": "route", "name": "figure_table_codegen", "targetSkill": "paper-intake-router", "notes": "对可程序化图表生成代码脚手架、CSV 模板、占位表数据与输出路径"},
            {"step": 13, "type": "route", "name": "chapter_prompt_pack", "targetSkill": "paper-intake-router", "notes": "读取 writing-evidence-pack.json 与 citation-plan.json；生成 chapter-writing-pack.json/.md，作为分章写作提示包"},
            {"step": 14, "type": "route", "name": "write_main", "targetSkill": writer_skill, "notes": "读取 chapter-writing-pack.json；完成正文草稿，段落可用 [claimType] 前缀标识论点类型；图表引用必须与 figure-table-plan.json 一致"},
            {"step": 15, "type": "route", "name": "validate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[0]["notes"]},
            {"step": 16, "type": "route", "name": "autofix_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[1]["notes"]},
            {"step": 17, "type": "route", "name": "revalidate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[2]["notes"]},
            {"step": 18, "type": "route", "name": "enforce_final_gate", "targetSkill": "paper-intake-router", "notes": validation_tail[3]["notes"]},
            {"step": 19, "type": "route", "name": "inject_inline_citations", "targetSkill": "paper-intake-router", "notes": "读取 citation-plan.json；对带 [claimType] 标识的草稿段落插入内部引用锚点，产出 cited-draft.md"},
            {"step": 20, "type": "route", "name": "render_final_citations", "targetSkill": "paper-intake-router", "notes": "读取 cited-draft.md 与 reference-pack.json；按目标样式渲染终版正文引用（先支持 GB/T 数字序号与 APA inline）"},
            {"step": 21, "type": "route", "name": "render_pdf", "targetToolchain": pdf_chain, "notes": "统一排版并导出PDF；仅允许在 final gate 通过后执行"}
        ]
    else:
        chain = [
            {"step": 1, "type": "route", "name": "outline", "targetSkill": writer_skill, "notes": "先出三级大纲并确认"},
            {"step": 2, "type": "route", "name": "paper_search", "targetSkill": paper_search_skill, "notes": "检索核心参考论文；读取 task sheet，写出 references-shortlist.json 与 references-shortlist.md"},
            {"step": 3, "type": "route", "name": "paper_screen", "targetSkill": "paper-intake-router", "notes": "读取 references-shortlist.json；筛掉弱匹配/重复/低相关结果；写出 reference-screening.json 与 reference-screening.md"},
            {"step": 4, "type": "route", "name": "query_reformulation", "targetSkill": "paper-intake-router", "notes": "若 screening 出现 core/recent/survey/method 不达标告警，则生成 query-reformulation.json"},
            {"step": 5, "type": "route", "name": "retry_plan", "targetSkill": "paper-intake-router", "notes": "读取 query-reformulation.json；生成 retry-plan.json，决定是否需要二次检索"},
            {"step": 6, "type": "route", "name": "paper_search_retry", "targetSkill": paper_search_skill, "notes": "若 retry-plan.json 中 retryNeeded=true，则按 queries 执行一次补检索，再回到 screening"},
            {"step": 7, "type": "route", "name": "reference_pack", "targetSkill": ref_skill, "notes": "读取 reference-screening.json；将筛选后的核心文献入库/格式化，并写出 reference-pack.json/.md"},
            {"step": 8, "type": "route", "name": "evidence_pack", "targetSkill": "paper-intake-router", "notes": "读取 reference-pack.json；生成 writing-evidence-pack.json/.md，按章节与论点整理写作证据"},
            {"step": 9, "type": "route", "name": "citation_plan", "targetSkill": "paper-intake-router", "notes": "读取 writing-evidence-pack.json；生成 citation-plan.json/.md，按章节与 claimType 规划推荐引用与 inline marker"},
            {"step": 10, "type": "route", "name": "figure_table_plan", "targetSkill": "paper-intake-router", "notes": "读取任务单与 writing-evidence-pack.json；生成 figure-table-plan.json/.md，严格锁定图表编号与正文引用格式"},
            {"step": 11, "type": "route", "name": "figure_table_codegen", "targetSkill": "paper-intake-router", "notes": "对可程序化图表生成代码脚手架、CSV 模板、占位表数据与输出路径"},
            {"step": 12, "type": "route", "name": "write_main", "targetSkill": writer_skill, "notes": "读取 writing-evidence-pack.json 与 citation-plan.json；完成正文草稿，并遵守 figure-table-plan.json 的图表编号"},
            {"step": 13, "type": "route", "name": "validate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[0]["notes"]},
            {"step": 14, "type": "route", "name": "autofix_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[1]["notes"]},
            {"step": 15, "type": "route", "name": "revalidate_figure_table_refs", "targetSkill": "paper-intake-router", "notes": validation_tail[2]["notes"]},
            {"step": 16, "type": "route", "name": "enforce_final_gate", "targetSkill": "paper-intake-router", "notes": validation_tail[3]["notes"]},
            {"step": 17, "type": "route", "name": "inject_inline_citations", "targetSkill": "paper-intake-router", "notes": "读取 citation-plan.json；对带 [claimType] 标识的草稿段落插入内部引用锚点，产出 cited-draft.md"},
            {"step": 18, "type": "route", "name": "render_final_citations", "targetSkill": "paper-intake-router", "notes": "读取 cited-draft.md 与 reference-pack.json；按目标样式渲染终版正文引用（先支持 GB/T 数字序号与 APA inline）"},
            {"step": 19, "type": "route", "name": "repro_pipeline", "targetToolchain": repro_chain, "notes": "构建可复现流水线与持续编译，并确保图表产物可重建；仅允许在 final gate 通过后执行"}
        ]

    msg = "任务单已齐全，建议立即进入执行链：Playbook {}。".format(playbook)
    if paper_type == "course":
        msg += " 课程论文优先保证论证完整、图表清晰与格式合规。"
    elif paper_type == "degree":
        msg += " 学位论文优先保证方法-实验-结论闭环，以及图表编号和正文引用严格一致。"

    return {
        "mode": "execute",
        "readyToExecute": True,
        "recommendedPlaybook": playbook,
        "assistantMessage": msg,
        "actions": chain
    }


def main():
    parser = argparse.ArgumentParser(description="Generate next actions from normalized task sheet")
    parser.add_argument("--task", required=True, help="Path to normalized task JSON")
    parser.add_argument("--caps", help="Path to capabilities JSON from detect_capabilities.py")
    parser.add_argument("--out", help="Path to output execution-plan JSON")
    args = parser.parse_args()

    with open(args.task, "r", encoding="utf-8") as f:
        task = json.load(f)

    caps = _load_caps(args.caps)
    plan = build_actions(task, caps)
    if caps:
        plan["capabilitiesUsed"] = True
        plan["capabilitySummary"] = caps.get("summary", {})
    else:
        plan["capabilitiesUsed"] = False

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
