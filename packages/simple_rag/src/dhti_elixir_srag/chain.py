import logging

from dhti_elixir_base import BaseChain, get_di
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import override

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DhtiChain(BaseChain):

    def retrieve_context(self, input):
        """Retrieve relevant documents."""
        # Check if input is a dict (if coming from CDS hook) or string
        query = input
        if isinstance(input, dict):
             query = input.get("input", "")

        logger.info(f"Retrieving context for query: {query}")
        retriever = get_di("srag_retriever")
        docs = retriever(query)
        return "\n\n".join(docs)

    @property
    @override
    def chain(self):  # type: ignore
        _chain = (
            {"context": self.retrieve_context, "input": RunnablePassthrough()}
            | get_di("srag_main_prompt")
            | get_di("srag_main_llm")
            | StrOutputParser()
        )
        return _chain.with_types(input_type=self.input_type)
