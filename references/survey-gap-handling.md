# Survey gap handling

Use this note when `reference-screening-round2` still reports `survey count below minimum`.

## Rule

Do **not** keep looping automatic query expansion forever.

After the second-round retry, if survey is still missing, treat it as a real evidence gap rather than a search-heuristic problem.

## What to do next

1. Record the gap explicitly in the workflow output.
2. Mark the literature set as usable but structurally incomplete.
3. Prefer one of these fallback paths:
   - broaden to the parent topic manually
   - add one authoritative overview/tutorial/source outside the narrow query scope
   - ask for user confirmation if the paper must claim a complete literature overview
4. Continue the paper only if the user accepts that the current reference set is strong on methods/results but weak on survey coverage.

## What not to do

- do not auto-loop unlimited retries
- do not pretend the survey requirement is satisfied
- do not silently downgrade the quality gate without recording it
