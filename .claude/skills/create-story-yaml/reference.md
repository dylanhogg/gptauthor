# Reference: how gptauthor consumes a story YAML

File:line citations are against this repo. Read this when a validation error is unclear or
when deviating from `assets/template.yaml`.

## Call sequence

`gptauthor --story <name>` resolves `<name>.yaml` against the current working directory
first, then the installed package's resource folder, and errors if neither exists
([prompts.py:33](../../../gptauthor/library/prompts.py)). Then
[engine.py:74](../../../gptauthor/library/engine.py) `do_writing` runs:

1. Reads `common-book-description` and `common-book-characters` verbatim.
2. Formats `synopsis.prompt` with `total_chapters`, `book_description`, `book_characters`,
   appends its own hard requirements block, and makes one LLM call with `synopsis.system`.
3. Parses the response into a title and chapter list, then validates the chapter count.
4. Pauses for the user to edit `synopsis_response_user_edited.txt` (unless
   `--no-allow-user-input`), and re-reads it.
5. Chapter 1 uses `expand-chapter-first.prompt`; chapters 2..N use
   `expand-chapter-next.prompt`, each fed the previous chapter's full text.
6. Concatenates everything into `_whole_book.md` and `_whole_book.html` under
   `./_output/<story-name>/<model>/<datetime>-<params>-<title>/`.

Each call is cached by joblib on `(system, prompt, llm_config)`, so a re-run with identical
arguments resumes rather than re-paying. Editing the YAML busts the cache for every prompt
it touches.

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Entity type '<x>' not supported` | A required top-level key is missing | Add all five keys |
| `AssertionError: ... missing a 'system' key` | Section is not a mapping with `system` + `prompt` ([prompts.py:28](../../../gptauthor/library/prompts.py)) | Add both sub-keys |
| `KeyError: '<name>'` mid-run | Prompt uses a placeholder gptauthor does not supply | Use only the supported names |
| `ValueError: Single '{' encountered` | Literal brace in a prompt | Double it: `{{` / `}}` |
| `InterpolationKeyError` on load | `${...}` in the file; OmegaConf resolves it | Remove the `$` |
| `Expected N chapter outlines, but model returned M` ([engine.py:65](../../../gptauthor/library/engine.py)) | Model ignored the count, or emitted extra "Chapter" headings | Lower temperature, or make the synopsis prompt less prone to epilogues |
| `Could not parse a book title from the synopsis response` | No `Chapter N: <title>` headings found | Keep the heading-format instruction in the synopsis prompt |
| `Unexpected synopsis_title length!` then exit 1 ([engine.py:142](../../../gptauthor/library/engine.py)) | Title line over 100 chars — usually the model wrote a preamble first | Ask for the title first and nothing before it |

The title is the **first non-empty line before the first chapter heading**, so the synopsis
prompt must not invite a preamble, tagline, or "Here is your outline:" opener.

## Placeholders in full

Supplied by [engine.py:89](../../../gptauthor/library/engine.py) and
[engine.py:197](../../../gptauthor/library/engine.py):

| Placeholder | synopsis | expand-chapter-first | expand-chapter-next |
| --- | :-: | :-: | :-: |
| `{book_description}` | yes | yes | yes |
| `{book_characters}` | yes | yes | yes |
| `{total_chapters}` | yes | yes | yes |
| `{synopsis_response}` | no | yes | yes |
| `{previous_chapter_number}` | no | no | yes |
| `{previous_chapter_text}` | no | no | yes |
| `{chapter_number}` | no | no | yes |

`{total_chapters}` differs subtly between calls: the synopsis gets the CLI `--total-chapters`
value, while the chapter prompts get the number of chapters actually parsed from the synopsis
([engine.py:190](../../../gptauthor/library/engine.py)). They match on a successful run.

`system` strings are passed straight to the API without formatting
([engine.py:98](../../../gptauthor/library/engine.py)), and only
`expand-chapter-first.system` is ever read for chapters
([engine.py:193](../../../gptauthor/library/engine.py)).

## Hard requirements appended automatically

[engine.py:44](../../../gptauthor/library/engine.py) appends this to the synopsis prompt, so
there is no need to repeat it — but nothing in the prompt should contradict it:

- return exactly `{total_chapters}` chapter outlines
- title first, then only chapter outlines
- headings exactly `"Chapter N: <title>"`
- compress the whole arc into one chapter when the count is 1
- no extra headings, epilogues, or appendices named "Chapter"

## Worked example

Short input:

> A lighthouse keeper on a remote island starts receiving letters addressed to her that were
> postmarked fifty years in the future.

That premise fixes the setting and the hook and nothing else, so all four style dimensions
are open and all four get asked. Suppose the answers come back: **adult (general)**,
**literary and restrained**, focus on **world and atmosphere** plus **characters and
relationships**, ending as a **twist that recasts the story**.

Those answers do real work. "Literary and restrained" picks Kazuo Ishiguro and Susanna
Clarke as comparables and rules out the thriller beats the premise would otherwise invite.
The atmosphere focus means the island, the weather, and the lamp room each earn their own
beat. The twist answer forces a specific ending to be committed to now: the letters are her
own, written near the end of her life and posted into a loop she has already lived, with the
predecessor's logbook turning out to be in her handwriting.

That becomes:

- `common-book-description` — a style block naming the genre, comparable authors, and the
  usual craft instructions, then ~12 beats: the posting, the first letter, the logbook, the
  pilot's scepticism, the escalating specificity of the letters, the storm, the discovery of
  the handwriting, the choice she makes, the ending as decided above.
- `common-book-characters` — three entries with appearance, personality, and a quirk each.
- The three prompt sections — copied from the template with "story book" swapped for
  "literary mystery" and a matching `system` persona.

The beats are what make the output good. Everything else is boilerplate.

Had the audience answer come back **middle grade (8-12)** instead, the same premise would
produce a different file end to end: a keeper's niece rather than the keeper as protagonist,
comparable authors swapped for Katherine Rundell and Eva Ibbotson, an audience line in the
style block, shorter chapters, the drowning risk in the storm beat softened, and an ending
that resolves warmly rather than closing a loop she cannot escape. That is the point of
asking first — audience is not a coat of paint applied at the end.

## Style notes drawn from the shipped examples

- `gptauthor/prompts-openai-drama.yaml` — beats grouped under dated headings; good model for
  a story that follows real events.
- `gptauthor/prompts-scifi-simulation.yaml` — uses a separate `Final chapter:` block to pin
  an ending that could not be inferred from the beats.
- `gptauthor/prompts-aventura-childrens-book.yaml` — Markdown bold inside the block string;
  fine, and it survives into the prompt.
- `gptauthor/prompts-echoes-of-atlantis.yaml` — leading `#` comments carrying source links;
  a good place to record where an idea came from.
