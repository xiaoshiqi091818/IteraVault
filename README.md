# 迭行 IteraVault

IteraVault is an early-stage, local-first engine for learning from a user's task feedback and retrieving relevant experience on future tasks. It is designed for an open set of tasks, rather than a fixed collection of writing or image workflows.

**Current status:** the first development slice stores and reads versioned task events in SQLite. Automatic task classification, experience promotion, retrieval, and host adapters are planned but not implemented.

## Quick start

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv python install 3.12
uv sync
uv run iteravault init
uv run iteravault record demo-1 task_started --payload '{"goal":"write an article"}'
uv run iteravault record demo-1 feedback_recorded --payload '{"comment":"shorter opening"}'
uv run iteravault history demo-1
uv run python -m unittest discover -s tests -v
```

The default database is `data/iteravault.sqlite3`, ignored by Git. Override it with `--db PATH` before the subcommand or the `ITERAVAULT_DB` environment variable. Do not commit real conversation logs, user feedback, generated artifacts, or API credentials.

## Roadmap

1. Versioned task events and local storage (current).
2. Task fingerprints and open task clusters.
3. Evidence-backed experience cards and reversible promotion.
4. Budget-aware retrieval and token accounting.
5. Host adapters, evaluation, and import/export.

## License

Apache License 2.0. See [LICENSE](LICENSE).
