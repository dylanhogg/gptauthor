import importlib.resources

from omegaconf import DictConfig, OmegaConf

from gptauthor.library import consts
from gptauthor.library.classes import AppUsageException


def _get_common(key: str, llm_config: DictConfig):
    yaml_file = importlib.resources.files(consts.package_name).joinpath(llm_config.story_file)
    conf_file = OmegaConf.load(yaml_file)
    if key not in conf_file:
        raise Exception(f"{key} not in conf_file")
    return conf_file[key]


def _get_conf(prompt_type: str, llm_config) -> (str, dict):
    yaml_file = importlib.resources.files(consts.package_name).joinpath(llm_config.story_file)
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


def get_prompt(prompt_type: str, llm_config: DictConfig):
    return _get_conf(prompt_type, llm_config).prompt


def get_system(prompt_type: str, llm_config: DictConfig):
    return _get_conf(prompt_type, llm_config).system


def get_book_description(llm_config: DictConfig):
    return _get_common("common-book-description", llm_config)


def get_book_characters(llm_config: DictConfig):
    return _get_common("common-book-characters", llm_config)
