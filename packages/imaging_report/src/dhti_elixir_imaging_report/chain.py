import json
import logging

from dhti_elixir_base import BaseChain, get_di
from dhti_elixir_base.cds_hook.generate_cards import get_card
from dhti_elixir_base.cds_hook.request_parser import get_context
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import override

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DhtiChain(BaseChain):

    def print_log(self, message):
        logger.info(message)
        return message

    def parse_input(self, context):
        """
        Parse the input to determine if it's a string or JSON containing image_url and text.
        Returns a dict with 'mode' ('text' or 'vision'), 'text', and optionally 'image_url'.
        """
        try:
            # Extract the actual input from the context
            input_data = context.get("input", "")
            
            # If input is already a dict, use it directly
            if isinstance(input_data, dict):
                parsed_input = input_data
            else:
                # Try to parse as JSON
                try:
                    parsed_input = json.loads(input_data)
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, treat as plain text
                    self.print_log(f"Input is plain text: {input_data[:50]}...")
                    return {
                        "mode": "text",
                        "text": input_data,
                        "context": context
                    }
            
            # Check if parsed_input has image_url field
            if isinstance(parsed_input, dict) and "image_url" in parsed_input:
                image_url = parsed_input.get("image_url", "")
                text = parsed_input.get("text", "")
                
                # Validate image_url (must be data URL or http(s) URL)
                if image_url.startswith(("data:image/", "http://", "https://")):
                    self.print_log(f"Input is vision mode with image_url: {image_url[:50]}...")
                    return {
                        "mode": "vision",
                        "text": text,
                        "image_url": image_url,
                        "context": context
                    }
            
            # Default to text mode if no valid image_url found
            self.print_log("No valid image_url found, defaulting to text mode")
            return {
                "mode": "text",
                "text": str(parsed_input),
                "context": context
            }
            
        except Exception as e:
            self.print_log(f"Error parsing input: {e}")
            return {
                "mode": "text",
                "text": str(context.get("input", "")),
                "context": context
            }

    def process_text_input(self, parsed_data):
        """Process plain text input using simple chat behavior."""
        text = parsed_data["text"]
        llm = get_di("imaging_report_main_llm")
        prompt = get_di("imaging_report_text_prompt")
        
        # Create a simple chain for text processing
        result = (prompt | llm | StrOutputParser()).invoke({"input": text})
        return result

    def process_vision_input(self, parsed_data):
        """Process vision input with image_url and text using multimodal model."""
        text = parsed_data["text"]
        image_url = parsed_data["image_url"]
        llm = get_di("imaging_report_main_llm")
        
        # Get system prompt
        system_prompt = get_di("imaging_report_system_prompt")
        
        # Create multimodal message with image and text
        # Use HumanMessage with structured content for vision models
        message = HumanMessage(
            content=[
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
        
        # Create messages list with system prompt
        messages = [
            SystemMessage(content=system_prompt),
            message
        ]
        
        # Invoke the LLM with the multimodal messages
        result = llm.invoke(messages)
        
        # Extract content from result
        if hasattr(result, "content"):
            return result.content
        return str(result)

    def route_and_process(self, context):
        """Route to appropriate processing based on input type."""
        parsed_data = self.parse_input(context)
        
        if parsed_data["mode"] == "vision":
            return self.process_vision_input(parsed_data)
        else:
            return self.process_text_input(parsed_data)

    @property
    @override
    def chain(self):  # type: ignore
        _chain = (
            RunnablePassthrough()
            | get_context
            | self.route_and_process
            | get_card
        )
        return _chain.with_types(input_type=self.input_type)
