import pytest
from .bootstrap import bootstrap

def pytest_configure(config):
    print("Bootstrapping...")
    bootstrap()

@pytest.fixture
def simple_chain():
    from packages.simple_chat.src.dhti_elixir_template.chain import DhtiChain
    return DhtiChain().chain

@pytest.fixture
def SimpleChain():
    from packages.simple_chat.src.dhti_elixir_template.chain import DhtiChain
    return DhtiChain