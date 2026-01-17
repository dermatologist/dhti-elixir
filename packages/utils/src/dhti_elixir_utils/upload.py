"""
Copyright 2024 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64

from dhti_elixir_base import get_di
from langchain_core.document_loaders import Blob
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langserve import CustomUserType
from pydantic import Field

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=get_di("upload_chunk_size"),
    chunk_overlap=get_di("upload_chunk_overlap"),
    length_function=len,
    is_separator_regex=False,
)


# ATTENTION: Inherit from CustomUserType instead of BaseModel otherwise
#            the server will decode it into a dict instead of a pydantic model.
class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., json_schema_extra={"widget": {"type": "base64file"}})



def process_file(request: FileProcessingRequest) -> str:
    """Extract the text from the first page of the PDF."""
    content = base64.b64decode(request.file.encode("utf-8"))
    blob = Blob(data=content)
    return get_di("process_file_function")(blob) # type: ignore


# List of runnables
_chain = (RunnableLambda(process_file).with_types(input_type=FileProcessingRequest),)
upload = _chain[0]
