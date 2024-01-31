import re
import time
import warnings
import webbrowser
from datetime import datetime

import markdown
import typer
from loguru import logger
from rich import print
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm

from . import consts, llm, prompts, utils

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


def p(message: str):
    print(message)
    logger.info(message)


def replace_chapter_text(string):
    pattern = r"\n\"?Chapter (\d+)"  # NOTE: double-quote at start is optional for match, but will leave a hanging double-quote if present
    replacement = r"\n### Chapter \1"
    new_chapter_text = re.sub(pattern, replacement, string, flags=re.IGNORECASE)
    return new_chapter_text


def user_input_continue_processing(synopsis_response_user_edited_filename):
    while True:
        print(f"This is your chance to edit the file '{synopsis_response_user_edited_filename}' before continuing.\n")
        user_input = input("Press 'C' to continue writing chapters, or 'Q' to quit: ")
        if user_input.lower() == "c":
            return True
        elif user_input.lower() == "q":
            return False
        else:
            print("Invalid input. Please try again.")


def do_writing(llm_config):
    start = time.time()
    p(f"Start {consts.package_name} {consts.version}, {llm_config.total_chapters=}, {llm_config.story_file=}...")

    # ------------------------------------------------------------------------------
    # Create synopsis
    # ------------------------------------------------------------------------------
    book_description = prompts.get_book_description(llm_config)
    book_characters = prompts.get_book_characters(llm_config)
    synopsis_system = prompts.get_system("synopsis", llm_config)
    synopsis_prompt_format = prompts.get_prompt("synopsis", llm_config)
    synopsis_prompt = synopsis_prompt_format.format(
        total_chapters=str(llm_config.total_chapters),
        book_description=book_description,
        book_characters=book_characters,
    )

    synopsis_response_user_edited_filename = "synopsis_response_user_edited.txt"

    synopsis_response, synopsis_total_tokens = llm.make_call(synopsis_system, synopsis_prompt, llm_config)
    synopsis_title, synopsis_chapters = utils.synopsis_processer(synopsis_response)

    output_folder = utils.get_folder(synopsis_title, synopsis_chapters, llm_config)
    safe_llm_config = llm_config.copy()
    del safe_llm_config["api_key"]
    safe_llm_config["app_version"] = consts.version
    safe_llm_config["output_folder"] = str(output_folder)
    safe_llm_config["datetime"] = datetime.now().strftime("%Y%m%d-%H%M%S")

    p(f"Writing output to folder: '{output_folder}'...")
    with open(output_folder / "_synopsis_prompt.txt", "w") as f:
        f.write(f"{synopsis_system}")
        f.write("\n---\n")
        f.write(f"{synopsis_prompt}\n")
    with open(output_folder / "synopsis_response_original.txt", "w") as f:
        f.write(f"{synopsis_response.strip()}")
    with open(output_folder / synopsis_response_user_edited_filename, "w") as f:
        f.write(f"{synopsis_response.strip()}")
    with open(output_folder / "_chapter_prompt_format.txt", "w") as f:
        f.write(prompts.get_prompt("expand-chapter-first", llm_config))
        f.write("\n---\n")
        f.write(prompts.get_prompt("expand-chapter-next", llm_config))
    with open(output_folder / "_synopsis.txt", "w") as f:
        f.write(synopsis_response)
        f.write("\n---\n")
        f.write(str(safe_llm_config))
        f.write(f"{synopsis_total_tokens=}")

    took = time.time() - start

    p("Synopsis:")
    print("```")
    p(synopsis_response)
    print("```")
    p(f"\nFinished synopsis for book '{synopsis_title}' with {len(synopsis_chapters)} chapters")
    p(f"\n{took=:.2f}s")
    p(f"Total synopsis tokens: {synopsis_total_tokens:,}")
    p(f"Rough GPT4 8k price: ${utils.gpt4_8k_price_estimate(synopsis_total_tokens):.2f}")
    p(f"Rough GPT3.5 4k price: ${utils.gpt35_4k_price_estimate(synopsis_total_tokens):.3f}")
    p(f"\n{llm_config=}\n")

    if len(synopsis_title) > 100:
        logger.warning(f"Unexpected synopsis_title length! {len(synopsis_title)=}")
        with open(output_folder / "__error.txt", "w") as f:
            f.write(f"Unexpected synopsis_title length! {len(synopsis_title)=}")
            f.write(str(safe_llm_config))
        raise typer.Exit(1)

    # ------------------------------------------------------------------------------
    # User input to continue or quit
    # ------------------------------------------------------------------------------
    if not user_input_continue_processing(str(output_folder / synopsis_response_user_edited_filename)):
        with open(output_folder / "__aborted.txt", "w") as f:
            f.write(f"Aborted writing book: {synopsis_title}.\n\n")
            f.write(str(safe_llm_config))
        raise typer.Exit(0)

    # ------------------------------------------------------------------------------
    # Load user edited synopsis (if applicable)
    # ------------------------------------------------------------------------------
    with open(output_folder / synopsis_response_user_edited_filename, "r") as f:
        synopsis_response_original = synopsis_response
        synopsis_response = f.read().strip()

    if synopsis_response_original != synopsis_response:
        print("Using new user edited synopsis:")
        print("```")
        print(synopsis_response)
        print("```")
    else:
        print("Synopsis unchanged.")

    # ------------------------------------------------------------------------------
    # Write chapters
    # ------------------------------------------------------------------------------
    start = time.time()
    p("Starting chapter writing...")

    chapter_responses = []
    all_chapter_total_tokens = []
    pbar = tqdm(range(0, len(synopsis_chapters)))
    for i in pbar:
        chapter_number = i + 1
        pbar.set_description(f"Writing chapter {chapter_number}")
        p(f"Writing {chapter_number=}")

        is_first_chapter = chapter_number == 1
        total_chapters = len(synopsis_chapters)
        previous_chapter_text = "" if is_first_chapter else chapter_responses[chapter_number - 2]

        chapter_system = prompts.get_system("expand-chapter-first", llm_config)
        chapter_first_prompt_format = prompts.get_prompt("expand-chapter-first", llm_config)
        chapter_next_prompt_format = prompts.get_prompt("expand-chapter-next", llm_config)

        chapter_prompt = (
            chapter_first_prompt_format.format(
                synopsis_response=synopsis_response,
                total_chapters=total_chapters,
                book_description=book_description,
                book_characters=book_characters,
            )
            if is_first_chapter
            else chapter_next_prompt_format.format(
                previous_chapter_number=chapter_number - 1,
                previous_chapter_text=previous_chapter_text,
                synopsis_response=synopsis_response,
                chapter_number=chapter_number,
                total_chapters=total_chapters,
                book_description=book_description,
                book_characters=book_characters,
            )
        )

        chapter_response, chapter_total_tokens = llm.make_call(chapter_system, chapter_prompt, llm_config)
        all_chapter_total_tokens.append(chapter_total_tokens)
        chapter_response = chapter_response.replace(
            "```", ""  # TODO: HACK: investigate, can be introduced if in prompt template
        )
        chapter_responses.append(chapter_response)
        with open(output_folder / f"chapter_{chapter_number}.txt", "w") as f:
            f.write(f"{chapter_total_tokens=}")
            f.write(f"{len(all_chapter_total_tokens)=}")
            f.write(f"{sum(all_chapter_total_tokens)=}")
            f.write(f"{chapter_number=}")
            f.write("\n---\nchapter_prompt=\n")
            f.write(chapter_prompt)
            f.write("\n---\nchapter_response=\n")
            f.write(chapter_response)

    # ------------------------------------------------------------------------------
    # Construct whole book and write to file
    # ------------------------------------------------------------------------------
    total_process_tokens = synopsis_total_tokens + sum(all_chapter_total_tokens)
    rough_gpt4_8k_price_estimate = utils.gpt4_8k_price_estimate(total_process_tokens)
    rough_gpt35_4k_price_estimate = utils.gpt35_4k_price_estimate(total_process_tokens)

    whole_book = f"# {synopsis_title}"
    whole_book += "\n\n---\n\n"
    whole_book += "## Synopsis\n\n" + synopsis_response
    whole_book += "\n\n---\n\n"
    whole_book += "## Full Book Text"
    for chapter_response in chapter_responses:
        whole_book += "\n\n" + chapter_response
    whole_book += "\n\n---\n\n"
    whole_book += "## Technicals\n\n" + str(safe_llm_config) + "\n\n"
    whole_book += f"Total process tokens: {total_process_tokens:,}\n\n"
    whole_book += f"Rough GPT4 8k price: ${rough_gpt4_8k_price_estimate:.2f}\n\n"
    whole_book += f"Rough GPT3.5 4k price: ${rough_gpt35_4k_price_estimate:.3f}\n\n"
    whole_book += f"Synopsis tokens: {synopsis_total_tokens:,}\n\n"
    whole_book += f"Sum of all chapter tokens: {sum(all_chapter_total_tokens):,}\n\n"
    whole_book += f"Average chapter tokens: {sum(all_chapter_total_tokens)/len(all_chapter_total_tokens):,.1f}\n\n"
    whole_book += f"Min chapter tokens: {min(all_chapter_total_tokens):,}\n\n"
    whole_book += f"Max chapter tokens: {max(all_chapter_total_tokens):,}\n\n"
    whole_book += f"Individual chapter tokens: {all_chapter_total_tokens}\n\n"
    whole_book += "\n\n---\n\n"

    whole_book = replace_chapter_text(whole_book)
    with open(output_folder / "_whole_book.md", "w") as f:
        f.write(whole_book)

    whole_book_html = markdown.markdown(whole_book)
    html_style = 'max-width:1000px; margin-left:auto; margin-right:auto; border:1px solid #ddd; padding:25px; font-family:"Georgia","Times New Roman",serif; font-size: larger;'
    whole_book_html = f"<html><body><div style='{html_style}'>" + whole_book_html + "</div></body></html>"
    with open(output_folder / "_whole_book.html", "w") as f:
        f.write(whole_book_html)

    with open(output_folder / "__finished.txt", "w") as f:
        f.write(f"Finished writing book: {synopsis_title}.\n\n")
        f.write(str(safe_llm_config))

    took = time.time() - start

    # ------------------------------------------------------------------------------
    # Final output
    # ------------------------------------------------------------------------------
    p(f"\n{str(safe_llm_config)}")
    p(f"\nFinished writing book: {synopsis_title}")
    p(f"\nOutput written to '{output_folder}'")
    p(
        f"\n{took=:.2f}s, {total_process_tokens=:,}, ${rough_gpt4_8k_price_estimate=:.2f}, ${rough_gpt35_4k_price_estimate=:.2f}"
    )

    while True:
        user_input = input("Press 'Y' to open the html book in a browser, or Enter/Return to finish: ")
        if user_input.lower() == "y":
            abs_file = (output_folder / "_whole_book.html").resolve()
            webbrowser.open(f"file://{abs_file}")
        elif user_input.lower() == "":
            return
        else:
            print("Invalid input. Please try again.")
