"""Phase 14 RAG: chunking -> embeddings -> hybrid retrieval -> cited context.

One retrieval code path: the pipeline's fixed retrieval step and the agent's
search_documents tool both call into this package. Mirrors the llm_client
rule — no embedding call happens outside embeddings_client.
"""
