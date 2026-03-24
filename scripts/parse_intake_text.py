#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def detect_paper_type(text: str) -> str | None:
    t = text.lower()
    if any(k in t for k in ["学位论文", "thesis", "毕业论文"]):
        return "degree"
    if any(k in t for k in ["课程论文", "course paper", "term paper", "课程作业"]):
        return "course"
    return None


def detect_degree_level(text: str) -> str | None:
    t = text.lower()
    if any(k in t for k in ["博士", "phd", "doctor"]):
        return "doctor"
    if any(k in t for k in ["硕士", "master", "研究生"]):
        return "master"
    if any(k in t for k in ["本科", "学士", "bachelor", "undergraduate"]):
        return "bachelor"
    return None


def detect_style(text: str) -> str | None:
    t = text.lower().replace(" ", "")
    if any(k in t for k in ["gb/t", "gbt", "gbt7714", "gb/t7714", "7714"]):
        return "GB/T 7714"
    if any(k in t for k in ["apa7", "apa"]):
        return "APA 7"
    return None


def detect_language(text: str) -> str:
    # 简单规则：中文字符比例高则 zh，否则 en
    zh_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    en_count = len(re.findall(r"[A-Za-z]", text))
    return "zh" if zh_count >= en_count else "en"


def detect_target_words(text: str) -> int | None:
    t = text.lower().replace(",", "")
    # e.g. 2.5w, 2.5万, 5000字, 5k
    m = re.search(r"(\d+(?:\.\d+)?)\s*(w|万|k|字)", t)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        if unit in ("w", "万"):
            return int(val * 10000)
        if unit == "k":
            return int(val * 1000)
        return int(val)

    # e.g. 字数 12000 / 12000 words
    m2 = re.search(r"(?:字数|words?)\D{0,6}(\d{4,6})", t)
    if m2:
        return int(m2.group(1))

    return None


def _trim_value(value: str) -> str:
    value = value.splitlines()[0].strip()
    stop_tokens = [
        "，主题", "，题目", "，论文题目", "，格式", "，字数", "，最终", "，排版", "，课程", "，学科",
        ", topic", ", title", ", style", ", format", ", words", ", delivery", ", course", ", discipline",
        "。", ";", "；"
    ]
    for tok in stop_tokens:
        idx = value.lower().find(tok.lower())
        if idx > 0:
            value = value[:idx].strip()
    return value.strip(" ：:，,")


def extract_field(text: str, labels: list[str]) -> str | None:
    # 支持“标签: 值”或“标签：值”
    for lb in labels:
        m = re.search(rf"{re.escape(lb)}\s*[：:]\s*(.+)", text, flags=re.IGNORECASE)
        if m:
            value = _trim_value(m.group(1))
            if value:
                return value
    return None


def detect_delivery_goal(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["可复现", "reproducible", "持续构建", "ci"]):
        return "reproducible_pdf"
    if any(k in t for k in ["只要初稿", "draft only", "初稿"]):
        return "draft_only"
    return "pdf_with_sources"


def detect_layout_reference(text: str) -> dict:
    ref = {"name": None, "url": None, "path": None}

    # URL
    m = re.search(r"https?://\S+", text)
    if m:
        ref["url"] = m.group(0)

    # 常见文件路径/文件名线索
    m2 = re.search(r"([\w\-/\.]+\.(pdf|docx|tex))", text, flags=re.IGNORECASE)
    if m2:
        candidate = m2.group(1)
        if not candidate.startswith("http") and not candidate.startswith("//"):
            ref["path"] = candidate

    # 标签提取
    name = extract_field(text, ["排版参考", "参考样例", "样例论文", "版式参考"])
    if name:
        ref["name"] = name

    if not ref["name"] and ref.get("url"):
        ref["name"] = "用户提供的排版参考链接"

    if any(ref.values()):
        return ref
    return {}


def parse_text(text: str) -> dict:
    paper_type = detect_paper_type(text)
    payload = {
        "paperType": paper_type,
        "degreeLevel": detect_degree_level(text),
        "discipline": extract_field(text, ["学科方向", "专业", "研究方向", "discipline"]),
        "courseName": extract_field(text, ["课程名称", "课程", "course"]),
        "topic": extract_field(text, ["主题", "题目", "论文题目", "topic"]),
        "style": detect_style(text),
        "targetWords": detect_target_words(text),
        "language": detect_language(text),
        "deliveryGoal": detect_delivery_goal(text),
        "layoutReference": detect_layout_reference(text),
    }

    # 兜底：如果没有显式主题，尝试从“写一篇关于xxx”提取
    if not payload["topic"]:
        m = re.search(r"(?:写一篇|写个|写|做一篇)\s*(?:关于)?(.{4,80}?)(?:的)?(?:论文|thesis|paper)", text, flags=re.IGNORECASE)
        if m:
            payload["topic"] = m.group(1).strip(" ：:，,。")

    return payload


def main():
    parser = argparse.ArgumentParser(description="Parse free-form intake text into structured payload JSON")
    parser.add_argument("--text", help="Free-form intake text")
    parser.add_argument("--input", help="Path to text file")
    parser.add_argument("--out", help="Output JSON path")
    args = parser.parse_args()

    if not args.text and not args.input:
        raise SystemExit("Provide --text or --input")

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = args.text

    payload = parse_text(text)

    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
