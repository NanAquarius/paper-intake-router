#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_intake_router.paths import skill_script

COMMANDS = {
    'parse-intake': 'parse_intake_text.py',
    'build-task': 'build_task_sheet.py',
    'init-workspace': 'init_task_workspace.py',
    'detect-capabilities': 'detect_capabilities.py',
    'next-actions': 'next_actions.py',
    'build-figure-plan': 'build_figure_table_plan.py',
    'generate-figure-codegen': 'generate_figure_table_codegen.py',
    'validate-figure-refs': 'validate_figure_table_refs.py',
    'autofix-figure-refs': 'autofix_figure_table_refs.py',
    'enforce-final-gate': 'enforce_final_gate.py',
    'build-reference-shortlist': 'build_reference_shortlist.py',
    'build-reference-screening': 'build_reference_screening.py',
    'build-reference-pack': 'build_reference_pack.py',
    'build-writing-evidence-pack': 'build_writing_evidence_pack.py',
    'build-citation-plan': 'build_citation_plan.py',
    'build-chapter-writing-pack': 'build_chapter_writing_pack.py',
    'inject-inline-citations': 'inject_inline_citations.py',
    'render-final-citations': 'render_final_citations.py',
    'smoke-test': 'smoke_test_pipeline.py',
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Unified CLI for paper-intake-router workflow scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Available commands:\n  ' + '\n  '.join(sorted(COMMANDS.keys())),
    )
    parser.add_argument('command', help='Workflow command to run')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments forwarded to the underlying script')
    ns = parser.parse_args()

    script_name = COMMANDS.get(ns.command)
    if not script_name:
        parser.error(f'Unknown command: {ns.command}')

    script = skill_script(REPO_ROOT, script_name)
    forwarded = list(ns.args)
    if forwarded and forwarded[0] == '--':
        forwarded = forwarded[1:]

    result = subprocess.run([sys.executable, str(script), *forwarded])
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
