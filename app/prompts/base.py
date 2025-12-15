# app/prompts/base.py
from pydantic import BaseModel, Field
from typing import List, Optional


class PromptTemplate(BaseModel):
    """
    Template de prompt dinámico
    
    Atributos:
        name: Identificador único del prompt
        template: String del prompt con placeholders {variable}
        variables: Lista de variables requeridas
        system_message: Mensaje de sistema opcional
        temperature: Creatividad del LLM (0-1)
        max_tokens: Tokens máximos de respuesta
    """
    name: str
    template: str
    variables: List[str]
    system_message: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, ge=100, le=4000)
    
    def format(self, **kwargs) -> str:
        """
        Rellena el template con variables
        
        Raises:
            ValueError: Si faltan variables requeridas
        """
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(
                f"Falta la variable '{missing_var}' en el template '{self.name}'. "
                f"Variables requeridas: {self.variables}"
            )
    
    def validate_variables(self, **kwargs) -> bool:
        """Valida que estén todas las variables requeridas"""
        return all(var in kwargs for var in self.variables)
    
    def get_missing_variables(self, **kwargs) -> List[str]:
        """Retorna lista de variables faltantes"""
        return [var for var in self.variables if var not in kwargs]


