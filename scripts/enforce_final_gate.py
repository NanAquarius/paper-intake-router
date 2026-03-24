#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

BLOCKING_KEYS = [
    "missingRequiredInBody",
    "unexpectedInBody",
    "duplicateInPlan",
    "numberingIssues",
]
WARNING_KEYS = [
    "missingRecommendedInBody",
    "missingOptionalInBody",
]


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Enforce final PDF gate for figure/table validation")
    parser.add_argument("--validation", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()

    report = load_json(args.validation)
    blocking = {k: report.get(k, []) for k in BLOCKING_KEYS if report.get(k)}
    warnings = {k: report.get(k, []) for k in WARNING_KEYS if report.get(k)}
    ok = not blocking and bool(report.get("ok"))

    result = {
        "ok": ok,
        "blocking": blocking,
        "warnings": warnings,
        "message": "figure/table gate passed" if ok else "figure/table gate blocked final PDF render"
    }

    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
