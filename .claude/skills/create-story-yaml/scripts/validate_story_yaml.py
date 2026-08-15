#!/usr/bin/env python3
"""Validate a gptauthor story prompt YAML file before running `gptauthor --story ...`.

Checks the structure and placeholders that gptauthor/library/{prompts,engine}.py rely on,
so failures surface here instead of part-way through a paid multi-chapter run.

Usage:
    python3 validate_story_yaml.py prompts-my-story.yaml [more.yaml ...]

Exit code 0 if every file passes, 1 if any file has an ERROR. WARNs never fail the run.
Uses PyYAML when importable, otherwise falls back to a parser for this specific schema.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from string import Formatter

# Placeholders engine.py passes to .format() for each prompt, and the subset whose absence
# means content is silently dropped from the prompt.
SECTIONS: dict[str, tuple[set[str], set[str]]] = {
    # section: (supplied placeholders, placeholders that should really be used)
    "synopsis": (
        {"total_chapters", "book_description", "book_characters"},
        {"total_chapters", "book_description", "book_characters"},
    ),
    "expand-chapter-first": (
        {"synopsis_response", "total_chapters", "book_description", "book_characters"},
        {"synopsis_response", "book_description", "book_characters"},
    ),
    "expand-chapter-next": (
        {
            "previous_chapter_number",
            "previous_chapter_text",
            "synopsis_response",
            "chapter_number",
            "total_chapters",
            "book_description",
            "book_characters",
        },
        {"previous_chapter_text", "synopsis_response", "chapter_number", "book_description", "book_characters"},
    ),
}

COMMON_KEYS = ("common-book-description", "common-book-characters")
PLACEHOLDER_RE = re.compile(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})")
LEFTOVER_MARKER_RE = re.compile(r"<[A-Z][A-Z0-9_ ,.:'()/-]{2,}>")


class Report:
    def __init__(self, path: Path):
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def print(self) -> None:
        print(f"\n{self.path}")
        for msg in self.errors:
            print(f"  ERROR  {msg}")
        for msg in self.warnings:
            print(f"  WARN   {msg}")
        if not self.errors and not self.warnings:
            print("  OK     valid gptauthor story prompt file")
        elif not self.errors:
            print(f"  OK     valid, with {len(self.warnings)} warning(s) to review")


# ----------------------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------------------
class ParseError(Exception):
    pass


KEY_RE = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z0-9_-]+):(?P<rest>.*)$")


def minimal_parse(text: str) -> dict:
    """Parse the restricted subset of YAML a story file uses: top-level scalars, block
    scalars, and one level of nested mappings. Only a fallback when PyYAML is missing."""
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        match = KEY_RE.match(line)
        if not match:
            raise ParseError(f"line {i + 1}: expected 'key:' but found {line.strip()!r}")
        indent = len(match.group("indent"))
        key = match.group("key")
        rest = match.group("rest").strip()
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if rest.startswith("|") or rest.startswith(">"):
            block: list[str] = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() and len(nxt) - len(nxt.lstrip(" ")) <= indent:
                    break
                block.append(nxt)
                j += 1
            pad = min((len(ln) - len(ln.lstrip(" ")) for ln in block if ln.strip()), default=0)
            parent[key] = "\n".join(ln[pad:] if ln.strip() else "" for ln in block).strip("\n")
            i = j
        elif rest == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
            i += 1
        else:
            if rest[:1] in "\"'" and rest[-1:] == rest[:1] and len(rest) > 1:
                rest = rest[1:-1]
            parent[key] = rest
            i += 1
    return root


def load(path: Path, report: Report) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as ex:
        report.error(f"could not read file: {ex}")
        return None

    bad_indent = [str(n) for n, ln in enumerate(text.splitlines(), 1) if re.match(r"^[ ]*\t", ln)][:5]
    if bad_indent:
        report.error(f"tab characters used for indentation (invalid YAML) on line(s) {', '.join(bad_indent)}")

    try:
        import yaml  # type: ignore
    except ImportError:
        try:
            data = minimal_parse(text)
        except ParseError as ex:
            report.error(f"could not parse YAML ({ex})")
            return None
        report.warn("PyYAML not installed; used the fallback parser - re-run with the project venv to be certain")
        return data

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as ex:
        report.error(f"invalid YAML: {str(ex).splitlines()[0] if str(ex) else ex}")
        return None

    if not isinstance(data, dict):
        report.error("top level of the file must be a mapping of keys")
        return None
    return data


# ----------------------------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------------------------
def format_fields(template: str) -> tuple[set[str], str | None]:
    """Return the placeholder names in a format string, or a message describing why it is
    not a valid format string."""
    names: set[str] = set()
    try:
        for _, field, _, _ in Formatter().parse(template):
            if field is None:
                continue
            if field == "":
                return names, "uses a positional placeholder '{}' - only named placeholders work"
            names.add(field.split(".")[0].split("[")[0])
    except ValueError as ex:
        return names, f"is not a valid format string ({ex}); literal braces must be doubled as {{{{ and }}}}"
    return names, None


def check_markers(value: str, where: str, report: Report) -> None:
    match = LEFTOVER_MARKER_RE.search(value)
    if match:
        report.error(f"'{where}' still contains an unfilled template marker: {match.group(0)}")


def required_string(data: dict, key: str, report: Report) -> str | None:
    """Return data[key] when it is a usable non-empty string, otherwise report why not."""
    value = data.get(key)
    if value is None:
        report.error(f"missing required top-level key '{key}'")
        return None
    if not isinstance(value, str):
        report.error(f"'{key}' must be a block string (use '{key}: |-'), got {type(value).__name__}")
        return None
    if not value.strip():
        report.error(f"'{key}' is empty")
        return None
    check_markers(value, key, report)
    return value


def check_description_shape(description: str, report: Report) -> None:
    if len(description) < 400:
        report.warn(
            f"'common-book-description' is only {len(description)} chars - it carries the whole plot, "
            "so it usually needs a style block plus 8-15 story beats including the ending"
        )
    lowered = description.lower()
    if "style of the" not in lowered:
        report.warn("'common-book-description' has no 'Style of the ... book:' section describing how to write")
    if not any(heading in lowered for heading in ("key points", "book outline", "story outline")):
        report.warn("'common-book-description' has no 'Key points of the story:' section describing the plot")


def check_common(data: dict, report: Report) -> None:
    description = required_string(data, "common-book-description", report)
    characters = required_string(data, "common-book-characters", report)
    if description:
        check_description_shape(description, report)
    if characters and len(characters.strip().splitlines()) < 2:
        report.warn("'common-book-characters' lists fewer than 2 lines - describe each character on its own line")


def check_section_system(section: dict, name: str, report: Report) -> None:
    system = section.get("system")
    if system is None:
        report.error(f"'{name}' is missing a 'system' key (engine asserts on this)")
        return
    if not isinstance(system, str) or not system.strip():
        report.error(f"'{name}.system' must be a non-empty string")
        return
    found = PLACEHOLDER_RE.search(system)
    if found:
        report.warn(
            f"'{name}.system' contains {found.group(0)} but system strings are never formatted - "
            "the model will see the literal braces"
        )
    check_markers(system, f"{name}.system", report)


def check_unsupported_placeholders(name: str, names: set[str], supplied: set[str], report: Report) -> bool:
    """Report placeholders gptauthor does not supply. Returns True if any were found."""
    unknown = sorted(names - supplied)
    literal = [u for u in unknown if not u.isidentifier()]
    named = [u for u in unknown if u.isidentifier()]
    if literal:
        report.error(
            f"'{name}.prompt' has un-escaped literal braces around {', '.join(repr(x) for x in literal)} - "
            "str.format() reads them as placeholders, so double them as {{ and }}"
        )
    if named:
        report.error(
            f"'{name}.prompt' uses placeholder(s) {', '.join('{' + u + '}' for u in named)} that gptauthor "
            f"does not supply - the run raises KeyError. Supplied here: "
            f"{', '.join('{' + s + '}' for s in sorted(supplied))}"
        )
    return bool(literal or named)


def check_section_prompt(section: dict, name: str, report: Report) -> None:
    supplied, expected = SECTIONS[name]
    prompt = section.get("prompt")
    if prompt is None:
        report.error(f"'{name}' is missing a 'prompt' key (engine asserts on this)")
        return
    if not isinstance(prompt, str) or not prompt.strip():
        report.error(f"'{name}.prompt' must be a non-empty block string (use 'prompt: |-')")
        return

    check_markers(prompt, f"{name}.prompt", report)

    names, problem = format_fields(prompt)
    if problem:
        report.error(f"'{name}.prompt' {problem}")
        return
    if check_unsupported_placeholders(name, names, supplied, report):
        return

    try:
        prompt.format(**{key: f"<{key}>" for key in supplied})
    except (KeyError, IndexError, ValueError) as ex:
        report.error(f"'{name}.prompt' fails str.format() at runtime: {type(ex).__name__}: {ex}")
        return

    for missing in sorted(expected - names):
        report.warn(f"'{name}.prompt' never uses {{{missing}}} - that content is dropped from the prompt")


def check_section(data: dict, name: str, report: Report) -> None:
    section = data.get(name)
    if section is None:
        report.error(f"missing required top-level key '{name}'")
        return
    if not isinstance(section, dict):
        report.error(f"'{name}' must be a mapping with 'system' and 'prompt' keys")
        return
    check_section_system(section, name, report)
    check_section_prompt(section, name, report)


def check_interpolation(data: dict, report: Report) -> None:
    """OmegaConf resolves '${...}' inside values (not comments) and dies if it cannot."""

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))
        elif isinstance(node, str) and "${" in node:
            report.error(
                f"'{path}' contains '${{' - OmegaConf reads this as an interpolation and the run fails on load"
            )

    walk(data, "")


def check_chapter_system_reuse(data: dict, report: Report) -> None:
    """engine.py uses expand-chapter-first's system for every chapter, so a different
    system on expand-chapter-next is dead config."""
    first, nxt = data.get("expand-chapter-first"), data.get("expand-chapter-next")
    if not isinstance(first, dict) or not isinstance(nxt, dict):
        return
    first_system, next_system = first.get("system"), nxt.get("system")
    if isinstance(first_system, str) and isinstance(next_system, str):
        if first_system.strip() != next_system.strip():
            report.warn(
                "'expand-chapter-next.system' differs from 'expand-chapter-first.system', but gptauthor "
                "sends the first one for every chapter - the difference has no effect"
            )


def check_synopsis_contract(data: dict, report: Report) -> None:
    section = data.get("synopsis")
    if not isinstance(section, dict) or not isinstance(section.get("prompt"), str):
        return
    prompt = section["prompt"]
    if "Chapter N: <title>" not in prompt:
        report.warn(
            "synopsis prompt does not ask for the '\"Chapter N: <title>\"' heading format - "
            "the outline parser looks for those headings to split chapters"
        )
    if not re.search(r"title of the book|give the title", prompt, re.IGNORECASE):
        report.warn(
            "synopsis prompt does not ask for the book title first - the first non-empty line "
            "before chapter 1 becomes the title and the run aborts if it exceeds 100 chars"
        )
    if re.search(r"\bwrite (one|two|three|four|five|six|seven|eight|nine|ten|\d+) chapter", prompt, re.IGNORECASE):
        report.warn("synopsis prompt looks like it hardcodes a chapter count - use {total_chapters} instead")


def check_unknown_keys(data: dict, report: Report) -> None:
    known = set(COMMON_KEYS) | set(SECTIONS)
    for key in data:
        if key not in known and not str(key).startswith(("_", "unit_test")):
            report.warn(f"top-level key '{key}' is not read by gptauthor and will be ignored")


def check_filename(path: Path, report: Report) -> None:
    if path.suffix != ".yaml":
        report.warn(f"'{path.name}' should use the .yaml extension - --story appends '.yaml' to the name given")
    elif not path.name.startswith("prompts-"):
        report.warn(f"'{path.name}' does not follow the prompts-<slug>.yaml naming convention")


def validate(path: Path) -> Report:
    report = Report(path)
    if not path.is_file():
        report.error("file does not exist")
        return report
    check_filename(path, report)
    data = load(path, report)
    if data is None:
        return report
    check_interpolation(data, report)
    check_common(data, report)
    for name in SECTIONS:
        check_section(data, name, report)
    check_chapter_system_reuse(data, report)
    check_synopsis_contract(data, report)
    check_unknown_keys(data, report)
    return report


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv[1:]]
    if not paths:
        print(__doc__)
        return 2

    reports = [validate(path) for path in paths]
    for report in reports:
        report.print()

    failed = [r for r in reports if r.errors]
    print()
    if failed:
        print(f"FAILED: {len(failed)} of {len(reports)} file(s) have errors")
        return 1
    print(f"PASSED: {len(reports)} file(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
