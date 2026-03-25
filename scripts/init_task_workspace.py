#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(text: str) -> str:
    text = (text or '').strip().lower()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'paper-task'


def load_task(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding='utf-8'))


def init_workspace(base_dir: Path, task: dict, task_slug: str | None) -> dict:
    title = task.get('topic') or task.get('title') or task.get('discipline') or 'paper-task'
    slug = slugify(task_slug or title)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%SZ')
    root = base_dir / f'{ts}-{slug}'

    paths = {
        'root': root,
        'intake': root / 'intake',
        'references': root / 'references',
        'evidence': root / 'evidence',
        'figures': root / 'figures',
        'tables': root / 'tables',
        'codegen': root / 'codegen',
        'data': root / 'data',
        'drafts': root / 'drafts',
        'final': root / 'final',
        'logs': root / 'logs',
    }

    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)

    manifest = {
        'createdAtUtc': datetime.now(timezone.utc).isoformat(),
        'taskTitle': title,
        'taskSlug': slug,
        'paths': {k: str(v) for k, v in paths.items()}
    }
    (root / 'workspace.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main():
    ap = argparse.ArgumentParser(description='Initialize a paper-intake-router task workspace')
    ap.add_argument('--base-dir', required=True)
    ap.add_argument('--task')
    ap.add_argument('--task-slug')
    ap.add_argument('--out-json')
    args = ap.parse_args()

    task = load_task(args.task)
    manifest = init_workspace(Path(args.base_dir), task, args.task_slug)
    if args.out_json:
        Path(args.out_json).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
