#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def build_retry_plan(reformulation: dict) -> dict:
    suggestions = reformulation.get('suggestions', [])
    warnings = reformulation.get('triggeredBy', [])
    queries = [
        {
            'kind': s.get('kind', 'broaden'),
            'query': s.get('query', ''),
            'reason': s.get('reason', '')
        }
        for s in suggestions if s.get('query')
    ]
    return {
        'topic': reformulation.get('topic', ''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'retryNeeded': bool(queries),
        'basedOnWarnings': warnings,
        'queries': queries,
        'notes': '若 retryNeeded=true，则按 queries 顺序执行一次补检索，并重新进入 screening。survey 类查询应优先保留综述候选。'
    }


def main():
    ap = argparse.ArgumentParser(description='Build retry plan from query reformulation suggestions')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    out = build_retry_plan(data)
    Path(args.out_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)


if __name__ == '__main__':
    main()
