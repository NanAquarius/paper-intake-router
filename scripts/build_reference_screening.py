#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def build_screening(shortlist: dict) -> dict:
    papers = shortlist.get('papers', [])
    accepted = []
    rejected = []
    warnings = []

    sorted_papers = sorted(papers, key=lambda p: ((p.get('citationCount') or 0), p.get('year') or 0), reverse=True)
    target = 8
    accepted = sorted_papers[:target]
    rejected_candidates = sorted_papers[target:]

    for p in rejected_candidates:
        rejected.append({
            'title': p.get('title', ''),
            'decision': 'drop',
            'reason': 'low_relevance'
        })

    survey_count = sum(1 for p in accepted if p.get('evidenceType') == 'survey')
    method_count = sum(1 for p in accepted if p.get('evidenceType') == 'method')
    recent_count = sum(1 for p in accepted if (p.get('year') or 0) >= (datetime.now().year - 2))
    all_preprints = all((p.get('doi','') == '' and p.get('arxivId','')) or p.get('source') == 'research-papers' for p in accepted) if accepted else False

    if len(accepted) < target:
        warnings.append('core paper count below target')
    if survey_count < 1:
        warnings.append('survey count below minimum')
    if method_count < 1:
        warnings.append('method count below minimum')
    if recent_count < 3:
        warnings.append('recent paper count below minimum')
    if all_preprints:
        warnings.append('all candidates are preprints')

    out = {
        'topic': shortlist.get('topic', ''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'selectionRules': {
            'targetCoreCount': 8,
            'minRecentYears': 3,
            'allowPreprints': True,
            'mustExplainExclusions': True,
            'minSurveyCount': 1,
            'minMethodCount': 1,
            'minRecentCount': 3,
            'requireCanonicalWhenAvailable': True,
            'warnIfAllPreprints': True,
        },
        'accepted': [
            {
                'rank': i,
                'title': p.get('title', ''),
                'decision': 'keep',
                'reason': p.get('relevanceNote', '') or 'high score',
                'bucket': p.get('evidenceType', 'method')
            }
            for i, p in enumerate(accepted, 1)
        ],
        'rejected': rejected,
        'warnings': warnings,
    }
    return out


def main():
    ap = argparse.ArgumentParser(description='Build reference screening decision from shortlist')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()

    shortlist = json.loads(Path(args.input).read_text(encoding='utf-8'))
    screening = build_screening(shortlist)
    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(screening, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out_json)
    if args.out_md:
        import subprocess
        subprocess.run([
            'python3',
            str(Path(__file__).resolve().parent / 'render_reference_screening.py'),
            '--input', str(out_json),
            '--out-md', args.out_md,
        ], check=True)


if __name__ == '__main__':
    main()
