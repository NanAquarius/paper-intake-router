#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def render_md(data: dict) -> str:
    lines = ['# 参考文献 pack', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append(f"- Style: {data.get('style','')}")
    lines.append(f"- Entry Count: {data.get('entryCount', 0)}")
    lines.append('')

    for i, e in enumerate(data.get('entries', []), 1):
        title = e.get('title','')
        url = e.get('url') or e.get('pdfUrl') or ''
        header = f"## {i}. [{title}]({url})" if url else f"## {i}. {title}"
        lines.append(header)
        lines.append('')
        lines.append(f"- Authors: {', '.join(e.get('authors', []))}")
        lines.append(f"- Year: {e.get('year','')}")
        lines.append(f"- DOI: {e.get('doi','') or 'N/A'}")
        lines.append(f"- arXiv: {e.get('arxivId','') or 'N/A'}")
        lines.append(f"- Type: {e.get('entryType','')}")
        lines.append(f"- Status: {e.get('status','')}")
        lines.append(f"- Citation Count: {e.get('citationCount','N/A')}")
        lines.append(f"- Notes: {e.get('notes','')}")
        if e.get('formattedCitation'):
            lines.append(f"- Formatted Citation: {e.get('formattedCitation')}")
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Render reference pack markdown from JSON')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-md', required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    Path(args.out_md).write_text(render_md(data), encoding='utf-8')
    print(args.out_md)


if __name__ == '__main__':
    main()
