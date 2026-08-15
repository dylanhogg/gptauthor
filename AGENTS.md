# AGENTS.md

## What this project is

`gptauthor` is a Python CLI that writes long-form, multi-chapter stories from a human-written
story prompt. The human writes the plot; the LLM writes the prose.

Pipeline (see [engine.py](gptauthor/library/engine.py) — `do_writing()` is the whole flow):

1. Load a story YAML (`prompts-<name>.yaml`) holding the book description, characters, and three prompt templates.
2. One LLM call produces a **synopsis**: a title plus one outline per chapter.
3. The synopsis is parsed and validated (chapter count must match `--total-chapters`).
4. Unless `--no-allow-user-input`, the run **pauses** so the user can edit
   `synopsis_response_user_edited.txt` on disk, then presses `C` to continue or `Q` to quit.
5. Each chapter is one LLM call. Chapter 1 sees the synopsis; chapter N sees the synopsis plus
   the **full text of chapter N-1 only** (this bounds token count, and is why cross-chapter
   continuity is imperfect by design).
6. Everything is written to `./_output/<story>/<model>/<datetime>-<params>-<title>/`, with
   `_whole_book.md` and `_whole_book.html` as the main outputs.

## Layout

| Path | What's there |
| --- | --- |
| [console.py](gptauthor/console.py) | Typer CLI entry point (`gptauthor` script), arg parsing, builds the OmegaConf `llm_config`, top-level error handling |
| [library/engine.py](gptauthor/library/engine.py) | The whole writing pipeline; synopsis validation; output file assembly |
| [library/llm.py](gptauthor/library/llm.py) | Single OpenAI chat-completions call, tenacity retry, joblib disk cache |
| [library/prompts.py](gptauthor/library/prompts.py) | Resolves and reads the story YAML |
| [library/utils.py](gptauthor/library/utils.py) | Synopsis/chapter parsing regexes, output folder naming, price estimate |
| [library/consts.py](gptauthor/library/consts.py) | Defaults (model, temperature, chapter count, output folder) |
| `gptauthor/prompts-*.yaml` | Bundled example stories |
| `tests/` | pytest; no API key needed (`test_costs.py` does hit the network for pricing data) |
| `samples/` | Committed example story outputs |
| `.claude/skills/create-story-yaml/` | Skill for authoring a new story YAML — read its `SKILL.md` before hand-writing one |

## Commands

Poetry-managed. Everything has a Make target:

```bash
make install
```

```bash
make test
```

```bash
make black && make ruff
```

Run the tool against a bundled story (needs `OPENAI_API_KEY`):

```bash
poetry run gptauthor --story prompts-openai-drama --total-chapters 3 --llm-model gpt-5.4-mini --llm-temperature 0.1 --no-allow-user-input
```

CI ([python-poetry-app.yml](.github/workflows/python-poetry-app.yml)) runs `black --check`,
`ruff check .`, and pytest on Python 3.12. Match that locally before pushing.

## Conventions

- Python ≥3.12. Black and ruff, both at line-length 120; `E501` is off because black handles it.
- Logging is loguru; `engine.p()` prints to the console *and* logs. Levels come from `.env`
  (copy `.env.template`), file log at `./log/app.log`.
- User-facing errors raise `AppUsageException` ([classes.py](gptauthor/library/classes.py));
  `console.py` catches it and prints example usage. Use it for anything the user can fix.
- `llm_config` is an OmegaConf `DictConfig` threaded through the whole pipeline. It holds the
  API key — copy and `del` the key before printing or writing it (engine does this as
  `safe_llm_config`).

## Story YAML contract

Five required top-level keys: `common-book-description`, `common-book-characters`, `synopsis`,
`expand-chapter-first`, `expand-chapter-next`. The last three are mappings with `system` and
`prompt`. `prompt` values are run through Python `str.format()`, so:

- Only these placeholders exist: `{total_chapters}`, `{book_description}`, `{book_characters}`,
  plus `{synopsis_response}` for the expand prompts, plus `{previous_chapter_number}`,
  `{previous_chapter_text}`, `{chapter_number}` for `expand-chapter-next`. Anything else is a
  `KeyError` mid-run.
- Literal braces must be doubled (`{{`, `}}`).
- Never write `${...}` — OmegaConf treats it as interpolation and the load fails.
- `expand-chapter-next.system` is never used (the engine reuses `expand-chapter-first.system`);
  keep the two identical so edits aren't silently dropped.
- `--story foo` resolves `foo.yaml` in the CWD first, then in the installed package resources.
  A YAML only ships with the package if it's listed in `pyproject.toml` `include`.

## Gotchas

- **Responses are cached to disk** by joblib in `.joblib_cache/`, keyed on system+prompt+config.
  Re-running identical arguments replays cached responses — free and instant, but it means you
  are not testing the live API. Delete the cache dir to force real calls.
- Changing anything inside `llm_config` (including temperature) changes the cache key.
- The synopsis chapter count is enforced: if the model returns a different number of chapters,
  the run aborts with an `AppUsageException` telling the user to lower temperature.
- `calculate_model_price_estimate()` fetches litellm's pricing JSON over the network and returns
  `-1` when the model or the network is unavailable. Costs are estimates only, and use the output
  token price for all tokens.
- Any change to the chapter/synopsis parsing regexes in `utils.py` should be covered by
  `tests/test_chapter_splits.py` and `tests/test_string_manipulations.py`.
- `make run` in the Makefile still passes `gpt-3.5-turbo`; the actual default is `gpt-5.4-mini`.
- Not tested on Windows — path handling may be a problem there.
