@pytest.mark.asyncio
async def test_full_rag_pipeline():
    """Test completo: upload → index → search → generate"""
    
    # 1. Upload documento
    with open("tests/fixtures/brand_guide.pdf", "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": f},
            data={"doc_type": "brand_guide"}
        )
    
    assert response.status_code == 200
    doc_id = response.json()["document_id"]
    
    # 2. Esperar indexación (o usar webhook)
    await asyncio.sleep(5)
    
    # 3. Generar con RAG
    response = await client.post(
        "/api/v1/generation/generate",
        json={
            "prompt_name": "product_description",
            "variables": {
                "product_name": "Zapatillas Pro",
                "features": "Cómodas, ligeras",
                "price": "89.99"
            },
            "use_rag": True
        }
    )
    
    assert response.status_code == 200
    assert "brand_guide.pdf" in response.json()["sources"]