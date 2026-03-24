#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

ZH_LABEL_RE = re.compile(r"(?:图|表)\s*\d+(?:-\d+)?")
EN_LABEL_RE = re.compile(r"\b(?:Figure|Table)\s+\d+\b", re.IGNORECASE)
ZH_TITLE_LINE_RE = re.compile(r"^(图|表)\s*\d+(?:-\d+)?\s*(.+)$", re.MULTILINE)
EN_TITLE_LINE_RE = re.compile(r"^(Figure|Table)\s+\d+\s*[:.-]?\s*(.+)$", re.MULTILINE | re.IGNORECASE)
ZH_VERBS = re.compile(r"是|为|包括|包含|采用|使用|展示|显示|表明|说明|给出|呈现|反映|提升|下降|增加|减少|优于|劣于|达到|可知|可以看出|可见|如下|存在")
EN_VERBS = re.compile(r"\b(is|are|was|were|be|shows?|illustrates?|summarizes?|presents?|reports?|compares?|demonstrates?|lists?|includes?|reveals?)\b", re.IGNORECASE)
LOW_INFO_ZH_PATTERNS = [
    r"相关工作对比情况",
    r"方法整体结构",
    r"整体结构",
    r"实验结果",
    r"性能变化",
    r"模块关系",
    r"系统整体流程",
    r"关键结果可视化",
    r"对比情况",
    r"结果情况",
]


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def normalize_label(raw: str) -> str:
    s = re.sub(r"\s+", " ", raw.strip())
    s = re.sub(r"\bfigure\b", "Figure", s, flags=re.IGNORECASE)
    s = re.sub(r"\btable\b", "Table", s, flags=re.IGNORECASE)
    s = s.replace("图 ", "图 ").replace("表 ", "表 ")
    return s


def extract_labels(text: str) -> list[str]:
    labels = [normalize_label(m.group(0)) for m in ZH_LABEL_RE.finditer(text)]
    labels.extend(normalize_label(m.group(0)) for m in EN_LABEL_RE.finditer(text))
    return labels


def plan_items(plan: dict) -> list[dict]:
    items = []
    for chapter in plan.get("chapters", []):
        for item in chapter.get("items", []):
            enriched = dict(item)
            enriched["chapter"] = chapter.get("chapter")
            enriched["chapterRole"] = chapter.get("chapterRole")
            items.append(enriched)
    return items


def build_item_map(plan: dict) -> dict:
    return {
        normalize_label(i.get("label", "")): {
            "title": i.get("title", ""),
            "purpose": i.get("purpose", ""),
            "kind": i.get("kind", ""),
            "specType": i.get("specType", ""),
            "chapter": i.get("chapter", ""),
            "chapterRole": i.get("chapterRole", "other"),
            "claimType": i.get("claimType", "result interpretation"),
            "supportEvidence": i.get("supportEvidence", []),
            "citationHint": i.get("citationHint", {}),
        }
        for i in plan_items(plan)
    }


def suggest_replacement(plan: dict, wrong_label: str) -> str | None:
    wrong_label = normalize_label(wrong_label)
    items = plan_items(plan)
    labels = [normalize_label(i.get("label", "")) for i in items]
    if wrong_label in labels:
        return None

    if wrong_label.startswith(("图 ", "表 ")):
        kind = wrong_label.split()[0]
        m = re.match(rf"^{re.escape(kind)}\s+(\d+)(?:-(\d+))?$", wrong_label)
        same_kind = [normalize_label(i.get("label", "")) for i in items if normalize_label(i.get("label", "")).startswith(kind)]
        if not same_kind:
            return None
        if m and m.group(2):
            chapter_hint = int(m.group(1))
            chapter_pref = []
            for label in same_kind:
                mm = re.match(rf"^{re.escape(kind)}\s+(\d+)-(\d+)$", label)
                if mm and int(mm.group(1)) == chapter_hint:
                    chapter_pref.append(label)
            if chapter_pref:
                return chapter_pref[0]
        return same_kind[0]

    if wrong_label.startswith(("Figure", "Table")):
        kind = wrong_label.split()[0]
        same_kind = [normalize_label(i.get("label", "")) for i in items if normalize_label(i.get("label", "")).startswith(kind)]
        if same_kind:
            return same_kind[0]
    return None


def cleanup_tail_zh(tail: str) -> str:
    tail = tail.strip().strip("，,。；;:：")
    tail = re.sub(r"^(可知|可以看出|可见)", "", tail).strip()
    return tail


def looks_fragment_zh(tail: str) -> bool:
    if not tail:
        return True
    if ZH_VERBS.search(tail):
        return False
    return True


def is_low_info_tail_zh(tail: str) -> bool:
    tail = cleanup_tail_zh(tail)
    if not tail:
        return True
    if len(tail) <= 8:
        return True
    return any(re.fullmatch(pat, tail) for pat in LOW_INFO_ZH_PATTERNS)


def summarize_purpose_zh(item: dict) -> str:
    claim_type = item.get("claimType") or "result interpretation"
    spec_type = item.get("specType") or ""
    if claim_type == "problem framing":
        return "研究对象、问题设定与系统流程如下"
    if claim_type == "baseline comparison":
        if spec_type == "comparison-table":
            return "不同相关方法在任务设定、训练目标与评价指标上存在明显差异"
        return "不同方法在核心指标上的性能差异如下"
    if claim_type == "method choice":
        if spec_type == "ablation-table":
            return "不同组成部分对模型性能的影响如下"
        return "本文方法的整体框架、模块关系与数据流如下"
    if claim_type == "result interpretation":
        if item.get("kind") == "figure":
            return "关键实验结果与性能变化趋势如下"
        return "核心实验结果与模型性能对比如下"
    if claim_type == "risk discussion":
        return "误差分布与典型案例反映出的模型局限如下"
    return item.get("title", "")


def internal_anchor(item: dict) -> str:
    hint = item.get("citationHint", {})
    keys = hint.get("recommendedCitations", [])
    ctype = item.get("claimType", "result interpretation")
    if not keys:
        return ""
    return f"[CITE:{ctype}|{','.join(keys)}]"


def evidence_phrase_zh(item: dict, citation_mode: str) -> str:
    hint = item.get("citationHint", {})
    inline_marker = hint.get("inlineMarker", "")
    evidence = item.get("supportEvidence", [])
    if citation_mode == "internal-anchor":
        return internal_anchor(item)
    if citation_mode == "inline-marker" and inline_marker:
        return inline_marker
    if not evidence and not hint.get("recommendedCitations"):
        return ""
    if hint.get("recommendedCitations"):
        keys = "、".join(hint.get("recommendedCitations", [])[:2])
        return f"相关判断可结合 {keys} 进一步支撑"
    first = evidence[0]
    if first.get("title"):
        return f"这一判断与《{first['title']}》中的相关结论一致"
    return ""


def chapter_claim_sentence_zh(label: str, item: dict, citation_mode: str) -> str:
    semantic = summarize_purpose_zh(item)
    evidence_hint = evidence_phrase_zh(item, citation_mode)
    if evidence_hint:
        if citation_mode in ("inline-marker", "internal-anchor") and evidence_hint.startswith("["):
            return f"如{label}所示，{semantic}{evidence_hint}。"
        return f"如{label}所示，{semantic}；{evidence_hint}。"
    return f"如{label}所示，{semantic}。"


def complete_zh_sentence(kind: str, label: str, tail: str, item: dict, citation_mode: str) -> str:
    tail = cleanup_tail_zh(tail)
    if tail and not is_low_info_tail_zh(tail) and not looks_fragment_zh(tail):
        base = tail
        if not re.search(r"[。！？!?]$", base):
            base += "。"
        return f"如{label}所示，{base}"
    return chapter_claim_sentence_zh(label, item, citation_mode)


def cleanup_tail_en(tail: str) -> str:
    return tail.strip().strip(",.;: ")


def looks_fragment_en(tail: str) -> bool:
    if not tail:
        return True
    return not bool(EN_VERBS.search(tail))


def summarize_purpose_en(item: dict) -> str:
    claim_type = item.get("claimType") or "result interpretation"
    if claim_type == "baseline comparison":
        return "the main performance differences across methods"
    if claim_type == "method choice":
        return "the method design choices and module relationships"
    if claim_type == "risk discussion":
        return "the observed limitations and failure patterns"
    return item.get("title", "the relevant content")


def complete_en_sentence(kind: str, label: str, tail: str, item: dict, citation_mode: str) -> str:
    tail = cleanup_tail_en(tail)
    base = tail or summarize_purpose_en(item)
    if citation_mode == "internal-anchor":
        marker = internal_anchor(item)
    elif citation_mode == "inline-marker":
        marker = item.get("citationHint", {}).get("inlineMarker", "")
    else:
        marker = ""
    if kind == "Figure":
        return f"{label} shows {base}{marker}." if marker else f"{label} shows {base}."
    return f"{label} summarizes {base}{marker}." if marker else f"{label} summarizes {base}."


def normalize_zh_reference_line(line: str, item_map: dict, changes: list[dict], citation_mode: str) -> str:
    stripped = line.strip()
    labels = [normalize_label(m.group(0)) for m in ZH_LABEL_RE.finditer(stripped)]
    if not labels:
        return line
    label = labels[0]
    kind = label.split()[0]
    item = item_map.get(label, {"title": "", "purpose": "", "kind": kind, "chapterRole": "other", "claimType": "result interpretation"})

    patterns = [
        rf"^(?:如\s*)?{re.escape(label)}\s*所示[，,]?\s*(.*)$",
        rf"^(?:见|参见)\s*{re.escape(label)}[，,]?\s*(.*)$",
        rf"^{re.escape(label)}\s*(显示|展示|表明|给出|呈现|描绘|说明|列出|统计|汇总)\s*(.*)$",
    ]

    for pat in patterns:
        m = re.match(pat, stripped)
        if not m:
            continue
        tail = m.group(len(m.groups()))
        if looks_fragment_zh(tail) or is_low_info_tail_zh(tail):
            new_line = complete_zh_sentence(kind, label, tail, item, citation_mode)
        else:
            cleaned = cleanup_tail_zh(tail)
            if not re.search(r"[。！？!?]$", cleaned):
                cleaned += "。"
            new_line = f"如{label}所示，{cleaned}"
        if new_line != stripped:
            changes.append({"type": "reference-sentence", "from": stripped, "to": new_line})
        return line.replace(stripped, new_line)
    return line


def normalize_en_reference_line(line: str, item_map: dict, changes: list[dict], citation_mode: str) -> str:
    stripped = line.strip()
    labels = [normalize_label(m.group(0)) for m in EN_LABEL_RE.finditer(stripped)]
    if not labels:
        return line
    label = labels[0]
    kind = label.split()[0]
    item = item_map.get(label, {"title": "", "purpose": "", "kind": kind, "claimType": "result interpretation"})

    patterns = [
        rf"^As\s+shown\s+in\s+{re.escape(label)}[,:]?\s*(.*)$",
        rf"^{re.escape(label)}\s+shows\s*(.*)$",
        rf"^see\s+{re.escape(label)}[,:]?\s*(.*)$",
    ]

    for pat in patterns:
        m = re.match(pat, stripped, flags=re.IGNORECASE)
        if not m:
            continue
        tail = m.group(1)
        if looks_fragment_en(tail):
            new_line = complete_en_sentence(kind, label, tail, item, citation_mode)
        else:
            if kind == "Figure":
                new_line = f"{label} shows {cleanup_tail_en(tail)}."
            else:
                new_line = f"As shown in {label}, {cleanup_tail_en(tail)}."
        if new_line != stripped:
            changes.append({"type": "reference-sentence", "from": stripped, "to": new_line})
        return line.replace(stripped, new_line)
    return line


def autofix(plan: dict, text: str, citation_mode: str) -> tuple[str, dict]:
    item_map = build_item_map(plan)
    changes = []
    fixed = text

    original_labels = extract_labels(text)
    seen = set()
    for raw_norm in original_labels:
        replacement = suggest_replacement(plan, raw_norm)
        if raw_norm in seen:
            continue
        seen.add(raw_norm)
        if replacement and replacement != raw_norm:
            fixed = re.sub(re.escape(raw_norm), replacement, fixed)
            changes.append({"type": "body-label", "from": raw_norm, "to": replacement})

    lines = fixed.splitlines()
    normalized_lines = []
    for line in lines:
        if not line.strip():
            normalized_lines.append(line)
            continue
        line2 = normalize_zh_reference_line(line, item_map, changes, citation_mode)
        line3 = normalize_en_reference_line(line2, item_map, changes, citation_mode)
        normalized_lines.append(line3)
    fixed = "\n".join(normalized_lines)

    def replace_zh_title(match):
        full = match.group(0)
        prefix = normalize_label(match.group(1) + " " + re.search(r"\d+(?:-\d+)?", full).group(0))
        item = item_map.get(prefix, {})
        title = item.get("title", "")
        if title:
            new_line = f"{prefix} {title}"
            if new_line != full.strip():
                changes.append({"type": "title-line", "from": full.strip(), "to": new_line})
            return new_line
        return full

    def replace_en_title(match):
        full = match.group(0)
        prefix = normalize_label(match.group(1) + " " + re.search(r"\d+", full).group(0))
        item = item_map.get(prefix, {})
        title = item.get("title", "")
        if title:
            new_line = f"{prefix}: {title}"
            if new_line != full.strip():
                changes.append({"type": "title-line", "from": full.strip(), "to": new_line})
            return new_line
        return full

    fixed = ZH_TITLE_LINE_RE.sub(replace_zh_title, fixed)
    fixed = EN_TITLE_LINE_RE.sub(replace_en_title, fixed)

    return fixed, {"changeCount": len(changes), "changes": changes, "citationMode": citation_mode}


def main():
    parser = argparse.ArgumentParser(description="Autofix figure/table labels, title lines, and reference phrases using figure-table plan")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--citation-mode", choices=["support-note", "inline-marker", "internal-anchor"], default="support-note")
    parser.add_argument("--out")
    parser.add_argument("--report")
    args = parser.parse_args()

    plan = load_json(args.plan)
    text = load_text(args.draft)
    fixed, report = autofix(plan, text, args.citation_mode)

    if args.out:
        Path(args.out).write_text(fixed, encoding="utf-8")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
