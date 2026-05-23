# from unittest.mock import patch, MagicMock
from gptauthor.library.utils import calculate_model_price_estimate

# https://platform.openai.com/docs/pricing


def test_calculate_model_price_estimate_1():
    model_name = "gpt-4o-2024-08-06"
    token_count = 1000000
    usd_total_cost = 10
    assert calculate_model_price_estimate(model_name, token_count) == usd_total_cost


def test_calculate_model_price_estimate_2():
    model_name = "gpt-4"
    token_count = 1000000
    usd_total_cost = 60
    assert calculate_model_price_estimate(model_name, token_count) == usd_total_cost


def test_calculate_model_price_estimate_3():
    model_name = "gpt-5.4-mini"
    token_count = 1000000
    usd_total_cost = 4.5
    assert calculate_model_price_estimate(model_name, token_count) == usd_total_cost


def test_calculate_model_price_estimate_4():
    model_name = "gpt-5.5"
    token_count = 1000000
    usd_total_cost = 30
    assert calculate_model_price_estimate(model_name, token_count) == usd_total_cost
