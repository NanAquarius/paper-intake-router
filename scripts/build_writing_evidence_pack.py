#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CHAPTER_ORDER = ['introduction', 'related-work', 'methods', 'experiments', 'discussion']


def build_pack(cards: dict) -> dict:
    grouped = defaultdict(list)
    for c in cards.get('cards', []):
        chapter = c.get('bestChapterFit') or 'discussion'
        grouped[chapter].append({
            'title': c.get('title', ''),
            'citationKey': c.get('citationKey', ''),
            'bestArgumentFit': c.get('bestArgumentFit', ''),
            'canSupportClaim': c.get('canSupportClaim', []),
            'usageNote': c.get('whyKeep', ''),
            'riskIfOverused': c.get('riskIfOverused', ''),
            'sourceUrl': c.get('sourceUrl', ''),
        })

    chapters = []
    for name in CHAPTER_ORDER:
        items = grouped.get(name, [])
        if items:
            chapters.append({'chapter': name, 'items': items})

    return {
        'topic': cards.get('topic', ''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'chapters': chapters,
    }


def render_md(data: dict) -> str:
    lines = ['# 写作证据包', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append('')

    for ch in data.get('chapters', []):
        title = ch.get('chapter', '')
        lines.append(f"## {title}")
        lines.append('')
        for i, item in enumerate(ch.get('items', []), 1):
            url = item.get('sourceUrl', '')
            head = f"### {i}. [{item.get('title','')}]({url})" if url else f"### {i}. {item.get('title','')}"
            lines.append(head)
            lines.append('')
            lines.append(f"- Citation key: {item.get('citationKey','')}")
            lines.append(f"- Best argument fit: {item.get('bestArgumentFit','')}")
            claims = item.get('canSupportClaim', [])
            if claims:
                lines.append('- Can support claim:')
                for claim in claims:
                    lines.append(f"  - {claim}")
            lines.append(f"- Usage note: {item.get('usageNote','')}")
            lines.append(f"- Risk if overused: {item.get('riskIfOverused','')}")
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Build writing evidence pack from reference cards')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()

    cards = json.loads(Path(args.input).read_text(encoding='utf-8'))
    data = build_pack(cards)
    Path(args.out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)
    if args.out_md:
        Path(args.out_md).write_text(render_md(data), encoding='utf-8')
        print(args.out_md)


if __name__ == '__main__':
    main()
