# app/core/cache.py
import redis.asyncio as redis
import json

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def get_cached_generation(
        self,
        prompt_name: str,
        variables: dict
    ) -> Optional[str]:
        """Retorna generación cacheada si existe"""
        cache_key = self._build_key(prompt_name, variables)
        cached = await self.redis.get(cache_key)
        return cached.decode() if cached else None
    
    async def cache_generation(
        self,
        prompt_name: str,
        variables: dict,
        content: str,
        ttl: int = 3600  # 1 hora
    ):
        """Cachea generación"""
        cache_key = self._build_key(prompt_name, variables)
        await self.redis.setex(cache_key, ttl, content)
    
    def _build_key(self, prompt_name: str, variables: dict) -> str:
        # Hash determinístico de variables
        import hashlib
        vars_hash = hashlib.md5(
            json.dumps(variables, sort_keys=True).encode()
        ).hexdigest()
        return f"gen:{prompt_name}:{vars_hash}"