#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CHAPTER_ROLE_MAP = {
    "绪论": "introduction",
    "相关工作": "related-work",
    "方法": "methods",
    "实验": "experiments",
    "讨论": "discussion",
    "结论": "conclusion",
    "introduction": "introduction",
    "related-work": "related-work",
    "methods": "methods",
    "experiments": "experiments",
    "discussion": "discussion",
    "conclusion": "conclusion",
}

DEFAULT_ITEMS_BY_ROLE = {
    "introduction": [
        ("figure", "研究问题与系统流程概览", "flowchart", "required"),
        ("table", "研究对象或符号说明表", "dataset-table", "recommended"),
    ],
    "related-work": [
        ("table", "相关方法对比表", "comparison-table", "required"),
    ],
    "methods": [
        ("figure", "方法框架图", "architecture", "required"),
        ("table", "模块定义与输入输出说明表", "results-table", "recommended"),
    ],
    "experiments": [
        ("table", "主实验结果表", "results-table", "required"),
        ("table", "消融实验表", "ablation-table", "recommended"),
        ("figure", "关键结果可视化", "bar", "recommended"),
    ],
    "discussion": [
        ("figure", "误差或案例分析图", "heatmap", "recommended"),
    ],
    "conclusion": [],
    "other": [],
}


def load_json(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def detect_numbering_mode(task: dict) -> str:
    selected = task.get("selectedLayoutTemplate") or {}
    template_id = (selected.get("templateId") or "").lower()
    paper_type = task.get("paperType")
    language = task.get("language")

    if paper_type == "degree":
        return "chapter-based"
    if language == "zh" and paper_type == "course":
        return "global-sequential"
    if "degree" in template_id:
        return "chapter-based"
    return "global-sequential"


def build_label(kind: str, chapter_index: int, global_index: int, numbering_mode: str, language: str) -> str:
    if language == "en":
        prefix = "Figure" if kind == "figure" else "Table"
        return f"{prefix} {global_index}"
    prefix = "图" if kind == "figure" else "表"
    if numbering_mode == "chapter-based":
        return f"{prefix} {chapter_index}-{global_index}"
    return f"{prefix} {global_index}"


def build_body_reference(kind: str, label: str, language: str) -> str:
    if language == "en":
        return f"As shown in {label}" if kind == "figure" else f"see {label}"
    return f"如{label}所示" if kind == "figure" else f"见{label}"


def slugify(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "item"


def pick_layout_patterns(task: dict, numbering_mode: str) -> tuple[str, str]:
    language = task.get("language") or "zh"
    if language == "en":
        return "Figure 1", "Table 1"
    if numbering_mode == "chapter-based":
        return "图 1-1", "表 1-1"
    return "图 1", "表 1"


def infer_claim_type(role: str, kind: str, spec_type: str) -> str:
    if role == "introduction":
        return "problem framing"
    if role == "related-work":
        return "baseline comparison"
    if role == "methods":
        return "method choice"
    if role == "experiments":
        if spec_type == "results-table":
            return "baseline comparison"
        if spec_type == "ablation-table":
            return "method choice"
        return "result interpretation"
    if role == "discussion":
        return "risk discussion"
    return "result interpretation"


def build_semantic_purpose(role: str, kind: str, title: str, spec_type: str, chapter_name: str, claim_type: str) -> str:
    if claim_type == "problem framing":
        if kind == "figure":
            return "用于概括研究对象、问题设定与系统流程，使读者快速理解全文的总体结构。"
        return "用于说明研究对象、符号定义或任务边界，帮助后续章节建立统一理解。"
    if claim_type == "baseline comparison":
        if spec_type == "comparison-table":
            return "用于比较不同相关方法在任务设定、训练目标、数据使用与评价指标上的差异，支撑研究空缺分析。"
        return "用于汇总不同方法在核心指标上的结果差异，支撑性能对比与优势判断。"
    if claim_type == "method choice":
        if spec_type == "ablation-table":
            return "用于展示消融实验中各组成部分对性能的影响，支撑方法设计选择的合理性。"
        if kind == "figure":
            return "用于展示方法框架、模块关系与数据流，帮助解释模型设计与执行路径。"
        return "用于明确模块定义、输入输出与关键配置，便于读者理解方法细节。"
    if claim_type == "result interpretation":
        if kind == "figure":
            return "用于可视化关键实验结果、性能趋势或分布差异，使实验结论更直观。"
        return "用于汇总核心实验结果，支撑模型性能、对比优势与主要结论。"
    if claim_type == "risk discussion":
        if kind == "figure":
            return "用于展示误差分布、失败案例或现象分析，支撑对模型局限性的讨论。"
        return "用于整理风险现象与局限性分析结果，支撑对模型边界的讨论。"
    return f"用于支撑章节《{chapter_name}》中的关键论证与结果解释。"


def index_evidence(evidence_pack: dict | None) -> dict:
    out = defaultdict(list)
    if not evidence_pack:
        return out
    for ch in evidence_pack.get("chapters", []):
        chapter = ch.get("chapter")
        for item in ch.get("items", []):
            out[(chapter, item.get("bestArgumentFit", ""))].append(item)
    return out


def index_citation_plan(citation_plan: dict | None) -> dict:
    out = {}
    if not citation_plan:
        return out
    for ch in citation_plan.get("chapters", []):
        chapter = ch.get("chapter")
        for claim in ch.get("claims", []):
            out[(chapter, claim.get("claimType", ""))] = claim
    return out


def select_support_evidence(chapter_role: str, claim_type: str, evidence_index: dict) -> list[dict]:
    items = evidence_index.get((chapter_role, claim_type), [])[:3]
    result = []
    for item in items:
        result.append({
            "title": item.get("title", ""),
            "citationKey": item.get("citationKey", ""),
            "bestArgumentFit": item.get("bestArgumentFit", ""),
            "usageNote": item.get("usageNote", ""),
            "sourceUrl": item.get("sourceUrl", ""),
        })
    return result


def select_citation_hint(chapter_role: str, claim_type: str, citation_index: dict) -> dict:
    hit = citation_index.get((chapter_role, claim_type), {})
    return {
        "recommendedCitations": hit.get("recommendedCitations", []),
        "inlineMarker": hit.get("inlineMarker", ""),
        "note": hit.get("note", ""),
    }


def build_plan(task: dict, evidence_pack: dict | None = None, citation_plan: dict | None = None) -> dict:
    language = task.get("language") or "zh"
    numbering_mode = detect_numbering_mode(task)
    figure_pattern, table_pattern = pick_layout_patterns(task, numbering_mode)
    selected = task.get("selectedLayoutTemplate") or {}
    chapters = [
        {"chapter": "绪论" if language == "zh" else "introduction"},
        {"chapter": "相关工作" if language == "zh" else "related-work"},
        {"chapter": "方法" if language == "zh" else "methods"},
        {"chapter": "实验" if language == "zh" else "experiments"},
        {"chapter": "讨论" if language == "zh" else "discussion"},
    ]

    evidence_index = index_evidence(evidence_pack)
    citation_index = index_citation_plan(citation_plan)

    global_counts = defaultdict(int)
    chapter_outputs = []

    for chapter_idx, chapter in enumerate(chapters, start=1):
        chapter_name = chapter.get("chapter") or f"chapter-{chapter_idx}"
        role = CHAPTER_ROLE_MAP.get(chapter_name, CHAPTER_ROLE_MAP.get(str(chapter_name).lower(), "other"))
        items = []
        local_counts = defaultdict(int)

        for kind, title, spec_type, required_level in DEFAULT_ITEMS_BY_ROLE.get(role, []):
            global_counts[kind] += 1
            local_counts[kind] += 1
            if numbering_mode == "chapter-based" and language != "en":
                serial_index = local_counts[kind]
            else:
                serial_index = global_counts[kind]

            label = build_label(kind, chapter_idx, serial_index, numbering_mode, language)
            stem = f"ch{chapter_idx:02d}-{'fig' if kind == 'figure' else 'tab'}{serial_index:02d}-{slugify(title)}"
            claim_type = infer_claim_type(role, kind, spec_type)
            purpose = build_semantic_purpose(role, kind, title, spec_type, chapter_name, claim_type)
            support_evidence = select_support_evidence(role, claim_type, evidence_index)
            citation_hint = select_citation_hint(role, claim_type, citation_index)

            items.append({
                "kind": kind,
                "requiredLevel": required_level,
                "label": label,
                "title": title,
                "purpose": purpose,
                "claimType": claim_type,
                "supportEvidence": support_evidence,
                "citationHint": citation_hint,
                "bodyReference": build_body_reference(kind, label, language),
                "numberingRule": numbering_mode,
                "specType": spec_type,
                "codegen": {
                    "enabled": True,
                    "language": "python",
                    "scriptPath": f"artifacts/codegen/{stem}.py",
                    "dataPath": f"artifacts/data/{stem}.csv",
                    "outputPath": f"artifacts/{'figures' if kind == 'figure' else 'tables'}/{stem}{'.png' if kind == 'figure' else '.csv'}"
                }
            })

        chapter_outputs.append({
            "chapter": chapter_name,
            "chapterRole": role,
            "items": items,
        })

    return {
        "topic": task.get("topic") or "",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "layoutTemplate": {
            "templateId": selected.get("templateId") or "user-provided",
            "name": selected.get("name") or "用户排版参考",
            "numberingMode": numbering_mode,
            "figurePattern": figure_pattern,
            "tablePattern": table_pattern,
        },
        "chapters": chapter_outputs,
    }


def render_markdown(plan: dict) -> str:
    lines = []
    lines.append(f"# 图表规划：{plan.get('topic') or '未命名主题'}")
    lines.append("")
    lines.append(f"- 模板：{plan['layoutTemplate'].get('name')}")
    lines.append(f"- 图编号：{plan['layoutTemplate'].get('figurePattern')}")
    lines.append(f"- 表编号：{plan['layoutTemplate'].get('tablePattern')}")
    lines.append("")

    for chapter in plan.get("chapters", []):
        lines.append(f"## {chapter.get('chapter')}")
        lines.append("")
        if not chapter.get("items"):
            lines.append("- 暂无强制图表项")
            lines.append("")
            continue
        for item in chapter["items"]:
            lines.append(f"- `{item['label']}` {item['title']}（{item['kind']} / {item['requiredLevel']} / {item['claimType']}）")
            lines.append(f"  - 作用：{item['purpose']}")
            if item.get('citationHint', {}).get('recommendedCitations'):
                lines.append(f"  - 引用建议：{', '.join(item['citationHint']['recommendedCitations'])}")
            lines.append(f"  - 正文引用：{item['bodyReference']}")
            lines.append(f"  - 产物：{item['codegen']['outputPath']}")
            lines.append(f"  - 脚本：{item['codegen']['scriptPath']}")
            lines.append(f"  - 数据：{item['codegen']['dataPath']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Build figure/table plan from task sheet and optional evidence pack/citation plan")
    parser.add_argument("--task", required=True)
    parser.add_argument("--evidence-pack")
    parser.add_argument("--citation-plan")
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    args = parser.parse_args()

    task = load_json(args.task)
    evidence_pack = load_json(args.evidence_pack)
    citation_plan = load_json(args.citation_plan)
    plan = build_plan(task, evidence_pack, citation_plan)
    md = render_markdown(plan)

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        Path(args.out_md).write_text(md, encoding="utf-8")

    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
