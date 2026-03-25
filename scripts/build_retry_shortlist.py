#!/usr/bin/env python3
import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_intake_router.paths import import_module_from_path, skill_script

ROOT = REPO_ROOT / 'scripts'
SHORTLIST_PATH = skill_script(REPO_ROOT, 'build_reference_shortlist.py')


def load_shortlist_module():
    return import_module_from_path('build_reference_shortlist', SHORTLIST_PATH)


def main():
    ap = argparse.ArgumentParser(description='Execute second-round reference search from retry plan and merge results')
    ap.add_argument('--base-shortlist', required=True)
    ap.add_argument('--retry-plan', required=True)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()

    base = json.loads(Path(args.base_shortlist).read_text(encoding='utf-8'))
    retry = json.loads(Path(args.retry_plan).read_text(encoding='utf-8'))

    if not retry.get('retryNeeded'):
        Path(args.out_json).write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding='utf-8')
        print(args.out_json)
        return

    mod = load_shortlist_module()
    combined_items = []
    base_topic = base.get('topic', '')

    for p in base.get('papers', []):
        combined_items.append({
            'title': p.get('title', ''),
            'authors': p.get('authors', []),
            'year': p.get('year'),
            'doi': p.get('doi', ''),
            'arxivId': p.get('arxivId', ''),
            'landingPage': p.get('landingPage', ''),
            'pdfUrl': p.get('pdfUrl', ''),
            'citationCount': p.get('citationCount'),
            'source': p.get('source', ''),
            'openAccess': p.get('openAccess'),
            'entryType': '',
            'raw': {},
            'relevanceNote': p.get('relevanceNote', ''),
            'needsVerification': p.get('needsVerification', False),
            'evidenceType': p.get('evidenceType', 'method'),
            '_queryKind': 'base'
        })

    current_year = datetime.now().year
    topic_terms = mod.significant_terms(base_topic)
    used_queries = [base_topic]
    excluded = list(base.get('excluded', []))
    sources_used = list(base.get('sourcesUsed', []))

    for qobj in retry.get('queries', []):
        q = qobj.get('query', '') if isinstance(qobj, dict) else str(qobj)
        kind = qobj.get('kind', 'broaden') if isinstance(qobj, dict) else 'broaden'
        if not q:
            continue
        used_queries.append(q)
        data = mod.build_shortlist(q, target_count=8)
        excluded.extend(data.get('excluded', []))
        for s in data.get('sourcesUsed', []):
            if s not in sources_used:
                sources_used.append(s)
        for p in data.get('papers', []):
            combined_items.append({
                'title': p.get('title', ''),
                'authors': p.get('authors', []),
                'year': p.get('year'),
                'doi': p.get('doi', ''),
                'arxivId': p.get('arxivId', ''),
                'landingPage': p.get('landingPage', ''),
                'pdfUrl': p.get('pdfUrl', ''),
                'citationCount': p.get('citationCount'),
                'source': p.get('source', ''),
                'openAccess': p.get('openAccess'),
                'entryType': '',
                'raw': {},
                'relevanceNote': p.get('relevanceNote', ''),
                'needsVerification': p.get('needsVerification', False),
                'evidenceType': p.get('evidenceType', 'method'),
                '_queryKind': kind
            })

    filtered = []
    for item in combined_items:
        title = item.get('title', '')
        if not title.strip():
            continue
        overlap = mod.keyword_overlap(title, topic_terms)
        norm_topic = mod.normalize_title(base_topic)
        norm_title = mod.normalize_title(title)
        item['evidenceType'] = mod.classify_evidence(title, item.get('year'), item.get('citationCount'), current_year)
        item['_score'] = mod.score_item(item, base_topic, topic_terms, current_year)
        if item.get('_queryKind') == 'survey':
            if any(k in title.lower() for k in ['survey', 'review', 'taxonomy', 'tutorial', 'overview', 'challenges']):
                item['_score'] += 10
                item['evidenceType'] = 'survey'
                item['relevanceNote'] = '综述专项回捞命中，优先保留。'
        else:
            item['relevanceNote'] = item.get('relevanceNote') or '题目相关，且元数据较完整。'
        item['needsVerification'] = item.get('needsVerification', False) or not bool(item.get('doi') or item.get('arxivId'))
        if topic_terms and overlap == 0 and norm_topic not in norm_title and item.get('_queryKind') != 'survey':
            excluded.append({'title': title, 'reason': 'weak_match'})
            continue
        filtered.append(item)

    deduped, dup_excluded = mod.dedupe(filtered)
    excluded.extend(dup_excluded)

    for item in deduped:
        item.pop('_queryKind', None)
        item.pop('_score', None)

    result = {
        'topic': base_topic,
        'queries': used_queries,
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'sourcesUsed': sources_used,
        'selectionPolicy': base.get('selectionPolicy', {}),
        'papers': deduped[: max(len(base.get('papers', [])), 8)],
        'excluded': excluded,
    }

    Path(args.out_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)


if __name__ == '__main__':
    main()
