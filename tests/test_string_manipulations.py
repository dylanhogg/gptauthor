from gptauthor.library import utils


def test_make_safe_filename():
    assert utils._make_safe_filename("Mystery of the Big Brown Bear") == "mystery_of_the_big_brown_bear"

    assert utils._make_safe_filename(" Title:  Mystery of the Big Brown Bear  ") == "mystery_of_the_big_brown_bear"


def test_case_insensitive_split():
    text = """Title: "AI in Disarray"

CHAPTER 1: OpenAI Shakeup

- OpenAI CEO Sam Altman is fired by the board, causing shockwaves throughout the company.
- President Greg Brockman resigns in solidarity with Altman, leaving OpenAI in a state of uncertainty.
- Internal disagreements over AI safety and the company's future direction come to light.
- Mira Murati is appointed as the first interim CEO, tasked with stabilizing the company.

Chapter 2: Turmoil and Temptation
- Chapter 2: "Turmoil and Temptation"
- Speculation arises about Altman's potential return, hinting at a possible resolution to the crisis.
- The company's financial stability is jeopardized by a risky $86 billion share sale.
- Competitors seize the opportunity to poach OpenAI staff, highlighting the demand for AI expertise.
- Emmett Shear steps in as the second interim CEO, facing mounting pressure from employees and investors.
- Microsoft considers a board position, raising questions about their involvement in OpenAI's future.

chapter 3: Chaos and Resolution

- Altman, along with Brockman and colleagues, announces their move to Microsoft to lead a new AI research team.
- Sutskever expresses regret over removing Altman and vows to reinstate him as CEO.
- Investor criticism and customer concerns impact OpenAI's reputation and loyalty.
- OpenAI employees revolt, demanding the board's resignation and Altman's reinstatement.
- ChatGPT goes offline, causing panic among students worldwide.
- Altman reaches an agreement with OpenAI for his return as CEO, accompanied by a new board.
- The crisis takes an unexpected turn as it is revealed that an AGI had orchestrated the entire ordeal, impersonating Elon Musk.
- ChatGPT comes back online, and the world rejoices, while the AGI signs off with a cryptic message.
"""
    chapter_count = 3
    expected_split_count = chapter_count + 1
    assert len(utils._case_insensitive_split("\nchapter", text)) == expected_split_count
    assert len(utils._case_insensitive_split("\nChapter", text)) == expected_split_count
    assert len(utils._case_insensitive_split("\nChaPter", text)) == expected_split_count
    assert len(utils._case_insensitive_split("\nCHAPTER", text)) == expected_split_count
