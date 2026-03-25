#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_intake_router.paths import run_python_script, skill_script


def format_entry(idx: int, paper: dict, style: str) -> dict:
    authors = paper.get('authors', [])
    author_text = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
    year = paper.get('year') or 'n.d.'
    title = paper.get('title', '')
    doi = paper.get('doi', '')
    arxiv = paper.get('arxivId', '')
    landing = paper.get('landingPage', '')

    if style.upper().startswith('APA'):
        citation = f"{author_text} ({year}). {title}."
    else:
        citation = f"[{idx}] {author_text}. {title}, {year}."

    if doi:
        citation += f" DOI: {doi}."
    elif arxiv:
        citation += f" arXiv: {arxiv}."
    elif landing:
        citation += f" {landing}"

    return {
        'id': doi or arxiv or f'ref-{idx:03d}',
        'title': title,
        'authors': authors,
        'year': paper.get('year'),
        'doi': doi,
        'arxivId': arxiv,
        'landingPage': landing,
        'pdfUrl': paper.get('pdfUrl', ''),
        'source': paper.get('source', ''),
        'formattedCitation': citation.strip(),
        'evidenceType': paper.get('evidenceType', 'method'),
    }


def build_pack(screening: dict, shortlist: dict, style: str) -> dict:
    keep_titles = {x['title'] for x in screening.get('included', [])}
    kept = [p for p in shortlist.get('papers', []) if p.get('title') in keep_titles]
    entries = [format_entry(i, p, style) for i, p in enumerate(kept, start=1)]
    return {
        'topic': shortlist.get('topic',''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'style': style,
        'entryCount': len(entries),
        'entries': entries
    }


def main():
    ap = argparse.ArgumentParser(description='Build formatted reference pack from screening + shortlist')
    ap.add_argument('--screening', required=True)
    ap.add_argument('--shortlist', required=True)
    ap.add_argument('--style', default='GB/T 7714')
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()

    screening = json.loads(Path(args.screening).read_text(encoding='utf-8'))
    shortlist = json.loads(Path(args.shortlist).read_text(encoding='utf-8'))
    pack = build_pack(screening, shortlist, args.style)
    Path(args.out_json).write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)
    if args.out_md:
        run_python_script(
            skill_script(REPO_ROOT, 'render_reference_pack.py'),
            '--input', args.out_json,
            '--out-md', args.out_md,
        )


if __name__ == '__main__':
    main()
