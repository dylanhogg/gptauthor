from importlib.metadata import version as package_version

package_name = "gptauthor"
version = package_version(package_name)

default_output_folder = "./_output/"
default_write_total_chapters = 3

# https://platform.openai.com/docs/api-reference/chat/create
default_llm_use_localhost = 0
default_llm_model = "gpt-5.4-mini"  # Default updated to gpt-5.4-mini as of 2024-06, previously gpt-3.5-turbo
default_llm_temperature = 1  # Default 1 as per OpenAI docs
default_llm_top_p = 1  # Default 1 as per OpenAI docs
