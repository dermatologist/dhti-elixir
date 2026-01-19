"""
Unit tests for DhtiChain in chain.py, mocking redis and process_file_function as needed.
"""

import base64
from unittest.mock import MagicMock, patch

import pytest

from packages.upload_file.src.dhti_elixir_upload.chain import DhtiChain


@pytest.fixture
def sample_pdf_bytes():
    return b"%PDF-1.4 test PDF content"


@pytest.fixture
def encoded_pdf(sample_pdf_bytes):
    return base64.b64encode(sample_pdf_bytes).decode("utf-8")


@pytest.fixture
def chain():
    return DhtiChain()


def test_chaininput_model_accepts_base64(chain, encoded_pdf):
    model = chain.ChainInput(input=encoded_pdf)
    assert model.input == encoded_pdf


def test_process_file_calls_di_function(chain, encoded_pdf):
    mock_func = MagicMock()
    with patch(
        "packages.upload_file.src.dhti_elixir_upload.chain.get_di",
        return_value=mock_func,
    ):
        result = chain.process_file(encoded_pdf)
        assert result == "File processed successfully."
        assert mock_func.called


def test_process_file_decodes_base64(chain, sample_pdf_bytes, encoded_pdf):
    with patch(
        "packages.upload_file.src.dhti_elixir_upload.chain.get_di",
        return_value=lambda x: None,
    ) as mock_di:
        with patch(
            "packages.upload_file.src.dhti_elixir_upload.chain.Blob"
        ) as mock_blob:
            chain.process_file(encoded_pdf)
            mock_blob.assert_called_once()
            args, kwargs = mock_blob.call_args
            assert kwargs["data"] == sample_pdf_bytes


def test_chain_property_returns_runnable(chain):
    chain_obj = chain.chain
    assert hasattr(chain_obj, "invoke")
    assert hasattr(chain_obj, "with_types")


def test_chain_integration_with_mocked_process(chain, encoded_pdf):
    mock_func = MagicMock()
    with patch(
        "packages.upload_file.src.dhti_elixir_upload.chain.get_di",
        return_value=mock_func,
    ):
        chain_obj = chain.chain
        result = chain_obj.invoke(input={"input": encoded_pdf})
        # The chain now returns a dict with a 'cards' key containing a summary
        assert isinstance(result, dict)
        assert "cards" in result
        assert result["cards"][0]["summary"] == "File processed successfully."
