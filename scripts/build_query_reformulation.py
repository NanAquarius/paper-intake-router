#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def build_reformulation(screening: dict) -> dict:
    topic = screening.get('topic', '')
    warnings = screening.get('warnings', [])
    suggestions = []

    if 'core paper count below target' in warnings:
        suggestions.append({
            'kind': 'broaden',
            'query': topic + ' RLHF OR reward model alignment',
            'reason': '核心文献数量不足，先扩大相关主题范围'
        })
    if 'survey count below minimum' in warnings:
        suggestions.append({
            'kind': 'survey',
            'query': topic + ' survey OR review OR taxonomy OR tutorial OR overview OR challenges',
            'reason': '缺少综述论文，优先补 survey/review/taxonomy/tutorial/overview/challenges'
        })
        suggestions.append({
            'kind': 'survey',
            'query': topic + ' OR reward hacking OR RLHF OR preference optimization survey OR review',
            'reason': '尝试上位概念回捞综述论文'
        })
    if 'recent paper count below minimum' in warnings:
        suggestions.append({
            'kind': 'recent',
            'query': topic + ' 2023 OR 2024 OR 2025',
            'reason': '近三年论文不足，优先补最新文献'
        })
    if 'method count below minimum' in warnings:
        suggestions.append({
            'kind': 'method',
            'query': topic + ' method OR algorithm OR framework',
            'reason': '方法论文不足，补方法类关键词'
        })
    if 'all candidates are preprints' in warnings:
        suggestions.append({
            'kind': 'canonical',
            'query': topic + ' doi OR conference OR journal',
            'reason': '当前几乎全是预印本，优先补正式发表版本'
        })

    return {
        'topic': topic,
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'triggeredBy': warnings,
        'suggestions': suggestions,
    }


def main():
    ap = argparse.ArgumentParser(description='Build next-round query reformulation suggestions from screening warnings')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()
    screening = json.loads(Path(args.input).read_text(encoding='utf-8'))
    data = build_reformulation(screening)
    Path(args.out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)


if __name__ == '__main__':
    main()
