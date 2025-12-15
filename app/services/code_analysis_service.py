# app/services/code_analysis_service.py
"""
Servicio RAG especializado para análisis de código de repositorios
- Indexa estructura y código de repos
- Análisis inteligente con prompts especializados
- Genera planes de mejora con archivos afectados
"""

from typing import List, Dict, Optional, Any
import os
import tempfile
import asyncio
from pathlib import Path
import logging
from github import Github
from tqdm import tqdm

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.schema import TextNode, NodeRelationship
from llama_index.core.node_parser import CodeSplitter

from app.services.llamaindex_rag_service import LlamaIndexRAGService
from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubRepoExtractor:
    """
    Extractor mejorado de repositorios GitHub
    Optimizado para análisis de código
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var")
        self.github = Github(self.token)
        
        # Extensiones de código a procesar
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
            '.sql', '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.html',
            '.css', '.scss', '.vue', '.md', '.rst', '.txt'
        }
        
        # Archivos importantes a priorizar
        self.important_files = {
            'README.md', 'CONTRIBUTING.md', 'CHANGELOG.md',
            'requirements.txt', 'package.json', 'setup.py', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'Makefile', 'Dockerfile',
            '.env.example', 'docker-compose.yml'
        }
    
    async def extract_repo(
        self,
        repo_url: str,
        include_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Extrae estructura y contenido de un repositorio
        
        Args:
            repo_url: URL del repositorio GitHub
            include_tests: Si incluir archivos de tests
        
        Returns:
            Dict con README, estructura, archivos y metadata
        """
        repo_name = repo_url.split('/')[-1]
        logger.info(f"Extracting repository: {repo_name}")
        
        try:
            # Obtener repo
            repo = self.github.get_repo(
                repo_url.replace('https://github.com/', '')
            )
            
            # Extraer información
            readme = await self._get_readme(repo)
            structure = await self._get_structure(repo)
            files = await self._get_files(repo, include_tests)
            metadata = await self._get_metadata(repo)
            
            return {
                "repo_name": repo_name,
                "repo_url": repo_url,
                "readme": readme,
                "structure": structure,
                "files": files,
                "metadata": metadata,
                "total_files": len(files),
                "languages": metadata.get("languages", {})
            }
            
        except Exception as e:
            logger.error(f"Error extracting repo: {str(e)}")
            raise
    
    async def _get_readme(self, repo) -> str:
        """Obtiene README del repositorio"""
        try:
            readme = repo.get_contents("README.md")
            return readme.decoded_content.decode('utf-8')
        except:
            return "README not found."
    
    async def _get_structure(self, repo) -> List[str]:
        """
        Obtiene estructura de directorios del repo
        Útil para entender organización
        """
        structure = []
        dirs_to_visit = [("", repo.get_contents(""))]
        dirs_visited = set()
        
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            
            for content in contents:
                if content.type == "dir":
                    if content.path not in dirs_visited:
                        structure.append(f"{content.path}/")
                        dirs_to_visit.append(
                            (content.path, repo.get_contents(content.path))
                        )
                else:
                    structure.append(content.path)
        
        return sorted(structure)
    
    async def _get_files(
        self,
        repo,
        include_tests: bool
    ) -> List[Dict[str, str]]:
        """
        Obtiene contenido de archivos relevantes
        Filtra binarios y archivos no útiles
        """
        files = []
        dirs_to_visit = [("", repo.get_contents(""))]
        dirs_visited = set()
        
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            
            for content in tqdm(
                contents,
                desc=f"Processing {path or 'root'}",
                leave=False
            ):
                if content.type == "dir":
                    # Skip directorios comunes no útiles
                    if any(skip in content.path for skip in [
                        'node_modules', '__pycache__', '.git',
                        'venv', 'env', 'dist', 'build', '.cache'
                    ]):
                        continue
                    
                    # Skip tests si no se incluyen
                    if not include_tests and 'test' in content.path.lower():
                        continue
                    
                    if content.path not in dirs_visited:
                        dirs_to_visit.append(
                            (content.path, repo.get_contents(content.path))
                        )
                else:
                    # Procesar archivo
                    file_info = await self._process_file(content)
                    if file_info:
                        files.append(file_info)
        
        logger.info(f"Extracted {len(files)} files")
        return files
    
    async def _process_file(self, content) -> Optional[Dict[str, str]]:
        """
        Procesa un archivo individual
        Extrae contenido si es relevante
        """
        filename = content.name
        filepath = content.path
        
        # Determinar si es archivo relevante
        ext = Path(filename).suffix.lower()
        is_important = filename in self.important_files
        is_code = ext in self.code_extensions
        
        if not (is_important or is_code):
            return None
        
        # Extraer contenido
        try:
            if content.encoding is None or content.encoding == 'none':
                return None
            
            file_content = content.decoded_content.decode('utf-8')
            
            # Determinar tipo de archivo
            file_type = self._determine_file_type(ext, filename)
            
            return {
                "path": filepath,
                "filename": filename,
                "content": file_content,
                "size": content.size,
                "type": file_type,
                "language": self._get_language(ext),
                "is_important": is_important
            }
            
        except UnicodeDecodeError:
            # Intentar con latin-1
            try:
                file_content = content.decoded_content.decode('latin-1')
                return {
                    "path": filepath,
                    "filename": filename,
                    "content": file_content,
                    "size": content.size,
                    "type": "text",
                    "language": "unknown",
                    "is_important": is_important,
                    "encoding": "latin-1"
                }
            except:
                return None
        except Exception as e:
            logger.warning(f"Could not process {filepath}: {str(e)}")
            return None
    
    def _determine_file_type(self, ext: str, filename: str) -> str:
        """Clasifica tipo de archivo"""
        config_files = {
            'package.json', 'requirements.txt', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'setup.py'
        }
        
        if filename in config_files:
            return "config"
        elif filename.startswith('README'):
            return "documentation"
        elif ext in {'.md', '.rst', '.txt'}:
            return "documentation"
        elif ext in {'.yml', '.yaml', '.json', '.xml', '.toml'}:
            return "config"
        elif ext in {'.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs'}:
            return "code"
        elif ext in {'.sql'}:
            return "database"
        elif ext in {'.sh', '.bash'}:
            return "script"
        else:
            return "other"
    
    def _get_language(self, ext: str) -> str:
        """Determina lenguaje de programación"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.sql': 'sql',
            '.sh': 'bash',
        }
        return lang_map.get(ext, 'unknown')
    
    async def _get_metadata(self, repo) -> Dict[str, Any]:
        """Extrae metadata del repositorio"""
        try:
            return {
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "languages": repo.get_languages(),
                "topics": repo.get_topics(),
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "license": repo.license.name if repo.license else None,
                "size": repo.size,
                "open_issues": repo.open_issues_count
            }
        except Exception as e:
            logger.warning(f"Could not get metadata: {str(e)}")
            return {}


class CodeAnalysisRAGService:
    """
    Servicio RAG especializado para análisis de código
    Integra extracción de repos con análisis inteligente
    """
    
    def __init__(self, rag_service: LlamaIndexRAGService):
        self.rag = rag_service
        self.extractor = GitHubRepoExtractor()
        
        # Code splitter especializado
        self.code_splitter = CodeSplitter(
            language="python",  # Detectar automáticamente
            chunk_lines=40,
            chunk_lines_overlap=15,
            max_chars=1500
        )
    
    async def index_repository(
        self,
        repo_url: str,
        include_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Indexa un repositorio completo para análisis
        
        Args:
            repo_url: URL del repositorio
            include_tests: Si incluir archivos de tests
        
        Returns:
            Stats de indexación
        """
        logger.info(f"Starting repository indexation: {repo_url}")
        
        # 1. Extraer repositorio
        repo_data = await self.extractor.extract_repo(repo_url, include_tests)
        
        # 2. Crear documentos para indexar
        documents = await self._create_documents(repo_data)
        
        # 3. Indexar con RAG
        doc_id = f"repo_{repo_data['repo_name']}"
        
        # Guardar temporalmente para procesar
        temp_path = await self._save_to_temp(repo_data)
        
        result = await self.rag.ingest_document(
            file_path=temp_path,
            doc_id=doc_id,
            doc_type="code_repository",
            metadata={
                "repo_url": repo_url,
                "repo_name": repo_data["repo_name"],
                "languages": repo_data["metadata"].get("languages", {}),
                "total_files": repo_data["total_files"]
            }
        )
        
        logger.info(f"Repository indexed: {repo_data['repo_name']}")
        
        return {
            **result,
            "repo_data": repo_data
        }
    
    async def _create_documents(
        self,
        repo_data: Dict[str, Any]
    ) -> List[Document]:
        """
        Convierte datos del repo en documentos para RAG
        Estructura jerárquica para mejor recuperación
        """
        documents = []
        
        # 1. README como documento principal
        if repo_data["readme"] != "README not found.":
            documents.append(Document(
                text=repo_data["readme"],
                metadata={
                    "type": "readme",
                    "repo_name": repo_data["repo_name"],
                    "importance": "high"
                }
            ))
        
        # 2. Estructura del repositorio
        structure_text = "Repository Structure:\n" + "\n".join(
            repo_data["structure"][:100]  # Primeros 100 paths
        )
        documents.append(Document(
            text=structure_text,
            metadata={
                "type": "structure",
                "repo_name": repo_data["repo_name"]
            }
        ))
        
        # 3. Archivos de código (agrupados por tipo)
        files_by_type = {}
        for file_info in repo_data["files"]:
            file_type = file_info["type"]
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_info)
        
        # Crear documentos por archivo
        for file_info in repo_data["files"]:
            # Contenido del archivo
            content = f"File: {file_info['path']}\n"
            content += f"Language: {file_info['language']}\n"
            content += f"Type: {file_info['type']}\n\n"
            content += file_info['content']
            
            documents.append(Document(
                text=content,
                metadata={
                    "type": "code_file",
                    "file_path": file_info["path"],
                    "language": file_info["language"],
                    "file_type": file_info["type"],
                    "is_important": file_info["is_important"],
                    "repo_name": repo_data["repo_name"]
                }
            ))
        
        logger.info(f"Created {len(documents)} documents from repository")
        return documents
    
    async def _save_to_temp(self, repo_data: Dict[str, Any]) -> str:
        """Guarda datos del repo en archivo temporal para procesamiento"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"{repo_data['repo_name']}_repo.txt")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            # README
            f.write("=" * 80 + "\n")
            f.write("README\n")
            f.write("=" * 80 + "\n\n")
            f.write(repo_data["readme"])
            f.write("\n\n")
            
            # Estructura
            f.write("=" * 80 + "\n")
            f.write("REPOSITORY STRUCTURE\n")
            f.write("=" * 80 + "\n\n")
            f.write("\n".join(repo_data["structure"]))
            f.write("\n\n")
            
            # Archivos
            f.write("=" * 80 + "\n")
            f.write("FILES\n")
            f.write("=" * 80 + "\n\n")
            
            for file_info in repo_data["files"]:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"File: {file_info['path']}\n")
                f.write(f"Language: {file_info['language']}\n")
                f.write(f"Type: {file_info['type']}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(file_info['content'])
                f.write("\n\n")
        
        return temp_file
    
    async def analyze_code_quality(
        self,
        repo_name: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analiza calidad del código usando RAG
        
        Args:
            repo_name: Nombre del repositorio
            focus_areas: Áreas específicas (security, performance, etc.)
        
        Returns:
            Análisis detallado con recomendaciones
        """
        query = f"""
        Analiza la calidad del código del repositorio {repo_name}.
        
        Enfócate en:
        - Patrones de diseño utilizados
        - Organización del código
        - Buenas prácticas
        - Áreas de mejora
        - Deuda técnica potencial
        """
        
        if focus_areas:
            query += f"\n\nPresta especial atención a: {', '.join(focus_areas)}"
        
        # Buscar contexto relevante
        context = await self.rag.query_with_prompt(
            query=query,
            prompt_name="code_analysis",
            top_k=10
        )
        
        # Generar análisis (aquí iría la llamada al LLM)
        # Por ahora, retornar contexto recuperado
        
        return {
            "repo_name": repo_name,
            "analysis_type": "code_quality",
            "context": context,
            "focus_areas": focus_areas or []
        }
    
    async def suggest_improvements(
        self,
        repo_name: str,
        improvement_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Genera sugerencias de mejora específicas
        
        Args:
            repo_name: Nombre del repositorio
            improvement_type: Tipo (performance, security, architecture)
        
        Returns:
            Plan de mejora con archivos afectados
        """
        query = f"""
        Para el repositorio {repo_name}, identifica oportunidades de mejora
        en {improvement_type}.
        
        Para cada mejora:
        1. Describe el problema actual
        2. Propón la solución
        3. Lista los archivos que necesitan modificarse
        4. Estima el impacto (bajo/medio/alto)
        5. Prioridad (P0/P1/P2/P3)
        """
        
        # Recuperar contexto relevante
        results = await self.rag.search(
            query=query,
            doc_types=["code_repository"],
            top_k=15
        )
        
        # Agrupar por archivos
        files_mentioned = set()
        for result in results:
            if "file_path" in result["metadata"]:
                files_mentioned.add(result["metadata"]["file_path"])
        
        return {
            "repo_name": repo_name,
            "improvement_type": improvement_type,
            "files_to_modify": list(files_mentioned),
            "context": results,
            "total_suggestions": len(results)
        }
    
    async def generate_migration_plan(
        self,
        repo_name: str,
        target: str,
        current: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera plan de migración (ej: Python 2 → 3, Angular → React)
        
        Args:
            repo_name: Repositorio a migrar
            target: Tecnología objetivo
            current: Tecnología actual (se detecta si es None)
        
        Returns:
            Plan de migración detallado
        """
        query = f"""
        Analiza el repositorio {repo_name} para migrar a {target}.
        
        Identifica:
        1. Dependencias que deben actualizarse
        2. APIs deprecadas en uso
        3. Cambios de sintaxis necesarios
        4. Configuraciones a modificar
        5. Tests que deben actualizarse
        
        Lista todos los archivos afectados por orden de prioridad.
        """
        
        if current:
            query += f"\n\nMigración: {current} → {target}"
        
        results = await self.rag.search(
            query=query,
            doc_types=["code_repository"],
            top_k=20
        )
        
        # Analizar archivos por tipo
        files_by_type = {}
        for result in results:
            file_type = result["metadata"].get("file_type", "other")
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(result)
        
        return {
            "repo_name": repo_name,
            "migration": f"{current or 'auto-detected'} → {target}",
            "files_by_type": {
                k: [r["metadata"].get("file_path") for r in v]
                for k, v in files_by_type.items()
            },
            "total_files_affected": len(results),
            "context": results[:10]  # Top 10 más relevantes
        }
    
    async def find_bugs_patterns(
        self,
        repo_name: str,
        bug_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Busca patrones de bugs comunes en el código
        
        Args:
            repo_name: Repositorio a analizar
            bug_categories: Categorías (sql_injection, xss, race_conditions)
        
        Returns:
            Potenciales bugs encontrados
        """
        categories = bug_categories or [
            "sql_injection",
            "xss",
            "hardcoded_credentials",
            "insecure_random",
            "resource_leaks",
            "race_conditions"
        ]
        
        query = f"""
        Analiza el código del repositorio {repo_name} buscando
        patrones de bugs comunes en las siguientes categorías:
        {', '.join(categories)}
        
        Para cada patrón encontrado:
        1. Archivo y línea aproximada
        2. Descripción del problema
        3. Severidad (critical/high/medium/low)
        4. Solución recomendada
        """
        
        results = await self.rag.search(
            query=query,
            doc_types=["code_repository"],
            top_k=15,
            similarity_threshold=0.6  # Más permisivo para bugs
        )
        
        return {
            "repo_name": repo_name,
            "bug_categories": categories,
            "potential_issues": results,
            "total_found": len(results)
        }