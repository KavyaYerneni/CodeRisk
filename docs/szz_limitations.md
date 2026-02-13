# SZZ limitations

The CodeRisk SZZ implementation is a **baseline heuristic**, not ground truth.

## Sources of label noise

- Keyword matching on commit messages misses silent fixes and flags refactors that say "fix".
- `git blame` on the parent may attribute lines to commits that only moved or reformatted code.
- Renames, deletions, and binary files are skipped or partially handled.
- Merge commits are ignored by default and can hide real fixing changes.
- Issue-link resolution is optional and not required for demo mode.

## How we use labels

- Synthetic demo labels use `label_source=synthetic_demo` and never claim SZZ provenance.
- Mined SZZ labels should be stored with `confidence` and `reason` fields.
- Evaluation reports must treat SZZ-derived positives as noisy proxies for bug-introducing changes.
