import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../packages/simple_rag/src")
    )
)

from unittest.mock import MagicMock, patch

from dhti_elixir_srag.chain import DhtiChain
from kink import di
from langchain_community.llms.fake import FakeListLLM


def test_srag_chain():
    # Mock Redis retriever
    mock_retriever = MagicMock(return_value=["Document 1", "Document 2"])
    di["srag_retriever"] = mock_retriever

    # Mock LLM
    di["srag_main_llm"] = FakeListLLM(responses=["Generated Answer"])

    # Initialize chain
    chain = DhtiChain().chain

    # Invoke chain
    response = chain.invoke({"input": "What is in the documents?"})

    # Verify retrieval
    mock_retriever.assert_called_with("What is in the documents?")

    # Verify response
    assert "cards" in response
    assert response["cards"][0]["summary"] is not None
