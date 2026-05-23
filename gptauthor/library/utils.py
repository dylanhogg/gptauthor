import re
from datetime import datetime
from pathlib import Path

import requests
from loguru import logger


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


def calculate_model_price_estimate(model_name: str, total_tokens: int) -> int:
    """
    Calculate the price for a specific model and token count using litellm's pricing data.
    TODO: pass in input/output cost per token for accurate cost estimation!
    """
    try:
        litellm_pricing_url = (
            "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
        )
        response = requests.get(litellm_pricing_url)

        if response.status_code == 200:
            model_pricing_data = response.json()
            for model_key, model_info in model_pricing_data.items():
                if model_name.lower() == model_key.lower():
                    price_per_token = model_info.get(
                        "output_cost_per_token"
                    )  # Over estimate the cost of the model since output cost > input cost
                    logger.info(f"Found pricing data for model: {model_name=}, {price_per_token=}")
                    return total_tokens * price_per_token
            logger.warning(f"Could not find pricing data for model: {model_name}")
            return -1
        else:
            logger.warning(f"Failed to fetch pricing data: {response.status_code}")
            return -1
    except Exception as ex:
        logger.exception(f"Error calculating model-specific price: {ex}")
        return -1


chapter_heading_pattern = re.compile(
    r"(?im)^(?P<prefix>\s{0,3}#{0,6}\s*)?(?P<bold_open>\*\*)?chapter\s+(?P<number>\d+)\s*:\s*(?P<title>.*?)(?P<bold_close>\*\*)?\s*$"
)


def _clean_synopsis_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"^\s{0,3}#{1,6}\s*", "", title)
    title = title.replace("**", "")
    title = re.sub(r"^Title\s*:\s*", "", title, flags=re.IGNORECASE)
    title = title.replace('"', "").strip()
    title = re.sub(" +", " ", title)
    return title


def _clean_chapter_title(title: str) -> str:
    title = title.replace("**", "").replace('"', "").strip()
    title = re.sub(" +", " ", title)
    return title


def synopsis_processer(synopsis_response):
    chapter_matches = list(chapter_heading_pattern.finditer(synopsis_response))

    if not chapter_matches:
        return _clean_synopsis_title(synopsis_response), []

    title = ""
    for line in synopsis_response[: chapter_matches[0].start()].splitlines():
        line = line.strip()
        if line:
            title = _clean_synopsis_title(line)
            break

    chapters = []
    for i, chapter_match in enumerate(chapter_matches):
        chapter_start = chapter_match.end()
        chapter_end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(synopsis_response)
        chapter_number = chapter_match.group("number")
        chapter_title = _clean_chapter_title(chapter_match.group("title"))
        chapter_body = synopsis_response[chapter_start:chapter_end].strip()
        chapter = f"Chapter {chapter_number}: {chapter_title}"
        if chapter_body:
            chapter += f"\n{chapter_body}"
        chapters.append(chapter)

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
