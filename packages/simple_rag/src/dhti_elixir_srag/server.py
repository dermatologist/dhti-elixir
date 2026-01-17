from fastapi import FastAPI
from langserve import add_routes
from langchain_core.runnables.config import RunnableConfig
from dhti_elixir_base.cds_hook.routes import add_services, add_invokes
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
mcp_server = FastMCP(name="dhti-mcp-server")
from pydantic import BaseModel, ConfigDict

class ChainInputString(BaseModel):
    """
    Input model for BaseChain.

    Attributes:
        input (Any): The input string or CDSHookRequest object for the chain.
    """

    input: str
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)
# ! DO NOT REMOVE THE COMMENT BELOW
# DHTI_CLI_IMPORT
from bootstrap import bootstrap as dhti_elixir_bootstrap

dhti_elixir_bootstrap()
# add src to sys path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from chain import DhtiChain as dhti_elixir_chain_class
dhti_elixir_chain_class.input_type = ChainInputString
dhti_elixir_chain = dhti_elixir_chain_class().get_chain_as_langchain_tool()
dhti_elixir_mcp_tool = dhti_elixir_chain_class().get_chain_as_mcp_tool
# 1. Define your MCP server
mcp_server.add_tool(dhti_elixir_mcp_tool) # type: ignore

import uvicorn

# Comes after elixir bootstraps, so can override elixir configurations
from bootstrap import bootstrap

bootstrap()


app = FastAPI(title="dhti-elixir-srag-server")
# Mount the MCP server's ASGI application at a specific path (Exposes /messages and /sse endpoints)
app.mount("/langserve/mcp", mcp_server.sse_app())

origins = [
        "*",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a root endpoint
@app.get("/langserve")
async def read_root():
    return {"message": "Hello from DHTI!"}


try:
    from langfuse import Langfuse # type: ignore
    from langfuse.callback import CallbackHandler # type: ignore

    langfuse_handler = CallbackHandler()
    langfuse_handler.auth_check()
    config = RunnableConfig(callbacks=[langfuse_handler])
    # ! DO NOT REMOVE THE COMMENT BELOW
    # DHTI_LANGFUSE_ROUTE
    add_routes(
        app,
        dhti_elixir_chain.with_config(config),
        path="/langserve/dhti_elixir",
    )

except:
    # ! DO NOT REMOVE THE COMMENT BELOW
    # DHTI_NORMAL_ROUTE
    add_routes(app, dhti_elixir_chain, path="/langserve/dhti_elixir")
    x = True

# ! DO NOT REMOVE THE COMMENT BELOW
# DHTI_COMMON_ROUTE
add_invokes(app, path="/langserve/dhti_elixir")
add_services(app, path="/langserve/dhti_elixir")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
