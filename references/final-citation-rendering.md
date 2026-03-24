# Final citation rendering

This stage converts internal draft markers into user-facing citation style.

## Input
- `cited-draft.md` containing internal markers like `[CITE:method choice|doi1,doi2]`
- `reference-pack.json`

## Output
- `final-cited-draft.md`

## Supported styles (current)
- `GB/T 7714` numeric markers, e.g. `[1]`, `[1,3]`
- `APA` inline author-year markers

## Rule
Use internal markers first, final rendering second.

Do not skip directly from draft prose to final citation style unless the draft already carries explicit internal anchors.


## Unified marker-aware pipeline
- 普通正文段可通过 `inject_inline_citations.py` 注入 `[CITE:...]`
- 图表说明句可通过 `autofix_figure_table_refs.py --citation-mode internal-anchor` 直接生成 `[CITE:...]`
- `render_final_citations.py` 统一把这些内部锚点渲染成最终样式
