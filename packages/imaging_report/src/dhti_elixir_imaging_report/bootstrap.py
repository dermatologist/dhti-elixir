# Define default variables here
# Can be overridden by the user in the server

import os

from kink import di
from langchain.chat_models import init_chat_model
from langchain_community.llms.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


def bootstrap():
    di["fhir_access_token"] = os.environ.get(
        "FHIR_ACCESS_TOKEN", "YWRtaW46QWRtaW4xMjM="
    )  # admin:Admin123 in base64
    di["fhir_base_url"] = os.environ.get(
        "FHIR_BASE_URL", "http://backend:8080/openmrs/ws/fhir2/R4"
    )

    # Configure vision-capable LLM
    # Check if google api key is set in the environment - gemini supports vision
    if os.environ.get("GOOGLE_API_KEY"):
        # Use Gemini Pro Vision or Flash Vision model
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
    # Check if openai api key is set in the environment - gpt-4o supports vision
    elif os.environ.get("OPENAI_API_KEY"):
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
    else:
        # Fallback to fake LLM for testing
        llm = FakeListLLM(
            responses=[
                "This is a simulated vision model response analyzing the image.",
                "I am a fake vision-capable LLM for testing purposes.",
            ]
        )

    # Optional: Configure function calling LLM
    try:
        model = init_chat_model(
            model="nex-agi/deepseek-v3.1-nex-n1:free",
            model_provider="openai",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
    except Exception:
        model = FakeListLLM(responses=["I am a function calling fake LLM."])

    di["main_llm"] = llm

    di["function_llm"] = model

    # System prompt for vision mode
    di["imaging_report_system_prompt"] = (
        "You are an expert medical imaging assistant. "
        "Analyze medical images and provide detailed, accurate reports based on the image content and user's query. "
        "Focus on relevant clinical details and use appropriate medical terminology."
    )

    # Text prompt for text-only mode (fallback)
    di["imaging_report_text_prompt"] = PromptTemplate.from_template(
        "You are a medical assistant. Answer the following question: {input}"
    )

    # CDS Hook discovery configuration
    di["dhti_elixir_imaging_report_cds_hook_discovery"] = {
        "services": [
            {
                "id": "dhti-service",
                "hook": "order-select",
                "title": "Medical Imaging Report Assistant",
                "description": "Analyzes medical images and generates reports using vision-capable AI models.",
                "prefetch": {
                    "patient": "Patient/{{context.patientId}}",
                    "draftOrders": "Bundle?patient={{context.patientId}}&status=draft",
                },
                "scopes": [
                    "launch",
                    "patient/Patient.read",
                    "user/Practitioner.read",
                    "patient/ImagingStudy.read",
                    "patient/DiagnosticReport.read",
                ],
                "metadata": {
                    "author": "DHTI Imaging Team",
                    "version": "1.0.0",
                    "supportedResources": [
                        "ImagingStudy",
                        "DiagnosticReport",
                    ],
                },
            }
        ]
    }
