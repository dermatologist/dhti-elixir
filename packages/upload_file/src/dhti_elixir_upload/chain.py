import base64
import logging

from dhti_elixir_base import BaseChain, get_di
from langchain_core.document_loaders import Blob
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langserve import CustomUserType
from pydantic import Field
from typing_extensions import override

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=get_di("upload_chunk_size"),
    chunk_overlap=get_di("upload_chunk_overlap"),
    length_function=len,
    is_separator_regex=False,
)


# ATTENTION: Inherit from CustomUserType instead of BaseModel otherwise
#            the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    file: str = Field(..., extra={"widget": {"type": "base64file"}}) # type: ignore



def process_file(request: FileProcessingRequest) -> str:
    """Extract the text from the first page of the PDF."""
    content = base64.b64decode(request.file.encode("utf-8"))
    blob = Blob(data=content)
    return get_di("process_file_function")(blob)  # type: ignore


_chain = (RunnableLambda(process_file).with_types(input_type=FileProcessingRequest),)
upload = _chain[0]


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DhtiChain(BaseChain):

    @override
    class ChainInput(FileProcessingRequest): # type: ignore
        """
        Input model for BaseChain.

        """

        pass

    @property
    @override
    def chain(self):  # type: ignore
        _chain = RunnablePassthrough() | upload
        return _chain.with_types(input_type=self.input_type)
