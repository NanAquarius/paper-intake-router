#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path

CHAPTER_GOALS = {
    'introduction': '交代研究背景、问题重要性与本文切入点。',
    'related-work': '梳理相关研究脉络，说明本文与既有工作的关系。',
    'methods': '说明方法选择、设计动机与技术路线。',
    'experiments': '解释实验设置、结果对比与发现。',
    'discussion': '讨论风险、局限、边界条件与未来工作。',
}

CLAIM_INSTRUCTIONS = {
    'problem framing': '先交代问题背景，再用引用说明该问题为何重要、为何值得研究。',
    'baseline comparison': '用引用说明主流基线是什么，再说明本文方案相对基线的差异。',
    'method choice': '解释为何采用该方法或训练范式，并用引用支撑方法选择的合理性。',
    'result interpretation': '解释结果意味着什么，引用实验/评测类文献帮助比较与归因。',
    'risk discussion': '明确指出风险、局限或失败模式，并用引用支撑这些担忧不是主观猜测。',
}


def build_pack(evidence_pack: dict, citation_plan: dict) -> dict:
    plan_map = {
        ch.get('chapter', ''): {c.get('claimType', ''): c for c in ch.get('claims', [])}
        for ch in citation_plan.get('chapters', [])
    }
    chapters_out = []
    for ch in evidence_pack.get('chapters', []):
        chapter = ch.get('chapter', '')
        prompts = []
        for item in ch.get('items', []):
            ctype = item.get('bestArgumentFit', 'method choice')
            claim_plan = plan_map.get(chapter, {}).get(ctype, {})
            prompts.append({
                'claimType': ctype,
                'instruction': CLAIM_INSTRUCTIONS.get(ctype, '围绕该论点写作，并用给定引用支撑关键判断。'),
                'recommendedCitations': claim_plan.get('recommendedCitations', []),
                'inlineMarker': claim_plan.get('inlineMarker', ''),
                'useThesePapersFor': item.get('canSupportClaim', []),
                'avoid': item.get('riskIfOverused', ''),
            })
        merged = {}
        for p in prompts:
            key = p['claimType']
            if key not in merged:
                merged[key] = p
            else:
                merged[key]['recommendedCitations'] = list(dict.fromkeys(merged[key]['recommendedCitations'] + p['recommendedCitations']))[:3]
                merged[key]['useThesePapersFor'] = list(dict.fromkeys(merged[key]['useThesePapersFor'] + p['useThesePapersFor']))
                if not merged[key]['avoid']:
                    merged[key]['avoid'] = p['avoid']
        chapters_out.append({
            'chapter': chapter,
            'writingGoal': CHAPTER_GOALS.get(chapter, '围绕本章目标组织论证。'),
            'prompts': list(merged.values())
        })
    return {
        'topic': evidence_pack.get('topic', ''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'chapters': chapters_out,
    }


def render_md(data: dict) -> str:
    lines = ['# Chapter-specific writing prompt pack', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append('')
    for ch in data.get('chapters', []):
        lines.append(f"## {ch.get('chapter','')}")
        lines.append('')
        lines.append(f"- Writing goal: {ch.get('writingGoal','')}")
        lines.append('')
        for i, p in enumerate(ch.get('prompts', []), 1):
            lines.append(f"### {i}. {p.get('claimType','')}")
            lines.append('')
            lines.append(f"- Instruction: {p.get('instruction','')}")
            lines.append(f"- Recommended citations: {', '.join(p.get('recommendedCitations', []))}")
            lines.append(f"- Inline marker: {p.get('inlineMarker','')}")
            uses = p.get('useThesePapersFor', [])
            if uses:
                lines.append('- Use these papers for:')
                for u in uses:
                    lines.append(f"  - {u}")
            lines.append(f"- Avoid: {p.get('avoid','')}")
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Build chapter-specific writing prompt packs from evidence pack + citation plan')
    ap.add_argument('--evidence-pack', required=True)
    ap.add_argument('--citation-plan', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()
    evidence = json.loads(Path(args.evidence_pack).read_text(encoding='utf-8'))
    plan = json.loads(Path(args.citation_plan).read_text(encoding='utf-8'))
    data = build_pack(evidence, plan)
    Path(args.out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)
    if args.out_md:
        Path(args.out_md).write_text(render_md(data), encoding='utf-8')
        print(args.out_md)


if __name__ == '__main__':
    main()
