# OpenDataODC Index Agent Guidelines

These rules apply to every nested `agent.md` file in this public index repo.

- Make changes locally only unless the user explicitly asks to push or deploy.
- Do not commit environment files, secrets, generated output, or crawl artifacts.
- Keep internal docs in the private `opendataodc-docs` repo, not this source repo.
- Do not accept crawl configuration in public dataset YAML; derive it internally.
- Keep dataset references organized by source domain and short topic.
- Do not commit generated index manifests in this public repo.
- Public submissions should stay small, reviewable, and source-linked.
- Reviews are human-only until the user explicitly adds automated review.
- When a submission path fails or gets reworked, capture the false start and
  the rule learned in one line so later edits do not repeat the same search.
- Keep learnings terse and durable; avoid long task notes that will not help
  the next submission.
