#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_intake_router.paths import run_python_script, skill_script

STOPWORDS = {
    'a', 'an', 'the', 'of', 'for', 'in', 'on', 'to', 'and', 'or', 'with', 'without', 'from', 'by', 'using', 'based',
    'study', 'studies', 'paper', 'method', 'methods', 'framework', 'frameworks', 'approach', 'approaches',
    'analysis', 'models', 'model', 'large', 'language', 'llm', 'llms'
}


def run_cmd(args: list[str]) -> str:
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return p.stdout.strip()


def safe_json_call(args: list[str]) -> Any:
    out = run_cmd(args)
    return json.loads(out)


def normalize_title(title: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', (title or '').lower())).strip()


def title_signature(title: str) -> str:
    nt = normalize_title(title)
    toks = [t for t in nt.split() if t and t not in STOPWORDS]
    return ' '.join(toks[:8])


def extract_arxiv_id(text: str) -> str:
    if not text:
        return ''
    m = re.search(r'arxiv(?:\.org/(?:abs|pdf)/|\.)([0-9]{4}\.[0-9]{4,5})(?:v\d+)?', text, re.I)
    if m:
        return m.group(1)
    return ''


def significant_terms(topic: str) -> list[str]:
    words = [w for w in normalize_title(topic).split() if len(w) >= 4 and w not in STOPWORDS]
    seen = set()
    out = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def keyword_overlap(title: str, topic_terms: list[str]) -> int:
    nt = normalize_title(title)
    return sum(1 for t in topic_terms if t in nt)


def parse_openalex(topic: str, per_page: int = 12) -> list[dict]:
    args = [
        'mcporter', 'call', 'openalex.search_works', '--args', json.dumps({
            'search': topic,
            'select': 'id,title,display_name,authorships,publication_year,doi,open_access,primary_location,cited_by_count,type',
            'per_page': per_page,
            'view': 'summary'
        }, ensure_ascii=False)
    ]
    data = safe_json_call(args)
    items = []
    for r in data.get('results', []):
        title = r.get('title') or r.get('display_name', '')
        if not title.strip():
            continue
        doi = r.get('doi') or ''
        if doi.startswith('https://doi.org/'):
            doi = doi.replace('https://doi.org/', '')
        primary = r.get('primary_location') or {}
        oa = r.get('open_access') or {}
        landing = primary.get('landing_page_url') or ''
        arxiv_id = extract_arxiv_id(doi) or extract_arxiv_id(landing) or extract_arxiv_id(primary.get('pdf_url') or '')
        items.append({
            'title': title,
            'authors': [a.get('author', {}).get('display_name', '') for a in r.get('authorships', []) if a.get('author', {}).get('display_name')],
            'year': r.get('publication_year'),
            'doi': doi,
            'arxivId': arxiv_id,
            'landingPage': landing,
            'pdfUrl': primary.get('pdf_url') or oa.get('oa_url') or '',
            'citationCount': r.get('cited_by_count'),
            'source': 'openalex',
            'openAccess': oa.get('is_oa'),
            'entryType': r.get('type', ''),
            'raw': r,
        })
    return items


def parse_semantic(topic: str, limit: int = 10) -> list[dict]:
    args = [
        'mcporter', 'call', 'semantic-scholar.search_paper', '--args', json.dumps({
            'query': topic,
            'limit': limit,
            'fields': 'paperId,title,authors,year,citationCount,publicationDate,url,openAccessPdf'
        }, ensure_ascii=False)
    ]
    data = safe_json_call(args)
    results = data.get('data', []) if isinstance(data, dict) else data
    items = []
    for r in results:
        title = r.get('title', '')
        if not title.strip():
            continue
        pdf = (r.get('openAccessPdf') or {}).get('url', '') if isinstance(r.get('openAccessPdf'), dict) else ''
        url = r.get('url') or ''
        arxiv = extract_arxiv_id(pdf or url)
        items.append({
            'title': title,
            'authors': [a.get('name', '') for a in r.get('authors', []) if a.get('name')],
            'year': r.get('year'),
            'doi': '',
            'arxivId': arxiv,
            'landingPage': url,
            'pdfUrl': pdf,
            'citationCount': r.get('citationCount'),
            'source': 'semantic-scholar',
            'openAccess': bool(pdf),
            'entryType': 'paper',
            'raw': r,
        })
    return items


def parse_research_papers(topic: str, max_results: int = 6) -> list[dict]:
    args = [
        'mcporter', 'call', 'research-papers.search_papers', '--args', json.dumps({
            'query': topic,
            'max_results': max_results
        }, ensure_ascii=False)
    ]
    out = run_cmd(args)
    blocks = [b.strip() for b in out.split('\n---\n') if b.strip()]
    items = []
    for b in blocks:
        title = authors = arxiv_id = date = abs_link = pdf_link = ''
        for line in b.splitlines():
            if line.startswith('Title: '):
                title = line.replace('Title: ', '', 1).strip()
            elif line.startswith('Authors: '):
                authors = line.replace('Authors: ', '', 1).strip()
            elif line.startswith('arXiv ID: '):
                arxiv_id = line.replace('arXiv ID: ', '', 1).strip()
            elif line.startswith('Published Date: '):
                date = line.replace('Published Date: ', '', 1).strip()
            elif line.startswith('Abstract Link: '):
                abs_link = line.replace('Abstract Link: ', '', 1).strip()
            elif line.startswith('PDF Link: '):
                pdf_link = line.replace('PDF Link: ', '', 1).strip()
        if not title.strip():
            continue
        year = None
        if date[:4].isdigit():
            year = int(date[:4])
        items.append({
            'title': title,
            'authors': [a.strip() for a in authors.split(',') if a.strip()],
            'year': year,
            'doi': '',
            'arxivId': extract_arxiv_id(arxiv_id) or extract_arxiv_id(abs_link) or extract_arxiv_id(pdf_link),
            'landingPage': abs_link,
            'pdfUrl': pdf_link,
            'citationCount': None,
            'source': 'research-papers',
            'openAccess': bool(pdf_link),
            'entryType': 'preprint',
            'raw': {'date': date},
        })
    return items


def classify_evidence(title: str, year: int | None, citation_count: int | None, current_year: int) -> str:
    t = (title or '').lower()
    if 'survey' in t or 'review' in t:
        return 'survey'
    if citation_count and citation_count >= 1000:
        return 'canonical'
    if year and year >= current_year - 2:
        return 'recent'
    if any(k in t for k in ['method', 'framework', 'attention', 'transformer', 'algorithm', 'reward', 'alignment']):
        return 'method'
    if any(k in t for k in ['application', 'benchmark', 'evaluation']):
        return 'application'
    return 'method'


def score_item(item: dict, topic: str, topic_terms: list[str], current_year: int) -> float:
    title = item.get('title', '')
    norm_title = normalize_title(title)
    norm_topic = normalize_title(topic)
    overlap = keyword_overlap(title, topic_terms)
    score = 0.0
    if norm_topic and norm_topic in norm_title:
        score += 8
    score += overlap * 3
    citations = item.get('citationCount') or 0
    score += min(citations / 200.0, 20)
    year = item.get('year')
    if year:
        if year >= current_year - 2:
            score += 4
        elif year >= current_year - 5:
            score += 2
    if item.get('pdfUrl'):
        score += 1
    if item.get('doi'):
        score += 1
    if item.get('source') == 'semantic-scholar':
        score += 0.5
    if overlap == 0 and norm_topic not in norm_title:
        score -= 12
    return score


def dedupe(items: list[dict]) -> tuple[list[dict], list[dict]]:
    seen = {}
    kept = []
    excluded = []
    for item in items:
        title = item.get('title', '')
        if not title.strip():
            continue
        sig = title_signature(title)
        year = item.get('year') or ''
        key = (f"{sig}:{year}" if sig else '') or item.get('arxivId') or item.get('doi') or normalize_title(title)
        prev = seen.get(key)
        if prev is None:
            seen[key] = item
            kept.append(item)
        else:
            prev_score = prev.get('_score', 0)
            new_score = item.get('_score', 0)
            if new_score > prev_score:
                kept.remove(prev)
                kept.append(item)
                seen[key] = item
                excluded.append({'title': prev.get('title', ''), 'reason': 'duplicate'})
            else:
                excluded.append({'title': item.get('title', ''), 'reason': 'duplicate'})
    return kept, excluded


def build_shortlist(topic: str, target_count: int = 8) -> dict:
    current_year = datetime.now().year
    topic_terms = significant_terms(topic)
    all_items = []
    sources_used = []
    excluded = []

    for source_name, loader in [
        ('openalex', lambda: parse_openalex(topic, per_page=max(target_count + 4, 12))),
        ('semantic-scholar', lambda: parse_semantic(topic, limit=max(target_count + 2, 10))),
        ('research-papers', lambda: parse_research_papers(topic, max_results=max(target_count, 6))),
    ]:
        try:
            batch = loader()
            all_items.extend(batch)
            sources_used.append(source_name)
        except Exception as exc:
            excluded.append({'title': source_name, 'reason': f'source_error: {exc}'})

    scored = []
    for item in all_items:
        title = item.get('title', '')
        if not title.strip():
            continue
        overlap = keyword_overlap(title, topic_terms)
        norm_topic = normalize_title(topic)
        norm_title = normalize_title(title)
        item['evidenceType'] = classify_evidence(title, item.get('year'), item.get('citationCount'), current_year)
        item['_score'] = score_item(item, topic, topic_terms, current_year)
        item['relevanceNote'] = '题目相关，且元数据较完整。' if overlap > 0 or norm_topic in norm_title else '相关性偏弱，建议人工复核。'
        item['needsVerification'] = not bool(item.get('doi') or item.get('arxivId'))
        if topic_terms and overlap == 0 and norm_topic not in norm_title:
            excluded.append({'title': title, 'reason': 'weak_match'})
            continue
        scored.append(item)

    deduped, dup_excluded = dedupe(scored)
    excluded.extend(dup_excluded)
    deduped.sort(key=lambda x: x.get('_score', 0), reverse=True)
    selected = deduped[:target_count]

    papers = []
    for i, item in enumerate(selected, start=1):
        papers.append({
            'rank': i,
            'title': item.get('title', ''),
            'authors': item.get('authors', []),
            'year': item.get('year'),
            'doi': item.get('doi', ''),
            'arxivId': item.get('arxivId', ''),
            'landingPage': item.get('landingPage', ''),
            'pdfUrl': item.get('pdfUrl', ''),
            'citationCount': item.get('citationCount'),
            'source': item.get('source', ''),
            'relevanceNote': item.get('relevanceNote', ''),
            'evidenceType': item.get('evidenceType', 'method'),
            'openAccess': item.get('openAccess'),
            'needsVerification': item.get('needsVerification', False)
        })
    return {
        'topic': topic,
        'queries': [topic],
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'sourcesUsed': sources_used,
        'selectionPolicy': {
            'targetCount': target_count,
            'mustIncludeRecentYears': 3,
            'preferCanonical': True,
            'preferOpenAccess': True,
        },
        'papers': papers,
        'excluded': excluded,
    }


def main():
    ap = argparse.ArgumentParser(description='Build reference shortlist from academic paper MCPs')
    ap.add_argument('--topic', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    ap.add_argument('--target-count', type=int, default=8)
    args = ap.parse_args()

    data = build_shortlist(args.topic, args.target_count)
    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out_json)
    if args.out_md:
        run_python_script(
            skill_script(REPO_ROOT, 'render_reference_shortlist.py'),
            '--input', str(out_json),
            '--out-md', args.out_md,
        )


if __name__ == '__main__':
    main()
    raw_items = []
    sources_used = []

    for fn, name in [
        (lambda: parse_openalex(topic), 'openalex'),
        (lambda: parse_semantic(topic), 'semantic-scholar'),
        (lambda: parse_research_papers(topic), 'research-papers'),
    ]:
        try:
            batch = fn()
            if batch:
                sources_used.append(name)
                raw_items.extend(batch)
        except Exception:
            continue

    excluded = []
    filtered_items = []
    for item in raw_items:
        title = item.get('title', '')
        if not title.strip():
            continue
        overlap = keyword_overlap(title, topic_terms)
        norm_topic = normalize_title(topic)
        norm_title = normalize_title(title)
        item['evidenceType'] = classify_evidence(title, item.get('year'), item.get('citationCount'), current_year)
        item['_score'] = score_item(item, topic, topic_terms, current_year)
        item['relevanceNote'] = '题目相关，且元数据较完整。'
        item['needsVerification'] = not bool(item.get('doi') or item.get('arxivId'))
        if topic_terms and overlap == 0 and norm_topic not in norm_title:
            excluded.append({'title': title, 'reason': 'weak_match'})
            continue
        filtered_items.append(item)

    deduped, dup_excluded = dedupe(filtered_items)
    excluded.extend(dup_excluded)
    ranked = sorted(deduped, key=lambda x: (x.get('_score', 0), x.get('citationCount') or 0, x.get('year') or 0), reverse=True)
    papers = []
    for i, item in enumerate(ranked[:target_count], 1):
        papers.append({
            'rank': i,
            'title': item.get('title', ''),
            'authors': item.get('authors', []),
            'year': item.get('year'),
            'doi': item.get('doi', ''),
            'arxivId': item.get('arxivId', ''),
            'landingPage': item.get('landingPage', ''),
            'pdfUrl': item.get('pdfUrl', ''),
            'citationCount': item.get('citationCount'),
            'source': item.get('source', ''),
            'relevanceNote': item.get('relevanceNote', ''),
            'evidenceType': item.get('evidenceType', 'method'),
            'openAccess': item.get('openAccess'),
            'needsVerification': item.get('needsVerification', False)
        })
    return {
        'topic': topic,
        'queries': [topic],
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'sourcesUsed': sources_used,
        'selectionPolicy': {
            'targetCount': target_count,
            'mustIncludeRecentYears': 3,
            'preferCanonical': True,
            'preferOpenAccess': True,
        },
        'papers': papers,
        'excluded': excluded,
    }


def main():
    ap = argparse.ArgumentParser(description='Build reference shortlist from academic paper MCPs')
    ap.add_argument('--topic', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    ap.add_argument('--target-count', type=int, default=8)
    args = ap.parse_args()

    data = build_shortlist(args.topic, args.target_count)
    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out_json)
    if args.out_md:
        subprocess.run([
            'python3',
            str(Path(__file__).resolve().parent / 'render_reference_shortlist.py'),
            '--input', str(out_json),
            '--out-md', args.out_md,
        ], check=True)


if __name__ == '__main__':
    main()
