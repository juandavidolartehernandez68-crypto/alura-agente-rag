# Agente Corporativo de IA — TiendaLuna (Challenge Alura Agente)

Agente de inteligencia artificial capaz de responder preguntas de colaboradores con base en
documentos internos de la empresa (RAG — *Retrieval-Augmented Generation*).

> 🚧 Proyecto en desarrollo — Challenge Alura Latam / ONE.

## Descripción

Este proyecto implementa un agente conversacional que responde preguntas sobre políticas y
procesos internos de **TiendaLuna**, una empresa ficticia de e-commerce, a partir de documentos
en distintos formatos (Markdown, Word, PDF).

## Funcionalidades

- [ ] Ingesta de documentos en múltiples formatos (Markdown, Word, PDF)
- [ ] Extracción y limpieza de texto por tipo de documento
- [ ] Chunking con metadatos (categoría, archivo, fecha)
- [ ] Generación de embeddings e indexación vectorial (Chroma)
- [ ] Búsqueda semántica + generación de respuestas con citación de fuente
- [ ] Interfaz conversacional (Streamlit)
- [ ] Despliegue en Oracle Cloud Infrastructure (OCI)

## Documentos incluidos (datos ficticios)

| Documento | Categoría | Formato |
|---|---|---|
| Política de Privacidad | Legal y Compliance | Markdown |
| Términos y Condiciones | Legal y Compliance | Markdown |
| Política de Reembolsos y Devoluciones | Operacional | Word (.docx) |
| Guía de Envíos y Entregas | Operacional | Word (.docx) |
| Preguntas Frecuentes (FAQ) | Marketing y Comercial | PDF |

## Stack técnico

- **LLM / Embeddings:** OpenAI (`gpt-4o-mini` + `text-embedding-3-small`)
- **Base de datos vectorial:** ChromaDB
- **Orquestación RAG:** LangChain
- **Interfaz:** Streamlit
- **Despliegue:** Oracle Cloud Infrastructure (OCI Compute / Container Instances)

## Cómo ejecutar (en construcción)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # agregar tu OPENAI_API_KEY
python src/ingest.py   # indexa los documentos de /docs
streamlit run src/app.py
```

## Captura / Video del agente en ejecución

*(Se agregará aquí una vez desplegado en OCI)*

## Estructura del proyecto

```
alura-agente-rag/
├── docs/           # Documentos fuente (los datos que el agente consulta)
├── src/            # Código del pipeline RAG y la app
├── data/           # Base de datos vectorial persistida (Chroma)
└── requirements.txt
```

## Autor

Juan David Olarte Hernández — Challenge Alura Agente (ONE)
