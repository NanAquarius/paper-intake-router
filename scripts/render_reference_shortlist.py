#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def render_md(data: dict) -> str:
    lines = []
    lines.append('# 参考论文 shortlist')
    lines.append('')
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append(f"- Sources Used: {', '.join(data.get('sourcesUsed',[]))}")
    lines.append('')

    papers = data.get('papers', [])
    for p in papers:
        title = p.get('title','')
        link = p.get('landingPage') or p.get('pdfUrl') or ''
        header = f"## {p.get('rank','?')}. [{title}]({link})" if link else f"## {p.get('rank','?')}. {title}"
        lines.append(header)
        lines.append('')
        lines.append(f"- Authors: {', '.join(p.get('authors',[]))}")
        lines.append(f"- Year: {p.get('year','')}")
        lines.append(f"- DOI: {p.get('doi','') or 'N/A'}")
        lines.append(f"- arXiv: {p.get('arxivId','') or 'N/A'}")
        lines.append(f"- PDF: {p.get('pdfUrl','') or 'N/A'}")
        lines.append(f"- Citation Count: {p.get('citationCount','N/A')}")
        lines.append(f"- Source: {p.get('source','')}")
        lines.append(f"- Type: {p.get('evidenceType','')}")
        lines.append(f"- Why it matters: {p.get('relevanceNote','')}")
        if p.get('needsVerification'):
            lines.append(f"- Note: needs verification")
        lines.append('')

    excluded = data.get('excluded', [])
    if excluded:
        lines.append('## Excluded candidates')
        lines.append('')
        for e in excluded:
            lines.append(f"- {e.get('title','')} — {e.get('reason','')}")
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Render reference shortlist markdown from JSON')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-md', required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    md = render_md(data)
    Path(args.out_md).write_text(md, encoding='utf-8')
    print(args.out_md)


if __name__ == '__main__':
    main()
