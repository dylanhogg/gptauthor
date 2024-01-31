import importlib.resources
from pathlib import Path

from loguru import logger
from omegaconf import DictConfig, OmegaConf

from gptauthor.library import consts
from gptauthor.library.classes import AppUsageException


def _get_common(key: str, llm_config: DictConfig):
    yaml_file = get_yaml_file(llm_config)
    conf_file = OmegaConf.load(yaml_file)
    if key not in conf_file:
        raise Exception(f"{key} not in conf_file")
    return conf_file[key]


def _get_conf(prompt_type: str, llm_config) -> (str, dict):
    yaml_file = get_yaml_file(llm_config)
    conf_file = OmegaConf.load(yaml_file)
    if prompt_type not in conf_file:
        valid_prompt_types = sorted(
            [k for k in conf_file.keys() if not k.startswith("_") and not k.startswith("unit_test")]
        )
        raise AppUsageException(f"Entity type '{prompt_type}' not supported. Try one of these: {valid_prompt_types}")
    conf = conf_file[prompt_type]
    assert "system" in conf, f"Prompt type '{prompt_type}' is missing a 'system' key"
    assert "prompt" in conf, f"Prompt type '{prompt_type}' is missing a 'prompt' key"
    return conf


def get_yaml_file(llm_config: DictConfig):
    local_yaml_file = Path(llm_config.story_file)
    if local_yaml_file.is_file():
        logger.info(f"Using local yaml file: {local_yaml_file}")
        return local_yaml_file

    resources_yaml_file = Path(importlib.resources.files(consts.package_name).joinpath(llm_config.story_file))
    if resources_yaml_file.is_file():
        logger.info(f"Using resources yaml file: {resources_yaml_file}")
        return resources_yaml_file

    raise Exception(
        f"Could not find yaml file: {llm_config.story_file} either locally or in the resources folder. "
        "See here for an example: https://github.com/dylanhogg/gptauthor/blob/main/gptauthor/prompts-openai-drama.yaml"
    )


def get_prompt(prompt_type: str, llm_config: DictConfig):
    return _get_conf(prompt_type, llm_config).prompt


def get_system(prompt_type: str, llm_config: DictConfig):
    return _get_conf(prompt_type, llm_config).system


def get_book_description(llm_config: DictConfig):
    return _get_common("common-book-description", llm_config)


def get_book_characters(llm_config: DictConfig):
    return _get_common("common-book-characters", llm_config)
