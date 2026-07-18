"""
Módulo de consulta (retrieval + generación).

Dada una pregunta del colaborador:
1. Genera el embedding de la pregunta (RETRIEVAL_QUERY)
2. Busca los chunks más similares en Chroma
3. Arma un prompt con esos chunks como contexto
4. Le pide a Gemini que responda SOLO con base en ese contexto, citando la fuente
"""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma"
COLLECTION_NAME = "tiendaluna_docs"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768
GENERATION_MODEL = "gemini-2.5-flash"
TOP_K = 4  # cuántos chunks recuperar por pregunta

SYSTEM_PROMPT = """Eres el asistente virtual interno de TiendaLuna. Respondes preguntas de \
colaboradores basándote ÚNICAMENTE en los fragmentos de documentos internos que se te \
proporcionan como contexto.

Reglas:
- Si la respuesta está en el contexto, respóndela de forma clara y concisa.
- Si el contexto no contiene información suficiente, dilo explícitamente: no inventes datos.
- Al final de tu respuesta, indica de qué documento(s) proviene la información, \
usando el campo "source_file" de los fragmentos.
- Responde siempre en español.
"""


def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")
    return genai.Client(api_key=api_key)


def get_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        return chroma_client.get_collection(COLLECTION_NAME)
    except Exception:
        raise RuntimeError(
            "No se encontró la colección indexada. Corre primero: python src/ingest.py"
        )


def retrieve(client: genai.Client, collection, question: str, top_k: int = TOP_K, category: str | None = None):
    """Busca los chunks más relevantes para la pregunta. Filtro opcional por categoría."""
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[question],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    query_embedding = result.embeddings[0].values

    where_filter = {"category": category} if category else None
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )
    return results


def build_context(results) -> str:
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    parts = []
    for doc, meta in zip(docs, metas):
        parts.append(f"[Fuente: {meta['source_file']} | Categoría: {meta['category']}]\n{doc}")
    return "\n\n---\n\n".join(parts)


def answer_question(question: str, category: str | None = None) -> dict:
    """Punto de entrada principal: recibe una pregunta, devuelve respuesta + fuentes usadas."""
    client = get_gemini_client()
    collection = get_collection()

    results = retrieve(client, collection, question, category=category)
    context = build_context(results)

    prompt = f"""Contexto (fragmentos de documentos internos de TiendaLuna):

{context}

Pregunta del colaborador: {question}

Responde siguiendo las reglas del sistema."""

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )

    sources = sorted({meta["source_file"] for meta in results["metadatas"][0]})
    return {
        "answer": response.text,
        "sources": sources,
        "retrieved_chunks": results["documents"][0],
    }


if __name__ == "__main__":
    test_questions = [
        "¿Cuánto tiempo tengo para devolver un producto?",
        "¿Hacen envíos a otros países?",
        "¿Qué pasa con mis datos personales si elimino mi cuenta?",
    ]
    for q in test_questions:
        print(f"\n{'=' * 60}\nP: {q}\n{'=' * 60}")
        result = answer_question(q)
        print(f"R: {result['answer']}")
        print(f"Fuentes: {result['sources']}")
