#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def format_authors_gbt(authors):
    if not authors:
        return ''
    if len(authors) <= 3:
        return ', '.join(authors)
    return ', '.join(authors[:3]) + ', et al.'


def format_authors_apa(authors):
    if not authors:
        return ''
    if len(authors) <= 3:
        return ', '.join(authors)
    return ', '.join(authors[:3]) + ', et al.'


def infer_entry_type(p):
    if p.get('arxivId'):
        return 'preprint'
    doi = (p.get('doi') or '').lower()
    landing = (p.get('landingPage') or '').lower()
    if 'acl' in doi or 'aclanthology' in landing or 'conference' in landing:
        return 'conference-paper'
    if doi:
        return 'journal-article'
    return 'other'


def format_citation(entry, style):
    authors = entry.get('authors', [])
    year = entry.get('year') or 'n.d.'
    title = entry.get('title', '')
    doi = entry.get('doi', '')
    arxiv = entry.get('arxivId', '')
    url = entry.get('url', '') or entry.get('pdfUrl', '')
    if style.upper().startswith('GB'):
        a = format_authors_gbt(authors)
        if doi:
            return f"{a}. {title}[J]. {year}. DOI: {doi}."
        if arxiv:
            return f"{a}. {title}[EB/OL]. arXiv:{arxiv}, {year}. {url}".strip()
        return f"{a}. {title}. {year}. {url}".strip()
    else:
        a = format_authors_apa(authors)
        if doi:
            return f"{a} ({year}). {title}. https://doi.org/{doi}" if not doi.startswith('http') else f"{a} ({year}). {title}. {doi}"
        if arxiv:
            return f"{a} ({year}). {title}. arXiv:{arxiv}. {url}".strip()
        return f"{a} ({year}). {title}. {url}".strip()


def build_pack(screening: dict, shortlist: dict, style: str):
    keep_titles = {a.get('title','') for a in screening.get('accepted', [])}
    shortlist_map = {p.get('title',''): p for p in shortlist.get('papers', [])}
    entries = []
    for i, title in enumerate(keep_titles, 1):
        p = shortlist_map.get(title)
        if not p:
            continue
        entry = {
            'id': f'R{i}',
            'title': p.get('title',''),
            'authors': p.get('authors',[]),
            'year': p.get('year'),
            'doi': p.get('doi',''),
            'arxivId': p.get('arxivId',''),
            'url': p.get('landingPage',''),
            'pdfUrl': p.get('pdfUrl',''),
            'citationCount': p.get('citationCount'),
            'entryType': infer_entry_type(p),
            'status': 'core',
            'notes': p.get('relevanceNote',''),
            'formattedCitation': ''
        }
        entry['formattedCitation'] = format_citation(entry, style)
        entries.append(entry)

    entries = sorted(entries, key=lambda e: ((e.get('citationCount') or 0), e.get('year') or 0), reverse=True)
    for idx, e in enumerate(entries, 1):
        e['id'] = f'R{idx}'

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
        import subprocess
        subprocess.run([
            'python3',
            str(Path(__file__).resolve().parent / 'render_reference_pack.py'),
            '--input', args.out_json,
            '--out-md', args.out_md,
        ], check=True)


if __name__ == '__main__':
    main()
