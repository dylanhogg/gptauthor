from datetime import datetime

from joblib import Memory
from loguru import logger
from omegaconf import DictConfig
from openai import AuthenticationError, OpenAI
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from .classes import AppUsageException

memory = Memory(".joblib_cache", verbose=0)

# TODO: try/catch! E.g.
#       APIError: HTTP code 502 from API
#       Timeout: Request timed out: HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out. (read timeout=600)


def log_retry(state):
    msg = (
        f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    )
    if state.attempt_number < 1:
        logger.warning(msg)
    else:
        logger.exception(msg)


@memory.cache()
@retry(
    wait=wait_exponential(multiplier=2, min=10, max=600),
    stop=stop_after_attempt(3),
    before_sleep=log_retry,
    retry=retry_if_not_exception_type(AppUsageException),
)
def make_call(system: str, prompt: str, llm_config: DictConfig) -> tuple[str, int]:
    client = OpenAI(
        api_key=llm_config.api_key if not llm_config.use_localhost else "localhost",
        base_url="http://localhost:8081" if llm_config.use_localhost else None,
    )

    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    start = datetime.now()
    try:
        api_response = client.chat.completions.create(
            model=llm_config.model, messages=messages, temperature=llm_config.temperature, top_p=llm_config.top_p
        )
    except AuthenticationError as ex:
        raise AppUsageException(str(ex)) from ex
    took = datetime.now() - start

    chat_response = api_response.choices[0].message.content
    total_tokens = int(api_response.usage.total_tokens)  # TODO: add input/output tokens

    logger.debug(f"{llm_config.use_localhost=}")
    logger.debug(f"{system=}")
    logger.debug(f"{prompt=}")
    logger.debug(f"{took=}")
    logger.debug("\n---- RESPONSE:")
    logger.debug(f"{chat_response=}")
    logger.debug(f"{total_tokens=}")

    return chat_response, total_tokens
