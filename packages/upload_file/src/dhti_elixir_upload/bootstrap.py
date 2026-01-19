# Define default variables here
# Can be overridden by the user in the server

import os
from datetime import datetime

from kink import di
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders.parsers.pdf import PDFMinerParser
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.llms.fake import FakeListLLM
from langchain_community.vectorstores import Redis
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


def bootstrap():
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
        llm = FakeListLLM(responses=["I am a fake LLM", "I don't know"])
        embedding_model = FakeEmbeddings(size=1352)
    di["embedding_model"] = embedding_model
    di["main_llm"] = llm
    di["upload_chunk_size"] = 100
    di["upload_chunk_overlap"] = 20
    model = init_chat_model(
        model="nex-agi/deepseek-v3.1-nex-n1:free",
        model_provider="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

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

    def create_vectorstore(docs):
        # Store in Redis
        db = Redis.from_documents(
            documents=docs,
            embedding=di["embedding_model"],
            index_name="dhti_elixir_upload_file",
            index_schema=index_schema,
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"), # langserve container has host network. so use localhost
        )
        assert db is not None
        return True

    def read_vectorstore():
        return Redis.from_existing_index(
            embedding=di["embedding_model"],
            index_name="dhti_elixir_upload_file",
            schema=index_schema,
            redis_url=os.environ.get(
                "REDIS_URL", "redis://localhost:6379"
            ),  # langserve container has host network. so use localhost
        )

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=di["upload_chunk_size"],
        chunk_overlap=di["upload_chunk_overlap"],
        length_function=len,
        is_separator_regex=False,
    )

    def document_store(blob):
        documents = list(PDFMinerParser().lazy_parse(blob))
        pages = ""
        for doc in documents:
            pages += doc.page_content
        docs = text_splitter.create_documents([pages])
        current_year = datetime.now().year
        metadata = {"authors": "DHTI", "year": str(current_year)}
        _docs = []
        for doc in docs:
            doc.page_content = doc.page_content
            doc.metadata = metadata
            _docs.append(doc)
        create_vectorstore(_docs)
        return f"Uploaded {len(_docs)} chunks to the vector store."

    di["process_file_function"] = document_store
    di["read_vectorstore_function"] = read_vectorstore

    di["dhti_elixir_upload_cds_hook_discovery"] = {
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
