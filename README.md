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
- [x] Despliegue en la nube (Streamlit Community Cloud)

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

> **Nota:** el pipeline RAG (extracción, chunking, embeddings, búsqueda semántica y generación)
> está implementado directamente con el SDK de Gemini y ChromaDB, sin frameworks de
> orquestación como LangChain o LangGraph. Esto fue una decisión intencional para demostrar
> el funcionamiento interno del RAG paso a paso.

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

## Ejemplos de preguntas y respuestas

**P: ¿Cuánto tiempo tengo para devolver un producto?**
> R: El cliente cuenta con 15 días calendario a partir de la fecha de entrega para solicitar la devolución de un producto.
> 📄 *Fuente: politica_reembolsos.docx*

**P: ¿Hacen envíos a otros países?**
> R: Sí, TiendaLuna realiza envíos internacionales a México, Chile, Perú y Ecuador.
> 📄 *Fuentes: faq.pdf, guia_envios.docx*

**P: ¿Qué pasa con mis datos personales si elimino mi cuenta?**
> R: Si eliminas tu cuenta, tienes el derecho a solicitar la eliminación de tus datos personales, conocido como "derecho al olvido". Estas solicitudes se atienden en un plazo máximo de 10 días hábiles. Además, los datos de cuentas inactivas por más de 3 años son eliminados o anonimizados, salvo obligación legal de conservarlos.
> 📄 *Fuente: politica_privacidad.md*

**P: ¿Cuál es el costo de envío a una zona rural?**
> R: El envío a zona rural o apartada cuesta $18.000 COP, con un tiempo estimado de 5 a 8 días hábiles.
> 📄 *Fuente: guia_envios.docx*

**P: ¿Puedo devolver ropa interior si no me gustó?**
> R: No, la ropa interior y los trajes de baño no son elegibles para devolución por razones de higiene.
> 📄 *Fuente: politica_reembolsos.docx*

**P: que pasa si me no alcanzo los 10 dias habiles** *(pregunta ambigua, respuesta honesta)*
> R: El contexto proporcionado no contiene información sobre qué sucede si no se alcanzan los 10 días hábiles en relación con una acción del cliente. La mención de "10 días hábiles" en los documentos se refiere al plazo en el que TiendaLuna procesa un reembolso, no a un plazo para el cliente.
> 📄 *Fuentes: guia_envios.docx, politica_reembolsos.docx*

*(Este último ejemplo muestra que el agente no inventa respuestas cuando la pregunta no tiene suficiente contexto en los documentos — reconoce la ambigüedad y explica qué sí sabe.)*


## Captura del agente en ejecución

🔗 **URL en vivo:** https://alura-agente-rag-mcypscvu4ar3emvhqnctwb.streamlit.app
<img width="1363" height="651" alt="image" src="https://github.com/user-attachments/assets/494c22e7-c86d-4710-8ae9-10951dcc9394" />

<img width="302" height="632" alt="image" src="https://github.com/user-attachments/assets/0ba3ae1f-99f7-472e-b2ef-2ab24f068c09" />




https://github.com/user-attachments/assets/d328c2e0-c077-4e6b-810c-5d1ec05d5f55









## Autor

Juan David Olarte Hernández — Challenge Alura Agente (ONE)
