import pytest

from gptauthor.library import engine, utils
from gptauthor.library.classes import AppUsageException


def test_synopsis_processer_parses_old_bold_chapter_headings():
    synopsis_response = """
**Title: "AI in Disarray"**

**Chapter 1: OpenAI Shakeup**
- First chapter outline.

**Chapter 2: Turmoil and Temptation**
- Second chapter outline.
"""

    title, chapters = utils.synopsis_processer(synopsis_response)

    assert title == "AI in Disarray"
    assert chapters == [
        "Chapter 1: OpenAI Shakeup\n- First chapter outline.",
        "Chapter 2: Turmoil and Temptation\n- Second chapter outline.",
    ]


def test_synopsis_processer_parses_markdown_heading_chapter_headings():
    synopsis_response = """
## **Title: "Leonie Skyforce-Clarke and the Mystery of the Observatory Vault"**

## **Chapter 1: The Letter in the Green Bottle**
- First chapter outline.

### **Chapter 2: The Tooth Between the Pages**
- Second chapter outline.
"""

    title, chapters = utils.synopsis_processer(synopsis_response)

    assert title == "Leonie Skyforce-Clarke and the Mystery of the Observatory Vault"
    assert chapters == [
        "Chapter 1: The Letter in the Green Bottle\n- First chapter outline.",
        "Chapter 2: The Tooth Between the Pages\n- Second chapter outline.",
    ]


def test_synopsis_processer_parses_case_insensitive_headings_and_ignores_bullets():
    synopsis_response = """
# Mixed Case Mystery

cHaPtEr 1: The First Real Heading
- This is the first outline.
- Chapter 2: This bullet is not a heading.

CHAPTER 2: The Second Real Heading
- This is the second outline.
"""

    title, chapters = utils.synopsis_processer(synopsis_response)

    assert title == "Mixed Case Mystery"
    assert len(chapters) == 2
    assert chapters[0] == (
        "Chapter 1: The First Real Heading\n"
        "- This is the first outline.\n"
        "- Chapter 2: This bullet is not a heading."
    )
    assert chapters[1] == "Chapter 2: The Second Real Heading\n- This is the second outline."


def test_validate_synopsis_accepts_exact_chapter_count():
    engine.validate_synopsis("AI in Disarray", ["Chapter 1: OpenAI Shakeup"], 1)


def test_validate_synopsis_rejects_missing_title():
    with pytest.raises(AppUsageException, match="Could not parse a book title"):
        engine.validate_synopsis("", ["Chapter 1: OpenAI Shakeup"], 1)


def test_validate_synopsis_rejects_zero_chapters():
    with pytest.raises(AppUsageException, match="Could not parse any chapter outlines"):
        engine.validate_synopsis("AI in Disarray", [], 1)


def test_validate_synopsis_rejects_wrong_chapter_count():
    with pytest.raises(AppUsageException, match="Expected 1 chapter outline, but model returned 2 chapter outlines"):
        engine.validate_synopsis(
            "AI in Disarray",
            ["Chapter 1: OpenAI Shakeup", "Chapter 2: Turmoil and Temptation"],
            1,
        )
