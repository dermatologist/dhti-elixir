# Define default variables here
# Can be overridden by the user in the server

import os

from kink import di
from langchain.chat_models import init_chat_model
from langchain_community.llms.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Redis
from langchain_community.embeddings import FakeEmbeddings


def bootstrap():
    di["rag_k"] = 3
    di["fhir_access_token"] = os.environ.get(
        "FHIR_ACCESS_TOKEN", "YWRtaW46QWRtaW4xMjM="
    )  # admin:Admin123 in base64
    di["fhir_base_url"] = os.environ.get(
        "FHIR_BASE_URL", "http://backend:8080/openmrs/ws/fhir2/R4"
    )
    # Check if google api key is set in the environment
    if os.environ.get("GOOGLE_API_KEY"):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )
    # Check if openai api key is set in the environment
    elif os.environ.get("OPENAI_API_KEY"):
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        embedding_model = ChatOpenAI(model="text-embedding-3-small")
    else:
        llm = FakeListLLM(responses=["The moon is made of green cheese."])
        embedding_model = FakeEmbeddings(size=1352)

    di["embedding_model"] = embedding_model
    di["srag_main_llm"] = llm

    model = init_chat_model(
        model="nex-agi/deepseek-v3.1-nex-n1:free",
        model_provider="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

    di["function_llm"] = model

    index_schema = {
        "numeric": [{"name": "year", "no_index": False, "sortable": False}],
        "text": [
            {
                "name": "authors",
                "no_index": False,
                "no_stem": False,
                "sortable": False,
                "weight": 0.5,
                "withsuffixtrie": False,
            },
            {
                "name": "content",
                "no_index": False,
                "no_stem": False,
                "sortable": False,
                "weight": 1,
                "withsuffixtrie": False,
            },
        ],
        "vector": [
            {
                "algorithm": "FLAT",
                "datatype": "FLOAT32",
                "dims": 384,
                "distance_metric": "COSINE",
                "name": "content_vector",
            }
        ],
    }

    def read_vectorstore():
        return Redis.from_existing_index(
            embedding=di["embedding_model"],
            index_name="dhti_elixir_upload_file",
            schema=index_schema,
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        )

    def retrieve_documents(query):
        try:
            db = read_vectorstore()
            docs = db.similarity_search(query, k=di["rag_k"])
            return [doc.page_content for doc in docs]
        except Exception:
            return ["Error connecting to Redis"]

    di["srag_retriever"] = retrieve_documents

    di["main_prompt"] = PromptTemplate.from_template(
        "Summarize the following in 100 words: {input}"
    )
    di["srag_main_prompt"] = PromptTemplate.from_template(
        "You are a helpful assistant. "
        "Use the following pieces of retrieved context to answer the question. "
        "Context: {context} "
        "Question: {input}"
    )

    di["dhti_elixir_srag_cds_hook_discovery"] = {
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
