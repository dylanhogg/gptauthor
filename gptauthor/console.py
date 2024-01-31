from typing import Optional

import typer
from loguru import logger
from omegaconf import OmegaConf
from rich import print
from typing_extensions import Annotated

from .library import consts, engine, env, log
from .library.classes import AppUsageException

typer_app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"{consts.package_name} version: {consts.version}")
        raise typer.Exit()


@typer_app.command()
def run(
    story: Annotated[str, typer.Option(help="The name within the yaml file name defining the story")],
    llm_model: Annotated[str, typer.Option(help="The model name")] = consts.default_llm_model,
    llm_temperature: Annotated[
        float, typer.Option(help="LLM temperature value (0 to 2, OpenAI default is 1)")
    ] = consts.default_llm_temperature,
    llm_top_p: Annotated[
        float, typer.Option(help="LLM top_p probability value (0 to 2, OpenAI default is 1)")
    ] = consts.default_llm_top_p,
    llm_use_localhost: Annotated[
        int, typer.Option(help="LLM use localhost:8081 instead of openai")
    ] = consts.default_llm_use_localhost,
    total_chapters: Annotated[int, typer.Option(help="Total chapters to write")] = consts.default_write_total_chapters,
    allow_user_input: Annotated[bool, typer.Option(help="Allow command line user input")] = True,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help=f"Display {consts.package_name} version", callback=version_callback),
    ] = None,
) -> None:
    """
    gptauthor entry point
    """

    try:
        log.configure()
        example_usage = f"Example usage: [bold green]{consts.package_name} --story openai-drama --total-chapters 3 --llm-model gpt-3.5-turbo --llm-temperature 0.1 --llm-top-p 1.0[/bold green]"

        llm_api_key = env.get("OPENAI_API_KEY", "")
        if not llm_use_localhost and not llm_api_key:
            raise AppUsageException(
                "Expected an environment variable 'OPENAI_API_KEY' to be set to use OpenAI API."
                "\nSee the OpenAI docs for more info: https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key"
                "\nAlternatively you can use the '--llm_use_localhost 1' argument to use a local LLM server."
            )

        story_file = f"prompts-{story}.yaml"
        llm_config = OmegaConf.create(
            {
                "version": consts.version,
                "api_key": llm_api_key,
                "model": llm_model,
                "temperature": llm_temperature,
                "top_p": llm_top_p,
                "total_chapters": total_chapters,
                "use_localhost": llm_use_localhost,
                "localhost_sleep": int(env.get("LLM_USE_LOCALHOST_SLEEP", 0)),
                "default_output_folder": consts.default_output_folder,
                "story_file": story_file,
                "allow_user_input": allow_user_input,
            }
        )

        engine.do_writing(llm_config)

    except AppUsageException as ex:
        print(example_usage)
        print(f"[bold red]{str(ex)}[/bold red]")
        print("")
        print(f"For more information, try '{consts.package_name} --help'.")
        logger.exception(ex)

    except typer.Exit as ex:
        if ex.exit_code == 0:
            print()
            print(
                "[bold green]Good bye and thanks for using gptauthor! Please visit https://github.com/dylanhogg/gptauthor for more info.[/bold green]"
            )
            return
        print(example_usage)
        print(f"[bold red]Unexpected error code: {str(ex)}[/bold red]")
        print("")
        print(f"For more information, try '{consts.package_name} --help'.")
        logger.exception(ex)

    except Exception as ex:
        print(example_usage)
        print(f"[bold red]Unexpected exception: {str(ex)}[/bold red]")
        print("")
        print(f"For more information, try '{consts.package_name} --help'.")
        logger.exception(ex)
