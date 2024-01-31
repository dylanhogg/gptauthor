# GPT Author

[![Latest Tag](https://img.shields.io/github/v/tag/dylanhogg/gptauthor)](https://github.com/dylanhogg/gptauthor/tags)
[![Build](https://github.com/dylanhogg/gptauthor/workflows/build/badge.svg)](https://github.com/dylanhogg/gptauthor/actions/workflows/python-poetry-app.yml)

Unleash your storytelling genius: GPTAuthor is an easy to use command-line tool for writing long form, multi-chapter stories given a story prompt.

![A GPT human cybord writing a manuscript](https://github.com/dylanhogg/gptauthor/blob/main/docs/img/header.jpg?raw=true)

## How It Works

1. **Install GPTAuthor:** Using pip as described below.
1. **Human written story description:** You describe, in a yaml file, the story outline, writing style, characters etc. This is your story prompt. (See an example [story prompt](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml)).
1. **Run GPTAuthor:** As described below.
1. **AI generateed synopsis:** Given the story prompt, GPTAuthor uses ChatGPT to automatically turn this into a synopsis that has chapter summaries for the number of chapters you specify.
1. **Human review:** You are given a chance to review the synopsis and (optionally) make changes, only proceeding to the next step if/when you are happy with the synopsis. If the Synopsis is not good enough, you can quit and generate another. I usually find that the synopsis pretty good after a few iterations.
1. **AI generated chapters:** Each chapter is iteratively written by ChatGPT given the common synopsis and previous chapter. (This approach is to keep token count low).
1. **Final result:** The synopsis and all chapters are written to files as Markdown and HTML for your reading pleasure. See an [example result about the Nov 2023 OpenAI leadership crisis](https://github.com/dylanhogg/gptauthor/blob/main/samples/openai-drama-20240131-224810-v0.5.0-gpt-4-0125-preview.md).

## Installation

You can install [gptauthor](https://pypi.org/project/gptauthor/) using pip, ideally into a Python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it).

```bash
pip install gptauthor
```

## Command Line Usage

### Example Usage and API Key

This example reads the story prompt from the example file [prompts-openai-drama.yaml](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml) file and writes 3 chapters using the `gpt-3.5-turbo` model with a temperature of `0.1`. Note that you will need to set an [OpenAI API Key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key) environment variable.

It's recommended to experiment using the default `gpt-3.5-turbo` model as generating a few chapters will only cost a couple cents (as of Jan 2024). Once you are happy with the results you can try one of the more expensive `gpt-4` models which will produce better quality results, be slower, and cost more to run. See the [OpenAI pricing page](https://openai.com/pricing#language-models) for more details.

```bash
export OPENAI_API_KEY=sk-<your key>
gptauthor --story prompts-openai-drama --total-chapters 3 --llm-model gpt-3.5-turbo --llm-temperature 0.1
```

### Required Arguments

- `--story TEXT`: The name of the yaml file defining the story and prompts

### Optional Arguments

- `--llm-model TEXT`: The model name [default: gpt-3.5-turbo]
- `--llm-temperature FLOAT`: LLM temperature value (0 to 2, OpenAI default is 1) [default: 1]
- `--llm-top-p FLOAT`: LLM top_p probability value (0 to 2, OpenAI default is 1) [default: 1]
- `--llm-use-localhost INTEGER`: LLM use localhost:8081 instead of openai [default: 0]
- `--total-chapters INTEGER`: Total chapters to write [default: 3]
- `--allow-user-input / --no-allow-user-input`: Allow command line user input [default: allow-user-input]
- `--version`: Display gptauthor version
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

### Produced Output Files

While running the app tells your the input paramers, the progress of the writing, and where the output is written to.

In progress and final output is written to the `./_output/` directory, in the sub-folders `./_output/<prompt-file-name>/<model-name>/<datetime>-<parameters>-<book-name>/`.

There are several files, the main output being a Markdown version of the whole book `_whole_book.md` and an HTML version of the same `_whole_book.html`.

### Creating Your Own Story Prompts

The prompts for creating your own story are defined in a yaml file, for example see: [prompts-openai-drama.yaml](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml).

Make a copy, fill in your story details and describe the writing style (while retaining the same structure), and run the app in the same folder as your new yaml file.

For example, if your yaml prompt file is called `prompts-my-really-great-story.yaml`:

```bash
export OPENAI_API_KEY=sk-<your key>
gptauthor --story prompts-my-really-great-story --total-chapters 5 --llm-model gpt-3.5-turbo --llm-temperature 0.1
```

### Example GPTAuthor Story Output

[The Nov 2023 OpenAI leadership crisis](https://github.com/dylanhogg/gptauthor/blob/main/samples/openai-drama-20240131-224810-v0.5.0-gpt-4-0125-preview.md).

(More examples to come...)

### Final notes

While an effort is made to count tokens and estimate OpenAI API costs for each run, they are just estimated and can be wrong. Check your OpenAI billing page to confirm the actual costs.

I'm sure there are bugs, please report them on the [Github issues page](https://github.com/dylanhogg/gptauthor/issues)

Have fun! And please share your results with me if you can (perhaps as a Github [documentation issue](https://github.com/dylanhogg/gptauthor/labels/documentation)), I'd love to see them.
