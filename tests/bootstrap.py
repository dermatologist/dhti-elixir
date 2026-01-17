import os
from datetime import datetime
from unittest.mock import MagicMock

from dotenv import load_dotenv
from kink import di
from langchain_community.document_loaders.parsers.pdf import PDFMinerParser
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter


def bootstrap():
    load_dotenv()
    fake_llm = FakeListLLM(responses=["Paris", "I don't know"])
    di["main_prompt"] = PromptTemplate.from_template(
        "Summarize the following in 100 words: {input}"
    )
    di["main_llm"] = fake_llm
    di["cds_hook_discovery"] = {
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

    # Utils bootstrap configuration
    di["embedding_model"] = FakeEmbeddings(size=1352)
    di["upload_chunk_size"] = 100
    di["upload_chunk_overlap"] = 20

    # Schema path for tests - use mock redis_schema.yaml location
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "packages",
        "utils",
        "src",
        "dhti_elixir_utils",
        "redis_schema.yaml",
    )

    # Mock vectorstore functions
    def create_vectorstore(docs):
        """Mock implementation of create_vectorstore for testing."""
        return True

    def read_vectorstore():
        """Mock implementation of read_vectorstore for testing."""
        return MagicMock()

    # Text splitter for document processing
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=di["upload_chunk_size"],
        chunk_overlap=di["upload_chunk_overlap"],
        length_function=len,
        is_separator_regex=False,
    )

    def document_store(blob):
        """Process uploaded documents."""
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
