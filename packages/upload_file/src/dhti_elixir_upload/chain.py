import logging

from dhti_elixir_base import BaseChain
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import override

from packages.utils.src.dhti_elixir_utils.upload import FileProcessingRequest
from packages.utils.src.dhti_elixir_utils.upload import upload


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DhtiChain(BaseChain):

    @override
    class ChainInput(FileProcessingRequest):
        """
        Input model for BaseChain.

        """
        pass


    @property
    @override
    def chain(self):  # type: ignore
        _chain = (
            RunnablePassthrough()
            | upload
        )
        return _chain.with_types(input_type=self.input_type)
