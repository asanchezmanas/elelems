# app/providers/llm/ollama.py
import httpx

class OllamaProvider:
    def __init__(self):
        # URL de TU servidor Ollama (no pública, por VPN)
        self.base_url = "http://tu-servidor-privado:11434"
        # O por Tailscale: http://100.x.x.x:11434
    
    async def generate(self, prompt: str, context: list) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "llama3.1:8b",  # Modelo descargado
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"]
```

## 🏗️ Arquitectura 100% Privada
```
┌─────────────────┐
│   Usuario       │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  FastAPI        │  ← Render (solo lógica)
│  (Render)       │
└────────┬────────┘
         │ VPN/Tailscale
         ▼
┌─────────────────┐
│  TU SERVIDOR    │  ← Aquí está TODO privado
│  ┌───────────┐  │
│  │  Ollama   │  │  Modelos Llama/Mistral
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Embeddings│  │  sentence-transformers
│  └───────────┘  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Supabase      │  ← Solo metadatos + vectores
│   (pgvector)    │     (no texto completo)
└─────────────────┘