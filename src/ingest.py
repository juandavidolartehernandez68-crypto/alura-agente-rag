"""
Pipeline de ingesta: extrae -> divide en chunks -> genera embeddings -> indexa en Chroma.

Uso:
    python src/ingest.py

Requiere GEMINI_API_KEY en el archivo .env (ver .env.example).
Usa el modelo gemini-embedding-001 (gratis vía Google AI Studio) para generar los vectores,
y los guarda en una base de datos vectorial Chroma persistida en disk (data/chroma/).
"""

import os
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

from extract import extract_text
from chunking import chunk_document

load_dotenv()

DOCS_DIR = Path(__file__).parent.parent / "docs"
CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma"
COLLECTION_NAME = "tiendaluna_docs"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768  # reducimos de 3072 (default) a 768 para que la búsqueda sea más liviana

SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".md")


def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY. Copia .env.example a .env y agrega tu key "
            "(consíguela gratis en https://aistudio.google.com/apikey)."
        )
    return genai.Client(api_key=api_key)


def embed_texts(client: genai.Client, texts: list[str], task_type: str) -> list[list[float]]:
    """
    Genera embeddings para una lista de textos.
    task_type: "RETRIEVAL_DOCUMENT" al indexar chunks, "RETRIEVAL_QUERY" al buscar.
    Se hace en lotes pequeños con reintento simple, porque el free tier tiene rate limits.
    """
    all_embeddings = []
    batch_size = 10
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for attempt in range(3):
            try:
                result = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=EMBEDDING_DIM,
                    ),
                )
                all_embeddings.extend([e.values for e in result.embeddings])
                break
            except Exception as e:
                wait = 5 * (attempt + 1)
                print(f"  ⚠️  Error en batch {i}: {e}. Reintentando en {wait}s...")
                time.sleep(wait)
        else:
            raise RuntimeError(f"No se pudo generar embeddings para el batch en índice {i}")
        # Pequeña pausa entre batches para respetar el rate limit del free tier
        time.sleep(1)
    return all_embeddings


def get_chroma_client() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def build_index():
    """Reconstruye la colección completa desde cero, leyendo todo lo que hay en docs/."""
    print("📂 Cargando documentos desde", DOCS_DIR)
    client = get_gemini_client()

    all_chunks = []
    for filepath in sorted(DOCS_DIR.glob("*")):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = extract_text(str(filepath))
        chunks = chunk_document(str(filepath), text)
        all_chunks.extend(chunks)
        print(f"  ✓ {filepath.name}: {len(chunks)} chunks")

    if not all_chunks:
        print("⚠️  No se encontraron documentos soportados en docs/.")
        return

    print(f"\n🧠 Generando embeddings para {len(all_chunks)} chunks con {EMBEDDING_MODEL}...")
    texts = [c.text for c in all_chunks]
    embeddings = embed_texts(client, texts, task_type="RETRIEVAL_DOCUMENT")

    print("💾 Guardando en ChromaDB en", CHROMA_PATH)
    chroma_client = get_chroma_client()

    # Recrea la colección desde cero cada vez que se corre el build completo (evita duplicados)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[c.id for c in all_chunks],
        embeddings=embeddings,
        documents=[c.text for c in all_chunks],
        metadatas=[c.metadata for c in all_chunks],
    )

    print(f"\n✅ Listo. {len(all_chunks)} chunks indexados en la colección '{COLLECTION_NAME}'.")


def ingest_single_document(filepath: str, category: str = "Sin categoría") -> int:
    """
    Indexa UN solo documento nuevo (subido desde la interfaz, por ejemplo) sin tocar
    los que ya estaban indexados. Usado por el uploader de la app de Streamlit.

    Devuelve la cantidad de chunks agregados.
    """
    from chunking import DOCUMENT_CATEGORIES

    filename = Path(filepath).name
    # Registra la categoría para este archivo (chunk_document la consulta por nombre de archivo)
    DOCUMENT_CATEGORIES[filename] = category

    text = extract_text(filepath)
    chunks = chunk_document(filepath, text)
    if not chunks:
        return 0

    client = get_gemini_client()
    texts = [c.text for c in chunks]
    embeddings = embed_texts(client, texts, task_type="RETRIEVAL_DOCUMENT")

    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    # upsert evita duplicados si el mismo archivo se vuelve a subir (mismos ids)
    collection.upsert(
        ids=[c.id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[c.metadata for c in chunks],
    )

    return len(chunks)


if __name__ == "__main__":
    build_index()
