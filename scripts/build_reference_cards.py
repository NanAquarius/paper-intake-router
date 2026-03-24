#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def infer_chapter_fit(entry):
    t = (entry.get('title') or '').lower()
    if 'survey' in t or 'review' in t or 'taxonomy' in t or 'tutorial' in t:
        return 'related-work'
    if any(k in t for k in ['benchmark', 'evaluation', 'empirical', 'experiment']):
        return 'experiments'
    if any(k in t for k in ['discussion', 'challenge', 'limitation', 'risk']):
        return 'discussion'
    if any(k in t for k in ['method', 'framework', 'algorithm', 'optimization', 'alignment', 'reward']):
        return 'methods'
    return 'introduction'


def contribution_note(entry):
    t = entry.get('title','')
    et = entry.get('entryType','')
    if 'survey' in t.lower() or 'review' in t.lower():
        return '提供该主题的综述视角，可用于 related work 或问题定义。'
    if et == 'conference-paper':
        return '正式会议论文，适合作为方法或结果证据。'
    if et == 'preprint':
        return '预印本，但与主题高度相关，适合作为最新进展参考。'
    return '与当前主题直接相关，可作为核心参考文献。'


def infer_argument_fit(entry):
    t = (entry.get('title') or '').lower()
    if 'survey' in t or 'review' in t or 'taxonomy' in t or 'tutorial' in t:
        return 'problem framing'
    if any(k in t for k in ['benchmark', 'evaluation', 'empirical', 'experiment']):
        return 'result interpretation'
    if any(k in t for k in ['challenge', 'risk', 'limitation', 'mitigate', 'overoptimization', 'hacking']):
        return 'risk discussion'
    if any(k in t for k in ['method', 'framework', 'algorithm', 'optimization', 'alignment', 'reward']):
        return 'method choice'
    return 'baseline comparison'


def infer_supported_claims(entry):
    t = (entry.get('title') or '').lower()
    claims = []
    if 'survey' in t or 'review' in t or 'taxonomy' in t or 'tutorial' in t:
        claims.append('该方向已有系统性研究脉络')
    if any(k in t for k in ['reward', 'alignment', 'rlhf', 'preference']):
        claims.append('该论文可支撑奖励模型/偏好优化相关论述')
    if any(k in t for k in ['mitigate', 'risk', 'overoptimization', 'hacking']):
        claims.append('该论文可支撑风险、失败模式或缓解策略的论述')
    if any(k in t for k in ['benchmark', 'evaluation', 'empirical']):
        claims.append('该论文可支撑实验比较或经验结果解释')
    return claims or ['该论文可支撑与主题直接相关的核心论点']


def infer_risk(entry):
    et = entry.get('entryType','')
    t = (entry.get('title') or '').lower()
    if et == 'preprint':
        return '预印本证据强度弱于正式发表版本，正文中不宜承担唯一关键论据。'
    if 'survey' in t or 'review' in t:
        return '适合概览，不宜替代方法细节或实验细节证据。'
    if (entry.get('citationCount') or 0) < 3:
        return '引用较少，适合作为补充证据，不宜单独支撑强结论。'
    return '适合支撑核心论点，但最好与同主题另一篇文献交叉印证。'


def build_cards(pack):
    cards = []
    for e in pack.get('entries', []):
        key = e.get('doi') or e.get('arxivId') or e.get('id') or ''
        cards.append({
            'title': e.get('title',''),
            'whyKeep': e.get('notes','') or '与主题高度相关。',
            'mainContribution': contribution_note(e),
            'bestChapterFit': infer_chapter_fit(e),
            'bestArgumentFit': infer_argument_fit(e),
            'canSupportClaim': infer_supported_claims(e),
            'riskIfOverused': infer_risk(e),
            'supportingQuote': '',
            'citationKey': key,
            'sourceUrl': e.get('url') or e.get('pdfUrl') or ''
        })
    return {
        'topic': pack.get('topic',''),
        'generatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'cards': cards
    }


def render_md(data):
    lines = ['# 核心文献摘要卡', '']
    lines.append(f"- Topic: {data.get('topic','')}")
    lines.append(f"- Generated At: {data.get('generatedAt','')}")
    lines.append('')
    for i, c in enumerate(data.get('cards', []), 1):
        url = c.get('sourceUrl','')
        header = f"## {i}. [{c.get('title','')}]({url})" if url else f"## {i}. {c.get('title','')}"
        lines.append(header)
        lines.append('')
        lines.append(f"- Why keep: {c.get('whyKeep','')}")
        lines.append(f"- Main contribution: {c.get('mainContribution','')}")
        lines.append(f"- Best chapter fit: {c.get('bestChapterFit','')}")
        lines.append(f"- Best argument fit: {c.get('bestArgumentFit','')}")
        claims = c.get('canSupportClaim', [])
        if claims:
            lines.append(f"- Can support claim:")
            for claim in claims:
                lines.append(f"  - {claim}")
        lines.append(f"- Risk if overused: {c.get('riskIfOverused','')}")
        lines.append(f"- Citation key: {c.get('citationKey','')}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Build reference cards from reference pack')
    ap.add_argument('--input', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()
    pack = json.loads(Path(args.input).read_text(encoding='utf-8'))
    data = build_cards(pack)
    Path(args.out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.out_json)
    if args.out_md:
        Path(args.out_md).write_text(render_md(data), encoding='utf-8')
        print(args.out_md)


if __name__ == '__main__':
    main()
