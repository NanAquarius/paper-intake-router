#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

BOOTSTRAP_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(BOOTSTRAP_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(BOOTSTRAP_REPO_ROOT))

from paper_intake_router.paths import repo_root_from_file, run_python_script, skill_script

REPO_ROOT = repo_root_from_file(__file__)
WORK = Path(tempfile.mkdtemp(prefix='paper-router-smoke-'))


def main() -> None:
    intake = WORK / 'intake.json'
    task = WORK / 'task.json'
    workspace_json = WORK / 'workspace.json'
    plan = WORK / 'figure-plan.json'
    validation = WORK / 'figure-validation.json'
    draft = WORK / 'draft.md'
    fixed = WORK / 'fixed.md'
    citation_plan = WORK / 'citation-plan.json'
    reference_pack = WORK / 'reference-pack.json'
    profile = WORK / 'profile.json'
    final = WORK / 'final.md'

    intake.write_text(json.dumps({
        'paperType': 'degree',
        'degreeLevel': 'master',
        'discipline': 'computer-science',
        'topic': '基于多模态检索增强生成的领域问答系统研究',
        'style': 'GB/T 7714',
        'targetWords': 25000,
        'language': 'zh',
        'deliveryGoal': 'pdf_with_sources'
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    citation_plan.write_text(json.dumps({
        'chapters': [
            {'chapter': 'experiments', 'claims': [
                {'claimType': 'baseline comparison', 'recommendedCitations': ['lee2024benchmark'], 'inlineMarker': '[2]'}
            ]}
        ]
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    reference_pack.write_text(json.dumps({
        'entries': [
            {'id': 'lee2024benchmark', 'authors': ['Lee'], 'year': 2024}
        ]
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    profile.write_text(json.dumps({
        'style': 'GB/T 7714',
        'profile': 'cn-thesis-brackets',
        'bracketStyle': 'square',
        'zhPunctuationMode': 'fullwidth',
        'apaParenModeZh': 'fullwidth'
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    run_python_script(skill_script(REPO_ROOT, 'build_task_sheet.py'), '--input', str(intake), '--out-json', str(task))
    run_python_script(skill_script(REPO_ROOT, 'init_task_workspace.py'), '--base-dir', str(WORK / 'runs'), '--task', str(task), '--out-json', str(workspace_json))
    run_python_script(skill_script(REPO_ROOT, 'build_figure_table_plan.py'), '--task', str(task), '--citation-plan', str(citation_plan), '--out-json', str(plan))

    draft.write_text('表 4-1 显示实验结果。\n', encoding='utf-8')
    run_python_script(skill_script(REPO_ROOT, 'autofix_figure_table_refs.py'), '--plan', str(plan), '--draft', str(draft), '--citation-mode', 'internal-anchor', '--out', str(fixed))
    run_python_script(skill_script(REPO_ROOT, 'validate_figure_table_refs.py'), '--plan', str(plan), '--draft', str(fixed), '--out-json', str(validation))
    run_python_script(skill_script(REPO_ROOT, 'render_final_citations.py'), '--draft', str(fixed), '--reference-pack', str(reference_pack), '--citation-plan', str(citation_plan), '--citation-profile-json', str(profile), '--style', 'GB/T 7714', '--out', str(final))

    rendered = final.read_text(encoding='utf-8')
    validation_data = json.loads(validation.read_text(encoding='utf-8'))
    workspace_data = json.loads(workspace_json.read_text(encoding='utf-8'))

    if '[1]' not in rendered and '[2]' not in rendered:
        raise SystemExit(f'Smoke test failed: expected rendered citation marker in final output, got:\n{rendered}')
    if not workspace_data.get('paths', {}).get('drafts'):
        raise SystemExit(f'Smoke test failed: workspace manifest missing drafts path: {workspace_data}')
    if validation_data.get('summary', {}).get('bodyLabelCount', 0) < 1:
        raise SystemExit(f'Smoke test failed: validation did not detect any body labels: {validation_data}')

    print(json.dumps({
        'ok': True,
        'workdir': str(WORK),
        'workspaceRoot': workspace_data.get('paths', {}).get('root'),
        'validationSummary': validation_data.get('summary', {}),
        'final': rendered,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run local smoke test for paper-intake-router core workflow')
    parser.add_argument('--json', action='store_true', help='Retained for compatibility; output is JSON by default')
    parser.parse_args()
    main()
