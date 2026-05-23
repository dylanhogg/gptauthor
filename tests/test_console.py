import typer
from click.testing import CliRunner

from gptauthor import console


def test_typer_command_builds_with_boolean_flags():
    command = typer.main.get_command(console.typer_app)
    runner = CliRunner()

    help_result = runner.invoke(command, ["--help"])
    version_result = runner.invoke(command, ["--version"])
    allow_user_input_option = next(param for param in command.params if param.name == "allow_user_input")

    assert help_result.exit_code == 0
    assert "--no-allow-user-input" in allow_user_input_option.secondary_opts
    assert allow_user_input_option.is_bool_flag
    assert version_result.exit_code == 0
    assert "gptauthor version:" in version_result.output
