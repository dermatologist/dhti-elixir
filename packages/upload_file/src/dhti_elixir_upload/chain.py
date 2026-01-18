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
import logging

from dhti_elixir_base import BaseChain, get_di
from dhti_elixir_base.cds_hook.generate_cards import get_card
from dhti_elixir_base.cds_hook.request_parser import get_context
from langchain_core.document_loaders import Blob
from langchain_core.runnables import RunnablePassthrough
from pydantic import Field
from typing_extensions import override
from pydantic import BaseModel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DhtiChain(BaseChain):
    """Chain for processing uploaded PDF files."""
    @override
    class ChainInput(BaseModel):  # type: ignore
        """Input model for BaseChain."""
        file: str = Field(..., extra={"widget": {"type": "base64file"}}) # type: ignore


    def process_file(self, input):
        """Extract the text from the PDF file and process it."""
        content = base64.b64decode(input["file"].encode("utf-8"))
        logger.info(
            "Decoded file content from base64." + str(len(content)) + " bytes received."
        )
        blob = Blob(data=content)
        get_di("process_file_function")(blob)  # type: ignore
        return "File processed successfully."

    @property
    @override
    def chain(self):  # type: ignore
        """Return the processing chain."""
        _chain = RunnablePassthrough() | get_context | self.process_file | get_card
        return _chain.with_types(input_type=self.ChainInput)  # type: ignore
