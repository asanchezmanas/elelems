# app/services/finetuning_service.py
class FineTuningService:
    """
    Fine-tune de modelos en base a feedback de usuarios
    
    - Recolecta generaciones + feedback (👍/👎)
    - Crea dataset JSONL
    - Lanza fine-tuning job en OpenAI/Groq
    - Swapea modelo en producción
    """
    
    async def collect_training_data(
        self,
        user_id: str,
        min_samples: int = 100
    ) -> str:
        """Exporta generaciones aprobadas como JSONL"""
        
    async def create_finetuning_job(
        self,
        dataset_path: str,
        model: str = "gpt-4o-mini"
    ) -> str:
        """Lanza job de fine-tuning"""