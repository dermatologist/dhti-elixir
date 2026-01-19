# dhti-elixir-srag

A simple RAG dhti-elixir package that connects to a Redis vector store (created by `upload_file` package) to answer user queries.

## Configuration

Set `rag_k` in `bootstrap.py` to control number of retrieved documents.
Ensure `REDIS_URL` is set if not using localhost.