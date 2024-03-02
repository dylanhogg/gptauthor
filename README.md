# GPT Author

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/gptauthor.svg?1)](https://badge.fury.io/py/gptauthor)
[![Build](https://github.com/dylanhogg/gptauthor/workflows/build/badge.svg)](https://github.com/dylanhogg/gptauthor/actions/workflows/python-poetry-app.yml)
[![Latest Tag](https://img.shields.io/github/v/tag/dylanhogg/gptauthor)](https://github.com/dylanhogg/gptauthor/tags)
[![Downloads](https://static.pepy.tech/badge/gptauthor)](https://pepy.tech/project/gptauthor)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dylanhogg/gptauthor/blob/master/notebooks/gptauthor_colab_custom_story.ipynb)

Unleash your storytelling genius: GPTAuthor is an easy to use command-line tool for writing long form, multi-chapter stories given a story prompt.

![A GPT human cybord writing a manuscript](https://github.com/dylanhogg/gptauthor/blob/main/docs/img/header.jpg?raw=true)

## How It Works

1. **Human written story description:** You describe your story outline, writing style, characters etc in a story prompt ([see an example](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml)).
1. **Run GPTAuthor:** As described below, choosing model, temperature, and number of chapters to write.
1. **AI generated synopsis:** Given the story prompt, GPTAuthor uses ChatGPT to automatically turn this into a synopsis that has chapter summaries for the number of chapters you specify.
1. **Human review of synopsis:** You are given a chance to review the synopsis and (optionally) make changes, only proceeding to the next step if/when you are happy with it. If it isn't what you want, you can generate another before proceeding.
1. **AI generated story:** Each chapter is iteratively written by ChatGPT given the common synopsis and previous chapter. (This approach is to keep token count within limits).
   The full story is written as Markdown and HTML to an `./_output/` folder for your reading pleasure.

## Example GPTAuthor Story Outputs

[The Nov 2023 OpenAI leadership crisis](https://github.com/dylanhogg/gptauthor/blob/main/samples/openai-drama-20240131-224810-v0.5.0-gpt-4-0125-preview.md) -
"In the heart of San Francisco, nestled among the city's tech giants and start-up hopefuls, stood the OpenAI office. A hive of activity, it buzzed with the sound of keyboards clacking, coffee machines hissing, and the occasional drone of a philosophical debate about whether AI could develop a taste for late-night taco runs. It was a typical day, or so everyone thought. Sam Altman, the CEO of OpenAI, was in his office, a space that looked more like a teenager's bedroom than the office of a tech mogul, with posters of space exploration and vintage computers adorning the walls. He was in the middle of explaining to a rubber duck on his desk the intricacies of AI alignment, a method he found surprisingly effective, when his phone buzzed with an email notification." [continue reading...](https://github.com/dylanhogg/gptauthor/blob/main/samples/openai-drama-20240131-224810-v0.5.0-gpt-4-0125-preview.md)

[Echoes of Atlantis](https://github.com/dylanhogg/gptauthor/blob/main/samples/echoes-of-atlantis--v1.0.0-gpt-4-0125-preview.md) (based on a [blogpost](https://medium.com/@chiaracoetzee/generating-a-full-length-work-of-fiction-with-gpt-4-4052cfeddef3)) - "In the dimly lit halls of the British Museum, Aria Seaborne's heart raced with anticipation. Her fingers, delicate yet steady, brushed against the surface of an ancient artifact that had long eluded understanding. It was a curious object, seemingly part of a larger mechanism, its origins shrouded in mystery and its purpose lost to time. Aria, with her keen eye for the arcane, noticed an almost imperceptible seam along its side. With a gentle nudge, the artifact sprang open, revealing a compartment that housed a parchment, brittle with age." [continue reading...](https://github.com/dylanhogg/gptauthor/blob/main/samples/echoes-of-atlantis--v1.0.0-gpt-4-0125-preview.md)

## Installation

You can install [gptauthor](https://pypi.org/project/gptauthor/) using pip, ideally into a Python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it).

```bash
pip install gptauthor
```

Alternatively, checkout [an example notebook](https://github.com/dylanhogg/gptauthor/blob/main/notebooks/gptauthor_colab_custom_story.ipynb) that uses gptauthor and you can run directly in Google Colab.

[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dylanhogg/gptauthor/blob/master/notebooks/gptauthor_colab_custom_story.ipynb)

## Run GPTAuthor

### Example Usage and API Key

This example reads the story prompt from the example [prompts-openai-drama.yaml](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml) file and writes 3 chapters using the `gpt-3.5-turbo` model with a temperature of `0.1`. Note that you will need to locally set your [OpenAI API Key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key) environment variable.

It's recommended to experiment using the default `gpt-3.5-turbo` model as generating a few chapters will only cost a couple cents (as of Jan 2024). Once you are happy with the results you can try one of the more expensive `gpt-4` models which will produce better quality results, be slower, and cost more to run. See the [OpenAI pricing page](https://openai.com/pricing#language-models) for more details.

Set your OpenAI API Key on MacOS/Linux:

```bash
export OPENAI_API_KEY=sk-<yourkey>
```

Or, set your OpenAI API Key on Windows:

```bash
setx OPENAI_API_KEY "sk-<yourkey>"
```

Then run the gptauthor command:

```bash
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
- `--help`: Show usage help

## Produced Output Files

While running the app tells your the input paramers, the progress of the writing, and where the output is written to.

In progress and final output is written to the `./_output/` directory, in the sub-folders `./_output/<prompt-file-name>/<model-name>/<datetime>-<parameters>-<book-name>/`.

There are several files, the main output being a Markdown version of the whole book `_whole_book.md` and an HTML version of the same `_whole_book.html`.

## Creating Your Own Story Prompts

The prompts for creating your own story are defined in a yaml file, for example see: [prompts-openai-drama.yaml](https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml).

Make a copy, fill in your story details and describe the writing style (while retaining the same structure), and run the app in the same folder as your new yaml file.

For example, if your yaml prompt file is called `prompts-my-really-great-story.yaml`:

```bash
export OPENAI_API_KEY=sk-<your key>
gptauthor --story prompts-my-really-great-story --total-chapters 5 --llm-model gpt-3.5-turbo --llm-temperature 0.1
```

## Issues

- The OpenAI API sometimes returns an error, in which case the app will exit. You can restart it and it will continue from where it left off as responses are cached (assuming same arguments).
- Continuity. Since each chapter only knows about the common synopsis and the previous chapter, there can be issues of continuity between chapters.
- Not tested on Windows so there could be path issues here.
- Cost estimation is based on total token but should treat input and output token counts seperately.
- The use of AI to write stories is a controversial topic. This is a tool to test the capabilities of ChatGPT and should be used responsibly.

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Create a pull request with a description of your changes.

## Final notes

While an effort is made to count tokens and estimate OpenAI API costs for each run, they are just estimated and can be wrong. Check your OpenAI billing page to confirm the actual costs.

I'm sure there are bugs, please report them on the [Github issues page](https://github.com/dylanhogg/gptauthor/issues)

Have fun! And please share your results with me if you can (perhaps as a Github [documentation issue](https://github.com/dylanhogg/gptauthor/labels/documentation)), I'd love to see them.

This project is [MIT](https://github.com/dylanhogg/gptauthor/blob/main/LICENSE) licensed.
