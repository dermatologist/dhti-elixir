import pytest

from .bootstrap import bootstrap


def pytest_configure(config):
    print("Bootstrapping...")
    bootstrap()


@pytest.fixture
def simple_chain():
    from packages.simple_chat.src.dhti_elixir_schat.chain import DhtiChain
    return DhtiChain().chain


@pytest.fixture
def agent_chain():
    from packages.agent_chat.src.dhti_elixir_achat.chain import DhtiChain
    return DhtiChain().chain
