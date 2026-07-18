# Agente Corporativo de IA — TiendaLuna (Challenge Alura Agente)

Agente de inteligencia artificial capaz de responder preguntas de colaboradores con base en
documentos internos de la empresa (RAG — *Retrieval-Augmented Generation*).

> 🚧 Proyecto en desarrollo — Challenge Alura Latam / ONE.

## Descripción

Este proyecto implementa un agente conversacional que responde preguntas sobre políticas y
procesos internos de **TiendaLuna**, una empresa ficticia de e-commerce, a partir de documentos
en distintos formatos (Markdown, Word, PDF).

## Funcionalidades

- [x] Ingesta de documentos en múltiples formatos (Markdown, Word, PDF)
- [x] Extracción y limpieza de texto por tipo de documento
- [x] Chunking por estructura lógica, con metadatos (categoría, archivo, sección)
- [x] Generación de embeddings e indexación vectorial (ChromaDB + Gemini Embeddings)
- [x] Búsqueda semántica + generación de respuestas con citación de fuente
- [x] Interfaz conversacional (Streamlit), con opción de subir nuevos documentos
- [ ] Despliegue en la nube (Streamlit Community Cloud)

## Documentos incluidos (datos ficticios)

| Documento | Categoría | Formato |
|---|---|---|
| Política de Privacidad | Legal y Compliance | Markdown |
| Términos y Condiciones | Legal y Compliance | Markdown |
| Política de Reembolsos y Devoluciones | Operacional | Word (.docx) |
| Guía de Envíos y Entregas | Operacional | Word (.docx) |
| Preguntas Frecuentes (FAQ) | Marketing y Comercial | PDF |

## Stack técnico

- **LLM / Embeddings:** Google Gemini API (`gemini-embedding-001` + `gemini-2.5-flash`) — free tier, sin tarjeta de crédito
- **Base de datos vectorial:** ChromaDB (persistida localmente en `data/chroma/`)
- **Interfaz:** Streamlit, con función de subir nuevos documentos desde la propia app
- **Despliegue:** Streamlit Community Cloud

## Cómo ejecutar

```bash
python -m venv venv
source venv/bin/activate          # En Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edita .env y agrega tu GEMINI_API_KEY (gratis en https://aistudio.google.com/apikey)

# 1. Indexa los documentos de docs/ en la base vectorial
python src/ingest.py

# 2. Prueba el pipeline de preguntas y respuestas por consola
python src/query.py
```

## Pipeline RAG — cómo funciona

```
docs/*.{pdf,docx,md}
      │
      ▼
src/extract.py     → extrae texto plano por formato (pypdf, python-docx, markdown+bs4)
      │
      ▼
src/chunking.py    → divide por secciones lógicas + metadatos (categoría, archivo, sección)
      │
      ▼
src/ingest.py       → genera embeddings (gemini-embedding-001) e indexa en ChromaDB
      │
      ▼
src/query.py         → busca chunks relevantes + genera respuesta citando la fuente (gemini-2.5-flash)
```

## Estructura del proyecto

```
alura-agente-rag/
├── docs/               # Documentos fuente (los datos que el agente consulta)
├── src/
│   ├── extract.py       # Extracción de texto por formato
│   ├── chunking.py       # División en fragmentos + metadatos
│   ├── ingest.py          # Embeddings + indexación vectorial
│   └── query.py            # Búsqueda semántica + generación de respuesta
├── data/chroma/            # Base de datos vectorial persistida (no se sube a git)
├── requirements.txt
└── .env.example
```

## Captura / Video del agente en ejecución
<img width="1365" height="647" alt="image" src="https://github.com/user-attachments/assets/122d6c42-53ab-4925-a365-95b517eaf0be" />

*(Se agregará aquí una vez desplegado )*

## Autor

Juan David Olarte Hernández — Challenge Alura Agente (ONE)
