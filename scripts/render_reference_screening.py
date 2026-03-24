#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def render_md(data: dict) -> str:
    lines = ['# 参考论文 screening', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    rules = data.get('selectionRules', {})
    if rules:
        lines.append('')
        lines.append('## Selection rules')
        lines.append('')
        for k, v in rules.items():
            lines.append(f"- {k}: {v}")
        lines.append('')

    accepted = data.get('accepted', [])
    if accepted:
        lines.append('## Accepted')
        lines.append('')
        for item in accepted:
            lines.append(f"- {item.get('rank','?')}. {item.get('title','')} — {item.get('bucket','')} — {item.get('reason','')}")
        lines.append('')

    rejected = data.get('rejected', [])
    if rejected:
        lines.append('## Rejected')
        lines.append('')
        for item in rejected:
            lines.append(f"- {item.get('title','')} — {item.get('reason','')}")
        lines.append('')

    warnings = data.get('warnings', [])
    if warnings:
        lines.append('## Warnings')
        lines.append('')
        for w in warnings:
            lines.append(f"- {w}")
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Render reference screening markdown from JSON')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-md', required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    Path(args.out_md).write_text(render_md(data), encoding='utf-8')
    print(args.out_md)


if __name__ == '__main__':
    main()
