from dhti_elixir_base.cds_hook.routes import add_invokes, add_services
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables.config import RunnableConfig
from langserve import add_routes
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP(name="dhti-mcp-server")
# ! DO NOT REMOVE THE COMMENT BELOW
# DHTI_CLI_IMPORT
from bootstrap import bootstrap as dhti_elixir_bootstrap
from pydantic import BaseModel, ConfigDict

dhti_elixir_bootstrap()
import os

# add src to sys path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from chain import DhtiChain as dhti_elixir_chain_class

dhti_elixir_chain = dhti_elixir_chain_class().get_chain_as_langchain_tool()
dhti_elixir_mcp_tool = dhti_elixir_chain_class().get_chain_as_mcp_tool
# 1. Define your MCP server
mcp_server.add_tool(dhti_elixir_mcp_tool)  # type: ignore

import uvicorn

# Comes after elixir bootstraps, so can override elixir configurations
from bootstrap import bootstrap

bootstrap()


app = FastAPI(title="dhti-elixir-server")
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
    from langfuse import Langfuse  # type: ignore
    from langfuse.callback import CallbackHandler  # type: ignore

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
    uvicorn.run(app, host="0.0.0.0", port=8002)
