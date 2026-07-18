"""
Interfaz conversacional del agente de TiendaLuna.

Ejecutar con:
    streamlit run src/app.py
"""

# --- Parche de compatibilidad para Streamlit Community Cloud ---
# ChromaDB requiere sqlite3 >= 3.35, pero el sistema de Streamlit Cloud trae una versión
# más antigua. pysqlite3-binary trae una versión moderna que reemplaza al módulo estándar.
# Debe ir ANTES de cualquier import que dependa de chromadb.
try:
    __import__("pysqlite3")
    import sys as _sys
    _sys.modules["sqlite3"] = _sys.modules.pop("pysqlite3")
except ImportError:
    pass  # en local (Mac/Linux/Windows con sqlite reciente) no hace falta

import os
import sys
from pathlib import Path

import streamlit as st

# En Streamlit Cloud, la API key se configura como "Secret" en el dashboard.
# La copiamos a una variable de entorno para que ingest.py/query.py la lean igual
# que en local (donde viene del archivo .env).
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

sys.path.insert(0, str(Path(__file__).parent))

from query import answer_question, get_collection
from ingest import ingest_single_document, build_index, DOCS_DIR

UPLOAD_CATEGORIES = ["Legal y Compliance", "Operacional", "Marketing y Comercial", "Otra"]

st.set_page_config(
    page_title="Asistente TiendaLuna",
    page_icon="🌙",
    layout="centered",
)

CATEGORIES = ["Todas", "Legal y Compliance", "Operacional", "Marketing y Comercial"]

st.title("🌙 Asistente Virtual — TiendaLuna")
st.caption(
    "Pregunta lo que quieras sobre políticas, envíos, devoluciones o privacidad. "
    "Respondo únicamente con base en los documentos internos de la empresa."
)

# Verifica que el índice ya exista; si no, lo construye automáticamente desde docs/
# (esto pasa en el primer arranque de la app en Streamlit Cloud, o la primera vez en local)
try:
    get_collection()
    index_ready = True
except Exception:
    index_ready = False
    with st.spinner("🧠 Primer arranque: indexando los documentos base, esto toma ~1 minuto..."):
        try:
            build_index()
            get_collection()
            index_ready = True
        except Exception as e:
            index_ready = False
            st.session_state["_index_error"] = str(e)

if not index_ready:
    error_detail = st.session_state.get("_index_error", "")
    st.warning(
        "⚠️ Todavía no hay una base de conocimiento indexada. "
        "Sube un documento desde la barra lateral para crear el índice, "
        "o revisa que GEMINI_API_KEY esté bien configurada."
        + (f"\n\nDetalle: {error_detail}" if error_detail else "")
    )

with st.sidebar:
    st.header("Filtros")
    selected_category = st.selectbox("Categoría de documentos", CATEGORIES)
    st.markdown("---")
    st.markdown(
        "**Documentos disponibles:**\n\n"
        "- Política de Privacidad\n"
        "- Términos y Condiciones\n"
        "- Política de Reembolsos\n"
        "- Guía de Envíos\n"
        "- Preguntas Frecuentes (FAQ)"
    )
    st.markdown("---")
    st.subheader("📤 Subir nuevo documento")
    st.caption("Agrega un documento (PDF, Word o Markdown) para mantener al agente actualizado.")

    uploaded_file = st.file_uploader(
        "Selecciona un archivo",
        type=["pdf", "docx", "md"],
        label_visibility="collapsed",
    )
    upload_category = st.selectbox("Categoría del documento", UPLOAD_CATEGORIES, key="upload_cat")

    if uploaded_file is not None:
        if st.button("Indexar documento", use_container_width=True):
            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            dest_path = DOCS_DIR / uploaded_file.name
            with open(dest_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(f"Procesando '{uploaded_file.name}'..."):
                try:
                    n_chunks = ingest_single_document(str(dest_path), category=upload_category)
                    st.success(f"✅ '{uploaded_file.name}' indexado ({n_chunks} fragmentos).")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Error al indexar: {e}")

    st.markdown("---")
    st.caption("Challenge Alura Agente · Powered by Gemini + ChromaDB")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! 👋 Soy el asistente virtual de TiendaLuna. ¿En qué puedo ayudarte hoy?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

chat_placeholder = "Escribe tu pregunta..." if index_ready else "Sube o indexa un documento primero..."
if prompt := st.chat_input(chat_placeholder, disabled=not index_ready):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            category_filter = None if selected_category == "Todas" else selected_category
            try:
                result = answer_question(prompt, category=category_filter)
                response_text = result["answer"]
                if result["sources"]:
                    sources_str = ", ".join(result["sources"])
                    response_text += f"\n\n📄 *Fuente(s): {sources_str}*"
            except Exception as e:
                response_text = f"⚠️ Ocurrió un error al procesar tu pregunta: {e}"

        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
