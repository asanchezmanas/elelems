import pytest
from app.services.llamaindex_rag_service import LlamaIndexRAGService

@pytest.mark.asyncio
async def test_ingest_document():
    rag = LlamaIndexRAGService()
    
    result = await rag.ingest_document(
        file_path="tests/fixtures/sample.pdf",
        doc_id="test-doc-1",
        doc_type="policy"
    )
    
    assert result["status"] == "indexed"
    assert result["nodes_created"] > 0

@pytest.mark.asyncio
async def test_search_with_anchoring():
    rag = LlamaIndexRAGService()
    
    results = await rag.search(
        query="política de devoluciones",
        doc_types=["policy"],
        top_k=5
    )
    
    assert len(results) > 0
    assert all(r["doc_type"] == "policy" for r in results)

@pytest.mark.asyncio
async def test_query_with_prompt_anchoring():
    rag = LlamaIndexRAGService()
    
    context = await rag.query_with_prompt(
        query="cliente quiere devolver producto",
        prompt_name="support_response",
        top_k=3
    )
    
    assert "policy" in context.lower() or "devoluc" in context.lower()