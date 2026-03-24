#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description='Generate standard reference-stage output paths')
    ap.add_argument('--base-dir', required=True)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()

    base = Path(args.base_dir)
    base.mkdir(parents=True, exist_ok=True)
    data = {
        'referenceShortlistJson': str(base / 'references-shortlist.json'),
        'referenceShortlistMd': str(base / 'references-shortlist.md'),
        'referenceScreeningJson': str(base / 'reference-screening.json'),
        'referenceScreeningMd': str(base / 'reference-screening.md'),
        'referencePackJson': str(base / 'reference-pack.json'),
        'referencePackMd': str(base / 'reference-pack.md')
    }
    Path(args.out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)


if __name__ == '__main__':
    main()
