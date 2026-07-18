"""
Módulo de chunking (división en fragmentos).

Estrategia usada: división por estructura lógica (por sección, detectando encabezados
tipo "1. Título de sección") con un fallback a división por tamaño fijo con overlap
para secciones muy largas. Esto preserva mejor el sentido completo de cada fragmento,
como recomienda la tarjeta "2 - Proceso y extracción de contenido".

Cada chunk recibe metadatos: categoría del documento, nombre del archivo, y el índice
del fragmento dentro del documento — necesarios después para filtrar y citar la fuente.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

CHUNK_SIZE = 800       # caracteres objetivo por chunk
CHUNK_OVERLAP = 120    # overlap entre chunks consecutivos, para no cortar una idea a la mitad

# Mapea nombre de archivo -> categoría de negocio (metadato clave para filtrar búsquedas)
DOCUMENT_CATEGORIES = {
    "politica_privacidad.md": "Legal y Compliance",
    "terminos_condiciones.md": "Legal y Compliance",
    "politica_reembolsos.docx": "Operacional",
    "guia_envios.docx": "Operacional",
    "faq.pdf": "Marketing y Comercial",
}


@dataclass
class Chunk:
    text: str
    source_file: str
    category: str
    chunk_index: int
    section_title: str = ""

    @property
    def id(self) -> str:
        # ID determinístico: mismo archivo + mismo índice = mismo id (útil para re-indexar sin duplicar)
        clean_name = Path(self.source_file).stem
        return f"{clean_name}_{self.chunk_index}"

    @property
    def metadata(self) -> dict:
        return {
            "source_file": self.source_file,
            "category": self.category,
            "chunk_index": self.chunk_index,
            "section_title": self.section_title,
        }


def _split_by_sections(text: str) -> list[tuple[str, str]]:
    """
    Divide el texto en secciones usando encabezados numerados ("1. Algo", "2. Otro...").
    Devuelve lista de (titulo_seccion, contenido_seccion). Si no encuentra encabezados,
    devuelve todo el texto como una sola sección.
    """
    pattern = re.compile(r"^(\d{1,2}\.\s+.{3,80})$", re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        return [("", text)]

    sections = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections.append((title, content))
    return sections


def _split_fixed_size(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Fallback: divide texto largo por tamaño fijo con overlap, cortando en el espacio más cercano."""
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        if end < len(text):
            # No cortar una palabra a la mitad: retrocede hasta el último espacio
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]


def chunk_document(filepath: str, text: str) -> list[Chunk]:
    """
    Convierte el texto extraído de un documento en una lista de Chunks con metadatos.
    Combina división por secciones (preferida) con división por tamaño para secciones largas.
    """
    filename = Path(filepath).name
    category = DOCUMENT_CATEGORIES.get(filename, "Sin categoría")

    sections = _split_by_sections(text)
    chunks: list[Chunk] = []
    idx = 0

    for section_title, section_content in sections:
        if not section_content.strip():
            continue
        # Si la sección es corta, es un chunk único; si es larga, se subdivide
        sub_pieces = _split_fixed_size(section_content)
        for piece in sub_pieces:
            # Anteponemos el título de sección al chunk para que el embedding capture el contexto
            chunk_text = f"{section_title}\n{piece}" if section_title else piece
            chunks.append(Chunk(
                text=chunk_text,
                source_file=filename,
                category=category,
                chunk_index=idx,
                section_title=section_title,
            ))
            idx += 1

    return chunks


if __name__ == "__main__":
    from extract import extract_text

    docs_dir = Path(__file__).parent.parent / "docs"
    total_chunks = 0
    for filepath in sorted(docs_dir.glob("*")):
        if filepath.suffix.lower() not in (".pdf", ".docx", ".md"):
            continue
        text = extract_text(str(filepath))
        chunks = chunk_document(str(filepath), text)
        total_chunks += len(chunks)
        print(f"\n{filepath.name} -> {len(chunks)} chunks")
        for c in chunks[:2]:
            print(f"  [{c.id}] ({c.category}) {c.text[:100]}...")
    print(f"\nTotal de chunks generados: {total_chunks}")
