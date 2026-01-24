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
    # Check if google api key is set in the environment
    if os.environ.get("GOOGLE_API_KEY"):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    # Check if openai api key is set in the environment
    elif os.environ.get("OPENAI_API_KEY"):
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
    else:
        llm = FakeListLLM(responses=["I am a fake LLM", "I don't know"])
    di["main_llm"] = llm

    try:
        model = init_chat_model(
            model="nex-agi/deepseek-v3.1-nex-n1:free",
            model_provider="openai",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
    except Exception:
        model = FakeListLLM(responses=["I am a function calling fake LLM."])

    di["function_llm"] = model
    di["main_prompt"] = PromptTemplate.from_template(
        "Summarize the following in 100 words: {input}"
    )
    di["schat_main_prompt"] = PromptTemplate.from_template(
        "You are a medical assistant. "
        "Using the following patient information:{fhir_context}, "
        "and a response from a medical knowledge agent: {agent_response}, "
        "answer the question: {query} briefly and accurately."
    )
    di["dhti_elixir_schat_cds_hook_discovery"] = {
        "services": [
            {
                "id": "dhti-service",
                "hook": "order-select",
                "title": "MyOrg Order Assistant",
                "description": "Provides suggestions and actions for selected draft orders, including handling CommunicationRequest resources.",
                "prefetch": {
                    "patient": "Patient/{{context.patientId}}",
                    "draftOrders": "Bundle?patient={{context.patientId}}&status=draft",
                },
                "scopes": [
                    "launch",
                    "patient/Patient.read",
                    "user/Practitioner.read",
                    "patient/CommunicationRequest.read",
                ],
                "metadata": {
                    "author": "MyOrg CDS Team",
                    "version": "1.0.0",
                    "supportedResources": [
                        "CommunicationRequest",
                    ],
                },
            }
        ]
    }
