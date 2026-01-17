import base64
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from kink import di

from packages.utils.src.dhti_elixir_utils.upload import (
    FileProcessingRequest,
    process_file,
)


@pytest.fixture
def sample_pdf_bytes():
    """Create a minimal PDF for testing."""
    # This is a minimal PDF structure for testing
    pdf_content = b"""%PDF-1.4
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
    return pdf_content


@pytest.fixture
def sample_file_request(sample_pdf_bytes):
    """Create a FileProcessingRequest with base64 encoded PDF."""
    encoded_pdf = base64.b64encode(sample_pdf_bytes).decode("utf-8")
    return FileProcessingRequest(file=encoded_pdf) # type: ignore


def test_file_processing_request_creation(sample_file_request):
    """Test that FileProcessingRequest can be created successfully."""
    assert sample_file_request is not None
    assert isinstance(sample_file_request.file, str)
    # Verify it can be decoded back
    decoded = base64.b64decode(sample_file_request.file.encode("utf-8"))
    assert decoded is not None


def test_process_file_integration(sample_file_request):
    """Test the process_file function with mocked DI function."""
    # Mock the document_store function
    mock_document_store = MagicMock(
        return_value="Uploaded 5 chunks to the vector store."
    )
    di["process_file_function"] = mock_document_store

    # Call process_file
    result = process_file(sample_file_request)

    # Verify the mock was called
    assert mock_document_store.called
    assert result == "Uploaded 5 chunks to the vector store."


def test_process_file_with_invalid_base64():
    """Test process_file with invalid base64 data."""
    invalid_request = FileProcessingRequest(file="not-valid-base64!")
    mock_document_store = MagicMock()
    di["process_file_function"] = mock_document_store

    with pytest.raises(Exception):
        process_file(invalid_request)


def test_process_file_calls_document_store_with_blob(sample_file_request):
    """Test that process_file correctly passes Blob to document_store."""
    mock_document_store = MagicMock(return_value="Success")
    di["process_file_function"] = mock_document_store

    result = process_file(sample_file_request)

    # Verify the function was called once
    assert mock_document_store.call_count == 1

    # Verify it was called with a Blob object
    call_args = mock_document_store.call_args
    assert call_args is not None
    blob_arg = call_args[0][0]
    assert blob_arg.data is not None
