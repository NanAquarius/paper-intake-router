#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

CLAIM_TYPES = [
    'problem framing',
    'baseline comparison',
    'method choice',
    'result interpretation',
    'risk discussion',
]


def load_plan(path: str):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    mapping = {}
    for ch in data.get('chapters', []):
        chapter = ch.get('chapter', '')
        mapping[chapter] = {}
        for claim in ch.get('claims', []):
            ctype = claim.get('claimType', '')
            keys = claim.get('recommendedCitations', [])
            mapping[chapter][ctype] = keys
    return mapping


def marker(claim_type: str, keys: list[str]) -> str:
    if not keys:
        return ''
    return f" [CITE:{claim_type}|{','.join(keys)}]"


def inject(text: str, plan_map: dict) -> str:
    current_chapter = None
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            current_chapter = stripped.replace('## ', '', 1).strip().lower()
            out.append(line)
            continue

        m = re.match(r'^\[(problem framing|baseline comparison|method choice|result interpretation|risk discussion)\]\s*(.*)$', stripped, re.I)
        if m and current_chapter:
            ctype = m.group(1).lower()
            body = m.group(2)
            keys = plan_map.get(current_chapter, {}).get(ctype, [])
            out.append(body + marker(ctype, keys))
        else:
            out.append(line)
    return '\n'.join(out) + ('\n' if text.endswith('\n') else '')


def main():
    ap = argparse.ArgumentParser(description='Inject internal citation markers into a draft using citation plan')
    ap.add_argument('--draft', required=True)
    ap.add_argument('--citation-plan', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    draft = Path(args.draft).read_text(encoding='utf-8')
    plan_map = load_plan(args.citation_plan)
    injected = inject(draft, plan_map)
    Path(args.out).write_text(injected, encoding='utf-8')
    print(args.out)


if __name__ == '__main__':
    main()
