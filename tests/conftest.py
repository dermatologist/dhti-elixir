import pytest

from .bootstrap import bootstrap


def pytest_configure(config):
    print("Bootstrapping...")
    bootstrap()

@pytest.fixture
def starter_chain():
    from packages.starter.src.dhti_elixir_starter.chain import DhtiChain
    return DhtiChain().chain


@pytest.fixture
def simple_chain():
    from packages.simple_chat.src.dhti_elixir_schat.chain import DhtiChain
    return DhtiChain().chain


@pytest.fixture
def agent_chain():
    from packages.agent_chat.src.dhti_elixir_achat.chain import DhtiChain
    return DhtiChain().chain


@pytest.fixture
def imaging_report_chain():
    from packages.imaging_report.src.dhti_elixir_imaging_report.chain import DhtiChain
    return DhtiChain().chain
