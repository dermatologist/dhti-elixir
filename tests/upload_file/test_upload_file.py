"""
Tests for the upload_file chain.
"""

import base64
from unittest.mock import MagicMock

import pytest
from kink import di


@pytest.fixture
def upload_chain():
    """Create the upload_file chain fixture."""
    from packages.upload_file.src.dhti_elixir_upload.chain import DhtiChain

    return DhtiChain().chain


@pytest.fixture
def file_processing_request():
    """Create a FileProcessingRequest fixture."""
    from packages.upload_file.src.dhti_elixir_upload.chain import FileProcessingRequest

    return FileProcessingRequest


@pytest.fixture
def sample_pdf_bytes():
    """Create a minimal PDF for testing."""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000273 00000 n
0000000383 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
481
%%EOF"""


def test_chain_creation(upload_chain):
    """Test that the upload chain can be created successfully."""
    assert upload_chain is not None
    assert hasattr(upload_chain, "invoke")


def test_chain_invoke_with_pdf(
    upload_chain, file_processing_request, sample_pdf_bytes, capsys
):
    """Test the upload chain with a valid PDF file."""
    encoded_pdf = base64.b64encode(sample_pdf_bytes).decode("utf-8")
    request = file_processing_request(file=encoded_pdf)

    mock_process_file = MagicMock(return_value="Uploaded 5 chunks to the vector store.")
    di["process_file_function"] = mock_process_file

    result = upload_chain.invoke(input=request)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert (
        "Uploaded" in captured.out or result == "Uploaded 5 chunks to the vector store."
    )


def test_chain_invoke_with_invalid_base64(upload_chain, file_processing_request):
    """Test the chain with invalid base64 data."""
    with pytest.raises(Exception):
        invalid_request = file_processing_request(file="not-valid-base64!")
        upload_chain.invoke(input=invalid_request)  # type: ignore


def test_chain_input_type(upload_chain, file_processing_request):
    """Test that the chain has the correct input type."""
    encoded_pdf = base64.b64encode(b"%PDF-1.4 test").decode("utf-8")
    request = file_processing_request(file=encoded_pdf)

    mock_process_file = MagicMock(return_value="Success")
    di["process_file_function"] = mock_process_file

    result = upload_chain.invoke(input=request)  # type: ignore
    assert result == "Success"


def test_chain_processes_through_upload_runnable(
    upload_chain, file_processing_request, sample_pdf_bytes
):
    """Test that the chain correctly processes data through the upload runnable."""
    encoded_pdf = base64.b64encode(sample_pdf_bytes).decode("utf-8")
    request = file_processing_request(file=encoded_pdf)

    mock_process_file = MagicMock(return_value="Processed successfully")
    di["process_file_function"] = mock_process_file

    result = upload_chain.invoke(input=request)  # type: ignore

    assert mock_process_file.called
    assert result == "Processed successfully"


def test_chain_with_actual_document_store(
    upload_chain, file_processing_request, sample_pdf_bytes
):
    """Test the chain with the real document_store function from bootstrap."""
    encoded_pdf = base64.b64encode(sample_pdf_bytes).decode("utf-8")
    request = file_processing_request(file=encoded_pdf)

    # Reset DI to get real document_store
    from tests.bootstrap import bootstrap

    bootstrap()

    result = upload_chain.invoke(input=request)  # type: ignore

    assert "Uploaded" in result
    assert "chunks" in result
