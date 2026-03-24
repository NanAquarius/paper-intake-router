#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def build_marker(keys, style='GB/T 7714'):
    if not keys:
        return ''
    if style.upper().startswith('APA'):
        return '(cite: ' + '; '.join(keys) + ')'
    return '[' + ','.join(keys) + ']'


def build_plan(evidence_pack: dict, style: str) -> dict:
    chapters_out = []
    for ch in evidence_pack.get('chapters', []):
        claim_map = {}
        for item in ch.get('items', []):
            ctype = item.get('bestArgumentFit', 'method choice')
            bucket = claim_map.setdefault(ctype, {
                'claimType': ctype,
                'recommendedCitations': [],
                'inlineMarker': '',
                'note': ''
            })
            ck = item.get('citationKey', '')
            if ck and ck not in bucket['recommendedCitations']:
                bucket['recommendedCitations'].append(ck)
        claims = []
        for c in claim_map.values():
            keys = c['recommendedCitations'][:3]
            c['recommendedCitations'] = keys
            c['inlineMarker'] = build_marker(keys, style)
            c['note'] = '写该类论点时优先使用这些引用；若正文没有明确对应 claim，不要硬插。'
            claims.append(c)
        chapters_out.append({'chapter': ch.get('chapter',''), 'claims': claims})
    return {
        'topic': evidence_pack.get('topic',''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'style': style,
        'chapters': chapters_out,
    }


def render_md(data: dict) -> str:
    lines = ['# Citation plan', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append(f"- Style: {data.get('style','')}")
    lines.append('')
    for ch in data.get('chapters', []):
        lines.append(f"## {ch.get('chapter','')}")
        lines.append('')
        for i, claim in enumerate(ch.get('claims', []), 1):
            lines.append(f"### {i}. {claim.get('claimType','')}")
            lines.append('')
            lines.append(f"- Recommended citations: {', '.join(claim.get('recommendedCitations', []))}")
            lines.append(f"- Inline marker: {claim.get('inlineMarker','')}")
            lines.append(f"- Note: {claim.get('note','')}")
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Build citation plan from writing evidence pack')
    ap.add_argument('--input', required=True)
    ap.add_argument('--style', default='GB/T 7714')
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()
    evidence = json.loads(Path(args.input).read_text(encoding='utf-8'))
    plan = build_plan(evidence, args.style)
    Path(args.out_json).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)
    if args.out_md:
        Path(args.out_md).write_text(render_md(plan), encoding='utf-8')
        print(args.out_md)


if __name__ == '__main__':
    main()
