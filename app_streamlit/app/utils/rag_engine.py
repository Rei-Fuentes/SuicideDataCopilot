"""
Motor RAG para CUIDAR IA
Funciones de retrieval y generación de respuestas
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader

from .config import (
    PROJECT_ROOT, 
    CHROMA_DIR, 
    RAG_CONFIG, 
    CHUNK_CONFIG,
    SYSTEM_PROMPT
)

# Cargar variables de entorno
load_dotenv(PROJECT_ROOT / ".env")


class RAGEngine:
    """
    Motor de Retrieval-Augmented Generation para CUIDAR IA.
    """
    
    def __init__(self):
        """Inicializa el motor RAG con el vector store de producción."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embeddings = OpenAIEmbeddings(
            model=RAG_CONFIG["embedding_model"],
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Cargar vector store de producción
        self.vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self.embeddings,
            collection_name=RAG_CONFIG["collection_name"]
        )
        
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": RAG_CONFIG["k_results"]}
        )
        
        # Almacenamiento temporal para documentos locales
        self.local_docs_chunks = []
        
    def add_local_document(self, pdf_file, filename):
        """
        Procesa y agrega un documento local al contexto de búsqueda.
        
        Parámetros:
        - pdf_file: Archivo PDF subido
        - filename: Nombre del archivo
        
        Retorna:
        - Diccionario con información del procesamiento
        """
        try:
            # Extraer texto del PDF
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += f"\n{text}"
            
            if not full_text.strip():
                return {
                    "success": False,
                    "message": "No se pudo extraer texto del documento"
                }
            
            # Crear chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_CONFIG["chunk_size"],
                chunk_overlap=CHUNK_CONFIG["chunk_overlap"],
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            chunks = text_splitter.split_text(full_text)
            
            # Crear documentos con metadata
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "category": "local",
                        "category_name": "Documento Local",
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "is_local": True
                    }
                )
                self.local_docs_chunks.append(doc)
            
            return {
                "success": True,
                "message": f"Documento procesado: {len(chunks)} fragmentos creados",
                "chunks": len(chunks),
                "pages": len(reader.pages)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al procesar documento: {str(e)}"
            }
    
    def clear_local_documents(self):
        """Limpia los documentos locales del contexto."""
        self.local_docs_chunks = []
        return {"success": True, "message": "Documentos locales eliminados"}
    
    def get_local_docs_count(self):
        """Retorna el número de chunks de documentos locales."""
        return len(self.local_docs_chunks)
    
    def generate_response(self, query, include_local=True):
        """
        Genera una respuesta usando RAG.
        
        Parámetros:
        - query: Pregunta del usuario
        - include_local: Si incluir documentos locales en la búsqueda
        
        Retorna:
        - Diccionario con respuesta, fuentes y metadatos
        """
        # Recuperar chunks del vector store principal
        retrieved_docs = self.retriever.invoke(query)
        
        # Agregar documentos locales si existen y están habilitados
        if include_local and self.local_docs_chunks:
            local_relevant = self._search_local_docs(query)
            retrieved_docs = retrieved_docs + local_relevant
        
        if not retrieved_docs:
            return {
                "respuesta": "No encontré información relevante en la base de conocimiento para responder esta consulta.",
                "fuentes": [],
                "chunks_utilizados": 0,
                "incluye_docs_locales": False
            }
        
        # Construir contexto
        context_parts = []
        sources = []
        has_local = False
        
        for i, doc in enumerate(retrieved_docs, 1):
            source_name = doc.metadata.get('source', 'Fuente desconocida')
            is_local = doc.metadata.get('is_local', False)
            
            if is_local:
                has_local = True
                context_parts.append(f"[Documento Local {i} - {source_name}]:\n{doc.page_content}")
            else:
                context_parts.append(f"[Documento {i} - {source_name}]:\n{doc.page_content}")
            
            if source_name not in sources:
                sources.append(source_name)
        
        context = "\n\n".join(context_parts)
        
        # Construir prompt
        user_prompt = f"""Contexto (documentos recuperados de la base de conocimiento):

{context}

---

Pregunta del usuario:
{query}

Por favor, responde basándote en el contexto proporcionado. Si consideras que sería útil contar con datos o investigación local adicional para complementar la respuesta, menciónalo."""
        
        # Generar respuesta
        try:
            response = self.client.chat.completions.create(
                model=RAG_CONFIG["llm_model"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=RAG_CONFIG["temperature"],
                max_tokens=RAG_CONFIG["max_tokens"]
            )
            
            return {
                "respuesta": response.choices[0].message.content,
                "fuentes": sources,
                "chunks_utilizados": len(retrieved_docs),
                "tokens_utilizados": response.usage.total_tokens,
                "incluye_docs_locales": has_local
            }
            
        except Exception as e:
            return {
                "respuesta": f"Error al generar respuesta: {str(e)}",
                "fuentes": sources,
                "chunks_utilizados": len(retrieved_docs),
                "incluye_docs_locales": has_local
            }
    
    def _search_local_docs(self, query, top_k=2):
        """
        Búsqueda simple en documentos locales.
        Retorna los chunks más relevantes basándose en coincidencia de palabras clave.
        """
        if not self.local_docs_chunks:
            return []
        
        # Búsqueda simple por palabras clave
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in self.local_docs_chunks:
            content_words = set(doc.page_content.lower().split())
            score = len(query_words.intersection(content_words))
            scored_docs.append((score, doc))
        
        # Ordenar por score y retornar top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k] if score > 0]


# Instancia global del motor RAG
_rag_engine = None

def get_rag_engine():
    """
    Obtiene la instancia del motor RAG (singleton).
    """
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
