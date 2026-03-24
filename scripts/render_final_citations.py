#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def load_reference_pack(path: str):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    entries = data.get('entries', [])
    key_to_index = {}
    key_to_entry = {}
    for idx, e in enumerate(entries, 1):
        key = e.get('doi') or e.get('arxivId') or e.get('id')
        if key:
            key_to_index[key] = idx
            key_to_entry[key] = e
    return key_to_index, key_to_entry


def load_json(path: str | None):
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def apa_marker(keys, entry_map):
    parts = []
    for k in keys:
        e = entry_map.get(k)
        if not e:
            continue
        authors = e.get('authors', [])
        year = e.get('year') or 'n.d.'
        if not authors:
            parts.append(f'Unknown, {year}')
        elif len(authors) == 1:
            parts.append(f'{authors[0]}, {year}')
        else:
            parts.append(f'{authors[0]} et al., {year}')
    return '(' + '; '.join(parts) + ')' if parts else ''


def gbt_marker(keys, index_map, bracket_style='square'):
    nums = [str(index_map[k]) for k in keys if k in index_map]
    if not nums:
        return ''
    if bracket_style == 'superscript':
        return '^[' + ','.join(nums) + ']'
    if bracket_style == 'round':
        return '(' + ','.join(nums) + ')'
    return '[' + ','.join(nums) + ']'


def render(text: str, style: str, index_map: dict, entry_map: dict, profile: dict | None = None) -> str:
    profile = profile or {}
    bracket_style = profile.get('bracketStyle', 'square')

    def repl(match):
        keys = [k.strip() for k in match.group(2).split(',') if k.strip()]
        if style.upper().startswith('APA'):
            return apa_marker(keys, entry_map)
        return gbt_marker(keys, index_map, bracket_style=bracket_style)

    return re.sub(r'\s*\[CITE:([^|\]]+)\|([^\]]+)\]', repl, text)


def markerize_inline_numbers(text: str, citation_plan: dict | None) -> str:
    if not citation_plan:
        return text
    marker_map = {}
    for ch in citation_plan.get('chapters', []):
        for claim in ch.get('claims', []):
            inline = claim.get('inlineMarker', '')
            keys = claim.get('recommendedCitations', [])
            ctype = claim.get('claimType', 'result interpretation')
            if inline and keys:
                marker_map[inline] = f"[CITE:{ctype}|{','.join(keys)}]"
    out = text
    for inline, internal in marker_map.items():
        out = out.replace(inline, internal)
    return out


def postprocess_prose(text: str, style: str, profile: dict | None = None) -> str:
    out = text
    profile = profile or {}
    profile_name = profile.get('profile', 'default')
    zh_punct = profile.get('zhPunctuationMode', 'fullwidth')
    apa_paren_mode_zh = profile.get('apaParenModeZh', 'fullwidth')

    if style.upper().startswith('APA'):
        if apa_paren_mode_zh == 'fullwidth':
            # 中文正文里的 APA 引用统一为全角括号，并让句号落在括号后
            out = re.sub(r'([\u4e00-\u9fff][^\n]*?)[。.]\(([^()]+,\s*\d{4}[a-z]?)\)', r'\1（\2）', out)
            out = re.sub(r'([\u4e00-\u9fff])\(([^()]+,\s*\d{4}[a-z]?)\)', r'\1（\2）', out)
            out = re.sub(r'（([^（）]+)）(?![。！？])', r'（\1）。', out)
            out = re.sub(r'（([^（）]+)）([。！？])', r'（\1）\2', out)
    else:
        out = re.sub(r'\s+(\[[0-9,]+\])', r'\1', out)
        out = re.sub(r'(\[[0-9,]+\])([。！？])', r'\1\2', out)
        if profile_name == 'cn-thesis-superscript':
            out = out.replace('^[', '^[')

    if zh_punct == 'fullwidth':
        out = re.sub(r'\s+([，。；：！？])', r'\1', out)
        out = re.sub(r'\s+（', '（', out)
        out = re.sub(r'）\s+', '）', out)
    return out


def main():
    ap = argparse.ArgumentParser(description='Render internal citation anchors into final citation style')
    ap.add_argument('--draft', required=True)
    ap.add_argument('--reference-pack', required=True)
    ap.add_argument('--citation-plan')
    ap.add_argument('--citation-profile-json')
    ap.add_argument('--style', default='GB/T 7714')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    text = Path(args.draft).read_text(encoding='utf-8')
    citation_plan = load_json(args.citation_plan)
    citation_profile = load_json(args.citation_profile_json) or {}
    text = markerize_inline_numbers(text, citation_plan)
    idx_map, entry_map = load_reference_pack(args.reference_pack)
    out = render(text, args.style, idx_map, entry_map, citation_profile)
    out = postprocess_prose(out, args.style, citation_profile)
    Path(args.out).write_text(out, encoding='utf-8')
    print(args.out)


if __name__ == '__main__':
    main()
