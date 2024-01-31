# GPT Author

[![Latest Tag](https://img.shields.io/github/v/tag/dylanhogg/gptauthor)](https://github.com/dylanhogg/gptauthor/tags)
[![Build](https://github.com/dylanhogg/gptauthor/workflows/build/badge.svg)](https://github.com/dylanhogg/gptauthor/actions/workflows/python-poetry-app.yml)

GPTAuthor is a tool for writing long form, multi-chapter stories and novels using AI

![A GPT human cybord writing a manuscript](https://github.com/dylanhogg/gptauthor/blob/main/docs/img/header.jpg?raw=true)

## Installation

You can install llmgraph using pip:

```bash
pip install gptauthor
```

## Usage

### Example Usage

This example reads the story prompt from the example file [prompts-openai-drama.yaml](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml) file and writes 3 chapters using the `gpt-3.5-turbo` model with a temperature of `0.1`:

```bash
export OPENAI_API_KEY=sk-<your key>
gptauthor --story openai-drama --total-chapters 3 --llm-model gpt-3.5-turbo --llm-temperature 0.1
```

### Required Arguments

- `--story TEXT`: The name within the yaml file name defining the story [default: openai-drama]

### Optional Arguments

- `--llm-model TEXT`: The model name [default: gpt-3.5-turbo]
- `--llm-temperature FLOAT`: LLM temperature value (0 to 2, OpenAI default is 1) [default: 1]
- `--llm-top-p FLOAT`: LLM top_p probability value (0 to 2, OpenAI default is 1) [default: 1]
- `--llm-use-localhost INTEGER`: LLM use localhost:8081 instead of openai [default: 0]
- `--total-chapters INTEGER`: Total chapters to write [default: 5]
- `--allow-user-input / --no-allow-user-input`: Allow command line user input [default: allow-user-input]
- `--version`: Display gptauthor version
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

### Produced Output Files

While running the app tells your the input paramers, the progress of the writing, and where the output is written to.

In progress and final output is written to the `./_output/` directory, in the sub-folders `./_output/<prompt-file-name>/<model-name>/<datetime>-<parameters>-<book-name>/`.

There are several files, the main output being a Markdown version of the whole book `_whole_book.md` and an HTML version of the same `_whole_book.html`.
