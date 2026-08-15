---
name: create-story-yaml
description: Turn a short story idea into a gptauthor story prompt YAML file (prompts-<name>.yaml) containing the required common-book-description, common-book-characters, synopsis, expand-chapter-first and expand-chapter-next sections, then validate it. Use when the user wants a new gptauthor story, a new story prompt file, or a yaml like prompts-openai-drama.yaml / prompts-scifi-simulation.yaml / prompts-gptauthor-usage.yaml.
---

# Create a gptauthor story YAML

Expand a short story idea (a sentence, a paragraph, a premise) into a complete gptauthor
story prompt file, then validate it so `gptauthor --story <name>` runs without errors.

The human writes the plot; gptauthor writes the prose. This file **is** the plot — it must
contain the whole arc including the ending. Do not leave the ending for the LLM to invent.

## Workflow

1. Read the user's short story text and note which decisions it already settles.
2. **Ask the user about the style** with a single `AskUserQuestion` call, before writing
   anything (see *Asking about style*).
3. Pick the output path (see *Filename and location*).
4. Copy `assets/template.yaml` and fill it in, applying the answers (see *Writing the content*).
5. Validate: `python3 .claude/skills/create-story-yaml/scripts/validate_story_yaml.py <path>`
   Fix every ERROR; treat WARNs as a review checklist.
6. Report the path, how the answers shaped the file, and the run command.

## Asking about style

A short premise never settles audience, tone, focus, or ending, and every one of those
changes the whole file. Ask once, up front, in **one** `AskUserQuestion` call — do not
write a draft first and revise it afterwards.

Rules:

- **Skip anything the user already specified.** If the premise says "a kids' book", don't
  ask about audience. Never ask a question the prompt already answers.
- Four questions maximum per call. Pick the four most open dimensions from the table below;
  if fewer than four are open, ask fewer.
- Put the option you'd recommend first and mark it `(Recommended)`. The user always gets a
  free-text "Other", which is where the interesting answers usually come from.
- If the user declines, answers "you choose", or is clearly in a hurry, pick sensible
  defaults, write the file, and state each choice you made in your reply.

| Dimension | `header` | Options to offer |
| --- | --- | --- |
| Audience age bracket | `Audience` | Adult (general) / Young adult (13-18) / Middle grade (8-12) / Early readers (5-8) |
| Tone and treatment | `Tone` | Warm and funny / Dark and tense / Literary and restrained / Fast-paced and plot-driven |
| Where the story's weight sits (`multiSelect: true`) | `Focus` | Characters and relationships / Puzzle or mystery the reader can solve / World and atmosphere / Ideas and themes |
| How it ends | `Ending` | Twist that recasts the story / Earned happy resolution / Bittersweet or ambiguous / Bleak or tragic |

Other dimensions worth a slot when they are the open ones: comparable authors to write
toward, real people or events to stay faithful to, story length (a 3-chapter run wants
~8 beats, a 15-chapter run wants ~15), and anything the story must avoid.

The most valuable answer is usually free text on **key story points to hit** — the user's
own beats. Invite it explicitly in the `Focus` question's phrasing, e.g. *"Where should the
story's weight sit? (Pick any, or use Other to list specific beats you want hit.)"*

Then use the answers:

- **Audience** sets vocabulary, sentence length, chapter length, and what content is on the
  table. Say it plainly in the style block, e.g. `The book is written for readers aged 8 to
  12: clear sentences, concrete images, no graphic violence.`
- **Tone** picks the comparable authors and the list of story devices.
- **Focus** decides which beats get several lines and which get one.
- **Ending** goes in the beats and, when it needs pinning down, a `Final chapter:` block.

## Required schema

All five top-level keys are required, spelled exactly like this. Nothing else is read.

| Key | Shape | Consumed as |
| --- | --- | --- |
| `common-book-description` | block string `\|-` | `{book_description}` in all three prompts |
| `common-book-characters` | block string `\|-` | `{book_characters}` in all three prompts |
| `synopsis` | mapping: `system`, `prompt` | one call, writes the chapter outline |
| `expand-chapter-first` | mapping: `system`, `prompt` | chapter 1 |
| `expand-chapter-next` | mapping: `system`, `prompt` | chapters 2..N, one call each |

`system` is a plain one-line string; `prompt` is a block string `|-`. A missing `system` or
`prompt` key is an assertion failure at runtime.

## Placeholders

`prompt` values go through Python `str.format()`. Only these names are supplied — anything
else raises `KeyError` mid-run:

- `synopsis.prompt` — `{total_chapters}` `{book_description}` `{book_characters}`
- `expand-chapter-first.prompt` — the above plus `{synopsis_response}`
- `expand-chapter-next.prompt` — the above plus `{previous_chapter_number}`
  `{previous_chapter_text}` `{chapter_number}`

Rules that follow from that:

- **Literal braces in a prompt must be doubled**: `{{` and `}}`.
- **`system` is never formatted.** Placeholders there are passed to the model verbatim.
- **`expand-chapter-next.system` is dead** — the engine uses `expand-chapter-first.system`
  for every chapter. Keep the two identical so a later edit isn't silently ignored.
- **Never write `${...}`** anywhere in the file; OmegaConf treats it as interpolation and
  the run dies on load.
- **Never hardcode a chapter count** in prose — the count comes from `--total-chapters`.
  Always use `{total_chapters}`.

Keep the three prompt bodies close to the existing files (`gptauthor/prompts-*.yaml`);
they are tuned to parse correctly. Vary the `system` line and the genre nouns to match the
story, and leave the mechanics alone. `assets/template.yaml` already has working versions.

## Writing the content

Every choice below traces back to an answer from *Asking about style*. If an answer had no
visible effect on the file, it wasn't applied.

### `common-book-description`

Two labelled parts, in this order:

1. `Style of the <adjectives> book:` — 6-10 lines: genre, **the audience bracket stated in
   plain terms**, two or three comparable authors, narrative devices matching the chosen
   tone, a line requiring rich dialog, a line requiring per-character description, a line
   requiring that scene/timeline/travel logic be worked out, and
   `You must not end a chapter with any variation of 'To be continued...'.`
2. `Key points of the story:` — the actual plot. 8-15 beats covering the full arc in order,
   naming characters and locations. Give the beats the user asked to focus on more room than
   the rest, and fold any beats they supplied as free text in verbatim in the right place.
   **State the chosen ending explicitly**, including any twist. A `Final chapter:` sub-block
   is a good way to pin down an unusual ending
   (see `gptauthor/prompts-scifi-simulation.yaml`).

Write beats, not prose — this is a brief for a writer, not a draft.

### `common-book-characters`

One line per character: name, gender, role, appearance, personality, quirks. Include minor
characters the beats depend on. Mark historical or offstage figures as such. Match the cast
to the audience — a middle grade book wants a protagonist near the reader's own age.

### `system` lines

One sentence naming the author persona for the genre, e.g. *"You are a clever and creative
hard science fiction book author. You are skilled at weaving stories that are coherent,
logical, and thrilling to read. You are skilled at creating characters that are engaging
and believable."* Name the audience here too when it is not adult, e.g. *"...a children's
book author writing for readers aged 8 to 12."* Use the same one in `synopsis` and both
`expand-chapter-*` sections unless the outline genuinely needs a different persona from
the prose.

## Filename and location

`prompts-<kebab-slug>.yaml`, slug derived from the story (e.g. `prompts-lighthouse-keeper.yaml`).

- A story for the user to run: write it to the current working directory. `--story` resolves
  a local file first, then the installed package's resources.
- A story to ship with this repo: write it to `gptauthor/`, and note that
  `pyproject.toml` `include` lists the yaml files that get packaged — it currently ships only
  two, so a new file needs adding there if it is meant to be distributed.

Do not overwrite an existing file; if the path is taken, pick another slug and say so.

## Reporting back

Give the path, one line per style answer showing where it landed in the file (and, for any
dimension the user left to you, what you picked), and the run command with the name minus
the `.yaml` extension:

```bash
gptauthor --story prompts-lighthouse-keeper --total-chapters 5 --llm-model gpt-5.4-mini --llm-temperature 0.1
```

Mention that `OPENAI_API_KEY` must be set, and that the run pauses after the synopsis so the
user can edit `synopsis_response_user_edited.txt` before the chapters are written.

## Further detail

`reference.md` — the engine call sequence, every runtime failure mode with file:line
citations, and a worked short-input-to-yaml example. Read it when a validation error is
unclear or when deviating from the template.
