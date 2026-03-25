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


def build_screening(shortlist: dict) -> dict:
    papers = shortlist.get('papers', [])
    included = []
    excluded = []
    warnings = []

    for paper in papers:
        title = paper.get('title', '')
        evidence_type = paper.get('evidenceType', 'method')
        weak = paper.get('needsVerification', False)
        if not title.strip():
            continue
        if evidence_type == 'survey' or evidence_type == 'canonical' or paper.get('rank', 999) <= 6:
            included.append({
                'title': title,
                'decision': 'keep',
                'reason': '高相关或高价值证据，保留进入 reference pack。',
                'evidenceType': evidence_type,
            })
        else:
            excluded.append({
                'title': title,
                'decision': 'drop',
                'reason': '相对次要，优先级不足。',
                'evidenceType': evidence_type,
            })
        if weak:
            warnings.append({'title': title, 'warning': '缺少 DOI/arXiv 等稳定标识，建议人工复核。'})

    summary = {
        'inputCount': len(papers),
        'keepCount': len(included),
        'dropCount': len(excluded),
        'warningCount': len(warnings),
        'coverage': {
            'hasSurvey': any(i.get('evidenceType') == 'survey' for i in included),
            'hasRecent': any((p.get('year') or 0) >= datetime.now().year - 2 for p in papers),
            'hasCanonical': any(i.get('evidenceType') == 'canonical' for i in included),
        }
    }

    if not summary['coverage']['hasSurvey']:
        warnings.append({'title': 'survey-gap', 'warning': '当前 shortlist 缺少综述类文献，建议触发 query reformulation。'})
    if not summary['coverage']['hasRecent']:
        warnings.append({'title': 'recent-gap', 'warning': '当前 shortlist 缺少近 2 年文献，建议补检索。'})

    return {
        'topic': shortlist.get('topic', ''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'summary': summary,
        'included': included,
        'excluded': excluded,
        'warnings': warnings,
    }


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
        run_python_script(
            skill_script(REPO_ROOT, 'render_reference_screening.py'),
            '--input', str(out_json),
            '--out-md', args.out_md,
        )


if __name__ == '__main__':
    main()
