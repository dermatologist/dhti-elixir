import json

import pytest


def test_chain_invoke_text_input(imaging_report_chain, capsys):
    """Test text-only input processing."""
    input_data = {"input": "What are common signs of pneumonia on chest X-rays?"}
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    # Should process as text and return some response
    assert len(captured.out) > 0


def test_chain_invoke_vision_input_json_string(imaging_report_chain, capsys):
    """Test vision input with JSON string containing image_url and text."""
    vision_input = {
        "image_url": "https://example.com/chest-xray.jpg",
        "text": "Analyze this chest X-ray for signs of pneumonia"
    }
    input_data = {"input": json.dumps(vision_input)}
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    # Should process as vision input
    assert len(captured.out) > 0


def test_chain_invoke_vision_input_dict(imaging_report_chain, capsys):
    """Test vision input with direct dict containing image_url and text."""
    input_data = {
        "input": {
            "image_url": "https://example.com/mri-scan.jpg",
            "text": "Describe findings in this MRI scan"
        }
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_chain_invoke_vision_input_data_url(imaging_report_chain, capsys):
    """Test vision input with data URL."""
    input_data = {
        "input": {
            "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "text": "What do you see in this image?"
        }
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_chain_invoke_invalid_image_url(imaging_report_chain, capsys):
    """Test handling of invalid image_url (should fallback to text mode)."""
    input_data = {
        "input": {
            "image_url": "not-a-valid-url",
            "text": "This should fallback to text mode"
        }
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    # Should fallback to text processing
    assert len(captured.out) > 0


def test_chain_invoke_json_without_image_url(imaging_report_chain, capsys):
    """Test JSON input without image_url field (should process as text)."""
    input_data = {
        "input": json.dumps({
            "text": "Just a text query without image",
            "other_field": "value"
        })
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_chain_invoke_with_hook(imaging_report_chain, capsys):
    """Test with CDS Hook format input."""
    input_data = {
        "hookInstance": "test_hook",
        "fhirServer": "http://example.com/fhir",
        "fhirAuthorization": "Bearer test_token",
        "hook": "order-select",
        "context": {
            "input": "What imaging findings suggest pneumonia?"
        },
        "prefetch": {},
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_chain_invoke_with_hook_vision(imaging_report_chain, capsys):
    """Test with CDS Hook format input including vision data."""
    input_data = {
        "hookInstance": "test_hook_vision",
        "fhirServer": "http://example.com/fhir",
        "fhirAuthorization": "Bearer test_token",
        "hook": "order-select",
        "context": {
            "input": {
                "image_url": "https://example.com/ct-scan.jpg",
                "text": "Analyze this CT scan"
            }
        },
        "prefetch": {},
    }
    result = imaging_report_chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_parse_input_text_mode(imaging_report_chain):
    """Test input parsing for text mode."""
    from packages.imaging_report.src.dhti_elixir_imaging_report.chain import DhtiChain
    
    chain_instance = DhtiChain()
    context = {"input": "Plain text query"}
    parsed = chain_instance.parse_input(context)
    
    assert parsed["mode"] == "text"
    assert parsed["text"] == "Plain text query"


def test_parse_input_vision_mode(imaging_report_chain):
    """Test input parsing for vision mode."""
    from packages.imaging_report.src.dhti_elixir_imaging_report.chain import DhtiChain
    
    chain_instance = DhtiChain()
    context = {
        "input": {
            "image_url": "https://example.com/image.jpg",
            "text": "Analyze this"
        }
    }
    parsed = chain_instance.parse_input(context)
    
    assert parsed["mode"] == "vision"
    assert parsed["image_url"] == "https://example.com/image.jpg"
    assert parsed["text"] == "Analyze this"


def test_parse_input_json_string_vision(imaging_report_chain):
    """Test parsing JSON string for vision input."""
    from packages.imaging_report.src.dhti_elixir_imaging_report.chain import DhtiChain
    
    chain_instance = DhtiChain()
    vision_data = {
        "image_url": "data:image/png;base64,abc123",
        "text": "What is this?"
    }
    context = {"input": json.dumps(vision_data)}
    parsed = chain_instance.parse_input(context)
    
    assert parsed["mode"] == "vision"
    assert "data:image/png;base64" in parsed["image_url"]
    assert parsed["text"] == "What is this?"
