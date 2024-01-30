from datetime import datetime
from time import sleep
from typing import Optional

import typer
from loguru import logger
from rich import print
from tqdm import tqdm
from typing_extensions import Annotated

from .library import consts, env, log
from .library.classes import AppUsageException

typer_app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"{consts.package_name} version: {consts.version}")
        raise typer.Exit()


@typer_app.command()
def run(
    required_arg: Annotated[str, typer.Argument(help="Required argument")],
    optional_arg: Annotated[str, typer.Option(help="Optional argument")] = None,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help=f"Display {consts.package_name} version", callback=version_callback),
    ] = None,
) -> None:
    """
    Command entry point
    """
    log.configure()

    example_usage = f"Example usage: [bold green]{consts.package_name}[/bold green]"

    logger.info(f"Start {consts.package_name}, required_arg = {required_arg}, optional_arg = {optional_arg}")
    logger.info(f"PYTHONPATH = {env.get('PYTHONPATH', 'Not set')}")
    logger.info(f"LOG_STDERR_LEVEL = {env.get('LOG_STDERR_LEVEL', 'Not set. Copy `.env_template` to `.env`')}")
    logger.info(f"LOG_FILE_LEVEL = {env.get('LOG_FILE_LEVEL', 'Not set. Copy `.env_template` to `.env`')}")

    try:
        start = datetime.now()

        print(f"Hello! required_arg = '{required_arg}', optional_arg = '{optional_arg}'")
        print("")

        # TODO: do the stuff
        for _ in tqdm(range(5)):
            sleep(0.1)

        took = datetime.now() - start
        print("")
        print(f"[bold green]gptauthor finished, took {took.total_seconds()}s.[/bold green]")
        print("")
        print(
            "Thank you for using gptauthor! Please consider starring the project on github: https://github.com/dylanhogg/gptauthor"
        )

    except AppUsageException as ex:
        print(example_usage)
        print(f"[bold red]{str(ex)}[/bold red]")
        print("")
        print(f"For more information, try '{consts.package_name} --help'.")
        raise typer.Exit(code=1) from ex
    except Exception as ex:
        print(example_usage)
        print(f"[bold red]Unexpected exception: {str(ex)}[/bold red]")
        print("")
        print(f"For more information, try '{consts.package_name} --help'.")
        raise typer.Exit(code=100) from ex
