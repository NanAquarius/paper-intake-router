#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULTS = {
    "zh": {
        "style": "GB/T 7714",
        "course_words": 5000,
        "bachelor_words": 15000,
        "master_words": 25000,
        "doctor_words": 50000,
    },
    "en": {
        "style": "APA 7",
        "course_words": 5000,
        "bachelor_words": 12000,
        "master_words": 20000,
        "doctor_words": 45000,
    },
}

PAPER_TYPE_ALIASES = {
    "degree": "degree",
    "学位": "degree",
    "学位论文": "degree",
    "thesis": "degree",
    "course": "course",
    "课程": "course",
    "课程论文": "course",
    "coursepaper": "course",
}

DEGREE_LEVEL_ALIASES = {
    "本科": "bachelor",
    "学士": "bachelor",
    "bachelor": "bachelor",
    "undergraduate": "bachelor",
    "硕士": "master",
    "master": "master",
    "研究生": "master",
    "博士": "doctor",
    "phd": "doctor",
    "doctor": "doctor",
}

STYLE_ALIASES = {
    "gb/t": "GB/T 7714",
    "gbt": "GB/T 7714",
    "gb/t 7714": "GB/T 7714",
    "gbt7714": "GB/T 7714",
    "apa": "APA 7",
    "apa7": "APA 7",
    "apa 7": "APA 7",
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def layout_template_dir() -> Path:
    return workspace_root() / "paper-template-library" / "layout" / "defaults"


def normalize_paper_type(value: str | None) -> str:
    if not value:
        return "unknown"
    v = str(value).strip().lower()
    return PAPER_TYPE_ALIASES.get(v, PAPER_TYPE_ALIASES.get(str(value).strip(), "unknown"))


def normalize_degree_level(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    v = raw.lower()
    return DEGREE_LEVEL_ALIASES.get(v, DEGREE_LEVEL_ALIASES.get(raw, raw))


def normalize_style(value: str | None, lang: str) -> tuple[str, bool]:
    if not value:
        return DEFAULTS[lang]["style"], True
    raw = str(value).strip()
    v = raw.lower().replace(" ", "")
    style = STYLE_ALIASES.get(v)
    if style:
        return style, False
    v2 = raw.lower()
    style = STYLE_ALIASES.get(v2)
    if style:
        return style, False
    return raw, False


def to_int_words(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip().lower().replace(",", "")
    s = s.replace("字", "")
    try:
        if s.endswith("k"):
            return int(float(s[:-1]) * 1000)
        if s.endswith("w"):
            return int(float(s[:-1]) * 10000)
        if s.endswith("万"):
            return int(float(s[:-1]) * 10000)
        return int(float(s))
    except Exception:
        return None


def pick_default_words(paper_type: str, degree_level: str | None, lang: str) -> int:
    d = DEFAULTS.get(lang, DEFAULTS["zh"])
    if paper_type == "course":
        return d["course_words"]
    lv = normalize_degree_level(degree_level)
    if lv == "doctor":
        return d["doctor_words"]
    if lv == "master":
        return d["master_words"]
    return d["bachelor_words"]


def load_layout_templates() -> list[dict]:
    templates = []
    base = layout_template_dir()
    if not base.exists():
        return templates

    for path in sorted(base.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_filePath"] = str(path)
        templates.append(data)
    return templates


def score_layout_template(template: dict, *, paper_type: str, degree_level: str | None, language: str, style: str, delivery_goal: str) -> int | None:
    scenarios = template.get("scenarios") or {}
    paper_types = scenarios.get("paperTypes") or []
    languages = scenarios.get("languages") or []
    styles = scenarios.get("styles") or []
    delivery_goals = scenarios.get("deliveryGoals") or []
    degree_levels = scenarios.get("degreeLevels") or []

    if paper_types and paper_type not in paper_types:
        return None
    if languages and language not in languages:
        return None
    if styles and style not in styles:
        return None
    if delivery_goals and delivery_goal not in delivery_goals:
        return None
    if paper_type == "degree" and degree_levels and degree_level not in degree_levels:
        return None

    score = int(((template.get("selection") or {}).get("priority")) or 0)
    if paper_type in paper_types:
        score += 30
    if language in languages:
        score += 20
    if style in styles:
        score += 20
    if delivery_goal in delivery_goals:
        score += 10
    if paper_type == "degree" and degree_level and degree_level in degree_levels:
        score += 20
    return score


def resolve_default_layout_template(*, paper_type: str, degree_level: str | None, language: str, style: str, delivery_goal: str) -> dict:
    candidates = []
    for template in load_layout_templates():
        score = score_layout_template(
            template,
            paper_type=paper_type,
            degree_level=degree_level,
            language=language,
            style=style,
            delivery_goal=delivery_goal,
        )
        if score is None:
            continue
        candidates.append((score, template))

    if not candidates:
        return {
            "source": "unresolved",
            "templateId": None,
            "name": None,
            "authorityLevel": None,
            "sourceKind": None,
            "path": None,
            "toolchainPreference": [],
            "selectionReason": "未找到匹配的默认排版模板。",
        }

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best = candidates[0]

    return {
        "source": "default-library",
        "templateId": best.get("templateId"),
        "name": best.get("name"),
        "authorityLevel": best.get("authorityLevel"),
        "sourceKind": best.get("sourceKind"),
        "path": best.get("_filePath"),
        "relativePath": (best.get("artifacts") or {}).get("relativePath"),
        "toolchainPreference": best.get("toolchainPreference") or [],
        "citationRendering": best.get("citationRendering") or {},
        "selectionReason": f"根据 paperType={paper_type}, degreeLevel={degree_level or '-'}, language={language}, style={style}, deliveryGoal={delivery_goal} 匹配默认模板。",
    }


def resolve_layout_selection(layout_reference: dict, *, paper_type: str, degree_level: str | None, language: str, style: str, delivery_goal: str) -> dict:
    has_user_reference = bool(layout_reference.get("name") or layout_reference.get("url") or layout_reference.get("path"))
    default_candidate = resolve_default_layout_template(
        paper_type=paper_type,
        degree_level=degree_level,
        language=language,
        style=style,
        delivery_goal=delivery_goal,
    )

    if has_user_reference:
        return {
            "source": "user-provided",
            "templateId": None,
            "name": layout_reference.get("name") or "用户提供的排版参考",
            "authorityLevel": "external-reference",
            "sourceKind": "user-reference",
            "path": layout_reference.get("path"),
            "url": layout_reference.get("url"),
            "toolchainPreference": default_candidate.get("toolchainPreference") or [],
            "citationRendering": default_candidate.get("citationRendering") or {},
            "selectionReason": "用户已提供排版参考，优先采用用户样例；默认模板仅作为兜底实现基线。",
            "fallbackDefault": default_candidate,
        }

    return default_candidate


def normalize(payload: dict) -> dict:
    lang = payload.get("language") or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"

    paper_type = normalize_paper_type(payload.get("paperType"))
    degree_level_norm = normalize_degree_level(payload.get("degreeLevel"))
    style, style_defaulted = normalize_style(payload.get("style"), lang)

    words = to_int_words(payload.get("targetWords"))
    words_defaulted = False
    if not words:
        words = pick_default_words(paper_type, payload.get("degreeLevel"), lang)
        words_defaulted = True

    layout_ref = payload.get("layoutReference") or {}
    has_layout_ref = bool(layout_ref.get("name") or layout_ref.get("url") or layout_ref.get("path"))
    delivery_goal = payload.get("deliveryGoal") or "pdf_with_sources"

    required_by_type = {
        "degree": ["degreeLevel", "discipline", "topic", "style", "targetWords"],
        "course": ["courseName", "topic", "style", "targetWords"],
        "unknown": ["paperType", "topic", "style", "targetWords"],
    }

    normalized = {
        "paperType": paper_type,
        "degreeLevel": degree_level_norm,
        "discipline": payload.get("discipline"),
        "courseName": payload.get("courseName"),
        "topic": payload.get("topic"),
        "style": style,
        "targetWords": int(words),
        "language": lang,
        "deliveryGoal": delivery_goal,
        "layoutReference": {
            "name": layout_ref.get("name"),
            "url": layout_ref.get("url"),
            "path": layout_ref.get("path"),
            "enabled": has_layout_ref,
        },
        "defaultsApplied": {
            "style": style_defaulted,
            "targetWords": words_defaulted,
            "layoutReference": not has_layout_ref,
        },
        "requiredFields": required_by_type[paper_type],
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
    }

    missing = []
    for f in required_by_type[paper_type]:
        if f in ("style", "targetWords"):
            continue
        if not normalized.get(f):
            missing.append(f)
    normalized["missingFields"] = missing
    normalized["readyToExecute"] = len(missing) == 0

    goal = (normalized.get("deliveryGoal") or "").lower()
    if "reproducible" in goal:
        normalized["recommendedPlaybook"] = "C"
    elif paper_type == "degree":
        normalized["recommendedPlaybook"] = "B" if goal != "draft_only" else "A"
    elif paper_type == "course":
        normalized["recommendedPlaybook"] = "A" if goal == "draft_only" else "B"
    else:
        normalized["recommendedPlaybook"] = "A"

    normalized["selectedLayoutTemplate"] = resolve_layout_selection(
        normalized["layoutReference"],
        paper_type=paper_type,
        degree_level=degree_level_norm,
        language=lang,
        style=style,
        delivery_goal=delivery_goal,
    )
    normalized["defaultsApplied"]["layoutTemplate"] = normalized["selectedLayoutTemplate"].get("source") == "default-library"

    return normalized


def render_markdown(task: dict) -> str:
    lines = []
    lines.append("【论文类型】")
    lines.append(f"- {task['paperType']}")
    lines.append("")

    lines.append("【基础信息】")
    if task.get("paperType") == "degree":
        lines.append(f"- 学位层级：{task.get('degreeLevel') or '未填'}")
        lines.append(f"- 学科方向：{task.get('discipline') or '未填'}")
    if task.get("paperType") == "course":
        lines.append(f"- 课程名称：{task.get('courseName') or '未填'}")
    lines.append(f"- 主题：{task.get('topic') or '未填'}")
    lines.append("")

    lines.append("【格式与篇幅】")
    lines.append(f"- 格式规范：{task.get('style')}" + ("（默认）" if task['defaultsApplied']['style'] else ""))
    lines.append(f"- 字数：{task.get('targetWords')}" + ("（默认）" if task['defaultsApplied']['targetWords'] else ""))
    lines.append("")

    lines.append("【排版参考】")
    if task["layoutReference"]["enabled"]:
        lines.append("- 用户已提供排版参考")
        for key in ("name", "url", "path"):
            if task["layoutReference"].get(key):
                lines.append(f"- {key}: {task['layoutReference'][key]}")
    else:
        lines.append("- 用户未提供排版参考")

    selected = task.get("selectedLayoutTemplate") or {}
    if selected.get("source") == "default-library":
        lines.append(f"- 已选默认模板：{selected.get('name')}")
        if selected.get("templateId"):
            lines.append(f"- templateId: {selected.get('templateId')}")
        if selected.get("relativePath"):
            lines.append(f"- relativePath: {selected.get('relativePath')}")
    elif selected.get("source") == "user-provided":
        lines.append(f"- 采用方式：优先按用户样例 `{selected.get('name')}` 对齐")
        fallback = selected.get("fallbackDefault") or {}
        if fallback.get("name"):
            lines.append(f"- 默认兜底模板：{fallback.get('name')}")
            if fallback.get("templateId"):
                lines.append(f"- fallbackTemplateId: {fallback.get('templateId')}")
    else:
        lines.append("- 默认模板：未解析到匹配项")
    lines.append("")

    lines.append("【交付目标】")
    lines.append(f"- {task.get('deliveryGoal')}")
    lines.append("")

    lines.append("【推荐执行方案】")
    lines.append(f"- Playbook {task.get('recommendedPlaybook')}")
    lines.append("")

    lines.append("【缺失信息】")
    if task.get("missingFields"):
        for f in task["missingFields"]:
            lines.append(f"- {f}")
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("【下一步执行建议】")
    if task.get("readyToExecute"):
        lines.append("- 字段齐全，进入大纲与文献阶段。")
    else:
        lines.append("- 先补齐缺失字段，再进入写作执行。")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Normalize paper intake payload into a task sheet")
    parser.add_argument("--input", required=True, help="Path to JSON intake file")
    parser.add_argument("--out-json", help="Output normalized JSON file path")
    parser.add_argument("--out-md", help="Output markdown task sheet path")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    task = normalize(payload)
    md = render_markdown(task)

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(task, f, ensure_ascii=False, indent=2)

    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md + "\n")

    print(json.dumps(task, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
