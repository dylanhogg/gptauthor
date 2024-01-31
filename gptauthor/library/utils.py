import re
from datetime import datetime
from pathlib import Path


def _make_safe_filename(s, max_chars=36):
    safe = s.lower()
    safe = safe.replace("title", "")
    safe = safe.replace(" ", "_")
    safe = re.sub("_+", "_", safe)
    safe = re.sub(r"[^a-zA-Z0-9_]", "", safe)
    safe = safe.strip("_")
    safe = safe.strip()
    safe = safe[:max_chars]
    return safe


def _case_insensitive_split(split, input):
    input = input.replace("**", "")  # Remove any MD bolding
    parts = re.split(split, input, flags=re.IGNORECASE)
    return parts


def gpt4_8k_price_estimate(total_tokens):
    # https://openai.com/pricing#language-models
    return (total_tokens / 1000) * 0.045  # Dec 2023


def gpt35_4k_price_estimate(total_tokens):
    # https://openai.com/pricing#language-models
    return (total_tokens / 1000) * 0.002  # Dec 2023


def synopsis_processer(synopsis_response):
    chapters_split = _case_insensitive_split("\nChapter", synopsis_response)

    title = None
    chapters = []
    for i, chapter in enumerate(chapters_split):
        if i == 0:
            title = chapter.strip()
            title = title.replace("Title:", "").replace('"', "").strip()
            title = re.sub(" +", " ", title)
        else:
            chapter_clean = chapter.replace('"', "").strip()
            chapters.append("Chapter " + chapter_clean)

    return title, chapters


def get_folder(synopsis_title: str, synopsis_chapters: list[str], llm_config: dict) -> Path:
    now = datetime.now()
    safe_title = _make_safe_filename(synopsis_title)
    num_chapters = len(synopsis_chapters)
    story_name = llm_config.story_file.split("/")[-1].split(".")[0]
    folder = (
        Path(llm_config.default_output_folder)
        / f"{story_name}"
        / f"{llm_config.model}"
        / f"{now.strftime('%Y%m%d-%H%M%S')}-v{llm_config.version}-{llm_config.model}-T{llm_config.temperature}-P{llm_config.top_p}-C{num_chapters}-{safe_title}"
    )
    folder.mkdir(parents=True, exist_ok=True)
    return folder
