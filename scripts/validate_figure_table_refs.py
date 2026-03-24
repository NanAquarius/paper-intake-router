#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ZH_LABEL_RE = re.compile(r"(?:(图|表)\s*\d+(?:-\d+)?)")
EN_LABEL_RE = re.compile(r"\b(?:Figure|Table)\s+\d+\b", re.IGNORECASE)


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def normalize_label(raw: str) -> str:
    s = re.sub(r"\s+", " ", raw.strip())
    s = re.sub(r"\bfigure\b", "Figure", s, flags=re.IGNORECASE)
    s = re.sub(r"\btable\b", "Table", s, flags=re.IGNORECASE)
    return s


def extract_body_labels(text: str) -> list[str]:
    labels = [normalize_label(m.group(0)) for m in ZH_LABEL_RE.finditer(text)]
    labels.extend(normalize_label(m.group(0)) for m in EN_LABEL_RE.finditer(text))
    return labels


def expected_items(plan: dict) -> list[dict]:
    out = []
    for chapter in plan.get("chapters", []):
        for item in chapter.get("items", []):
            if item.get("label"):
                out.append({
                    "label": normalize_label(item["label"]),
                    "requiredLevel": item.get("requiredLevel", "recommended"),
                    "chapter": chapter.get("chapter"),
                    "title": item.get("title"),
                })
    return out


def validate(plan: dict, text: str) -> dict:
    items = expected_items(plan)
    expected = [item["label"] for item in items]
    expected_counter = Counter(expected)
    body = extract_body_labels(text)
    body_counter = Counter(body)

    missing_required = []
    missing_recommended = []
    missing_optional = []
    for item in items:
        if body_counter.get(item["label"], 0) > 0:
            continue
        level = item.get("requiredLevel", "recommended")
        if level == "required":
            missing_required.append(item)
        elif level == "optional":
            missing_optional.append(item)
        else:
            missing_recommended.append(item)

    unexpected_in_body = [label for label in body if expected_counter.get(label, 0) == 0]
    duplicate_in_plan = [label for label, count in expected_counter.items() if count > 1]

    numbering_issues = []
    zh_fig = [label for label in expected if label.startswith("图 ")]
    zh_tab = [label for label in expected if label.startswith("表 ")]

    def _check_chapter_sequence(labels: list[str], prefix: str):
        buckets = {}
        for label in labels:
            m = re.match(rf"^{re.escape(prefix)}\s+(\d+)-(\d+)$", label)
            if not m:
                continue
            chapter = int(m.group(1))
            serial = int(m.group(2))
            buckets.setdefault(chapter, []).append(serial)
        for chapter, serials in buckets.items():
            serials = sorted(serials)
            expected_serials = list(range(1, len(serials) + 1))
            if serials != expected_serials:
                numbering_issues.append({
                    "kind": prefix,
                    "chapter": chapter,
                    "expected": expected_serials,
                    "actual": serials,
                })

    _check_chapter_sequence(zh_fig, "图")
    _check_chapter_sequence(zh_tab, "表")

    hard_block = bool(missing_required or unexpected_in_body or duplicate_in_plan or numbering_issues)
    ok = not hard_block

    return {
        "ok": ok,
        "hardBlock": hard_block,
        "summary": {
            "expectedLabelCount": len(expected),
            "bodyLabelCount": len(body),
            "missingRequiredCount": len(missing_required),
            "missingRecommendedCount": len(missing_recommended),
            "missingOptionalCount": len(missing_optional),
            "unexpectedInBodyCount": len(unexpected_in_body),
            "duplicateInPlanCount": len(duplicate_in_plan),
            "numberingIssueCount": len(numbering_issues),
        },
        "missingRequiredInBody": missing_required,
        "missingRecommendedInBody": missing_recommended,
        "missingOptionalInBody": missing_optional,
        "unexpectedInBody": unexpected_in_body,
        "duplicateInPlan": duplicate_in_plan,
        "numberingIssues": numbering_issues,
    }


def render_markdown(report: dict) -> str:
    lines = []
    lines.append("# 图表引用校验报告")
    lines.append("")
    lines.append(f"- 结果：{'通过' if report['ok'] else '未通过'}")
    lines.append(f"- Hard block：{'是' if report['hardBlock'] else '否'}")
    lines.append(f"- 规划编号数：{report['summary']['expectedLabelCount']}")
    lines.append(f"- 正文命中数：{report['summary']['bodyLabelCount']}")
    lines.append("")

    def _render_missing(title: str, items: list[dict]):
        if not items:
            return
        lines.append(title)
        lines.append("")
        for item in items:
            lines.append(f"- {item['label']}（{item['requiredLevel']} / {item['chapter']} / {item['title']}）")
        lines.append("")

    _render_missing("## 必需图表未在正文出现（hard block）", report["missingRequiredInBody"])
    _render_missing("## 建议图表未在正文出现（warning）", report["missingRecommendedInBody"])
    _render_missing("## 可选图表未在正文出现（warning）", report["missingOptionalInBody"])

    if report["unexpectedInBody"]:
        lines.append("## 正文引用但规划不存在（hard block）")
        lines.append("")
        for label in report["unexpectedInBody"]:
            lines.append(f"- {label}")
        lines.append("")

    if report["duplicateInPlan"]:
        lines.append("## 规划内重复编号（hard block）")
        lines.append("")
        for label in report["duplicateInPlan"]:
            lines.append(f"- {label}")
        lines.append("")

    if report["numberingIssues"]:
        lines.append("## 编号连续性问题（hard block）")
        lines.append("")
        for item in report["numberingIssues"]:
            lines.append(f"- {item['kind']} 第 {item['chapter']} 章：expected={item['expected']} actual={item['actual']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Validate figure/table references in draft against figure-table plan")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    args = parser.parse_args()

    plan = load_json(args.plan)
    text = load_text(args.draft)
    report = validate(plan, text)
    md = render_markdown(report)

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        Path(args.out_md).write_text(md, encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
