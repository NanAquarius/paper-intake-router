# Inline citation injection notes

Use this layer to inject **internal citation markers** into draft text before final formatting.

## Principle

Do not jump directly to final superscript or layout-specific numbering during drafting.

Inject stable internal markers first, then let the downstream renderer convert them to:
- GB/T numeric references
- superscript markers
- APA-style inline citations
- LaTeX/Quarto cite syntax

## Safer marker style

Prefer markers like:
- `[CITE:method choice|10.48550/arxiv.2305.18290]`
- `[CITE:risk discussion|10.48550/arxiv.2210.10760,10.48550/arxiv.2406.02900]`

This preserves meaning and makes later transformation easier.

## Rule

Only inject markers when the paragraph or line is already tagged with an explicit claim type.

Do not guess blindly from arbitrary prose.
