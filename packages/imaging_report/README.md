# DHTI Imaging Report Elixir

## Overview

The Imaging Report Elixir is a vision-capable DHTI elixir service that processes medical imaging queries using vision-capable GenAI models. It can analyze medical images and generate detailed reports based on image content and user queries.

## Features

- **Dual Input Mode**: Accepts either plain text or JSON payloads containing image URLs
- **Vision-Capable**: Uses state-of-the-art vision models (GPT-4o, Gemini Pro Vision) to analyze medical images
- **Flexible Image Sources**: Supports both data URLs (`data:image/png;base64,...`) and standard URLs (`https://...`)
- **Intelligent Routing**: Automatically detects input format and routes to appropriate processing pipeline
- **Text Fallback**: Processes plain text queries like a standard chat interface when no image is provided

## Installation

Using dhti-cli:

```bash
dhti-cli elixir install -g dermatologist/dhti-elixir -s packages/imaging_report
```

## Usage

### Text-Only Input

For simple text queries without images:

```json
{
  "input": "What are the common signs of pneumonia on a chest X-ray?"
}
```

### Vision Input with Image URL

For analyzing medical images:

```json
{
  "input": "{\"image_url\": \"https://example.com/chest-xray.jpg\", \"text\": \"Analyze this chest X-ray for signs of pneumonia\"}"
}
```

Or with a data URL:

```json
{
  "input": "{\"image_url\": \"data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...\", \"text\": \"What abnormalities do you see in this CT scan?\"}"
}
```

### Direct JSON Input

If your system supports direct JSON payloads:

```json
{
  "input": {
    "image_url": "https://example.com/mri-scan.jpg",
    "text": "Describe the findings in this MRI scan"
  }
}
```

## Configuration

### Environment Variables

- **GOOGLE_API_KEY**: Google API key for Gemini Pro Vision model (recommended for vision tasks)
- **OPENAI_API_KEY**: OpenAI API key for GPT-4o model (alternative vision model)
- **OPENROUTER_API_KEY**: OpenRouter API key for additional model support
- **FHIR_BASE_URL**: FHIR server base URL (default: `http://backend:8080/openmrs/ws/fhir2/R4`)
- **FHIR_ACCESS_TOKEN**: FHIR server access token (default: `YWRtaW46QWRtaW4xMjM=`)

### Vision Models

The elixir automatically selects the best available vision-capable model:

1. **Gemini 2.0 Flash Exp** (if GOOGLE_API_KEY is set) - Fast and efficient vision model
2. **GPT-4o** (if OPENAI_API_KEY is set) - High-quality vision and text understanding
3. **Fake LLM** (fallback for testing) - Simulated responses for development

## API Endpoints

- **POST /langserve/dhti_elixir/invoke**: Main endpoint for invoking the chain
- **POST /langserve/dhti_elixir/batch**: Batch processing endpoint
- **GET /langserve/dhti_elixir/playground**: Interactive playground for testing
- **GET /langserve/dhti_elixir/services**: CDS Hooks service discovery endpoint

## Integration with DHTI

This elixir integrates seamlessly with DHTI as a CDS Hooks service. It supports:

- **Hook**: `order-select`
- **Resources**: ImagingStudy, DiagnosticReport
- **Scopes**: Patient and practitioner read access

## Development

### Running Tests

```bash
cd /path/to/dhti-elixir
uv run pytest tests/imaging_report/ -v
```

### Running the Server Locally

```bash
cd packages/imaging_report
uv run python src/dhti_elixir_imaging_report/server.py
```

The server will start on `http://localhost:8002`.

## Architecture

### Input Processing Flow

1. **Input Detection**: The chain analyzes the input to determine if it contains image data
2. **JSON Parsing**: Attempts to parse input as JSON and extract `image_url` and `text` fields
3. **URL Validation**: Validates that image_url is either a data URL or HTTP(S) URL
4. **Mode Selection**: Routes to vision processing or text processing based on detected input type
5. **LLM Invocation**: Calls the appropriate model with properly formatted prompts
6. **Response Generation**: Returns the model's analysis or response

### Vision Processing

For vision inputs, the elixir:

1. Creates a multimodal message with both text and image content
2. Sends the message to a vision-capable LLM (GPT-4o or Gemini Pro Vision)
3. Includes a system prompt optimized for medical imaging analysis
4. Returns the model's detailed analysis

### Text Processing

For text-only inputs, the elixir:

1. Uses a simple text prompt template
2. Invokes the LLM with standard text processing
3. Returns the model's response

## Dependencies

- `dhti-elixir-base>=1.4.1`: Core DHTI functionality
- `fhiry>=5.2.1`: FHIR resource handling
- `langchain-google-genai`: Google Gemini model support
- `langchain-openai`: OpenAI GPT model support
- `langchain-core`: LangChain core components

## Example Use Cases

1. **Radiology Reports**: Analyze X-rays, CT scans, MRI images and generate diagnostic reports
2. **Dermatology**: Evaluate skin lesion images for signs of conditions
3. **Pathology**: Analyze microscopy images and provide findings
4. **Telehealth**: Support remote consultations with image-based diagnosis
5. **Medical Education**: Help students learn to interpret medical images

## Best Practices

- Use high-quality images for better analysis results
- Provide specific, clear questions in the text field
- Consider image file size when using data URLs (base64 encoding increases size by ~33%)
- Use HTTPS URLs for external images to ensure secure transmission
- Test with the fake LLM first before using production API keys

## Troubleshooting

### Issue: "No valid image_url found"

**Solution**: Ensure your image_url starts with `data:image/`, `http://`, or `https://`

### Issue: "Model doesn't support vision"

**Solution**: Verify that you're using a vision-capable model (GPT-4o or Gemini Pro Vision) and have set the appropriate API key

### Issue: "JSON parsing error"

**Solution**: Ensure your JSON is properly formatted and stringified if passing as a string

## License

See the main repository LICENSE file.

## Contributing

Contributions are welcome! Please see the main repository [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/dermatologist/dhti-elixir).