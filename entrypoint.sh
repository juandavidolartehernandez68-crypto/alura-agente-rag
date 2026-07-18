#!/bin/sh
set -e

# Si la base vectorial no existe todavía dentro del contenedor, la genera
if [ ! -d "/app/data/chroma" ] || [ -z "$(ls -A /app/data/chroma 2>/dev/null)" ]; then
  echo "📦 No se encontró índice vectorial. Generando con src/ingest.py..."
  python src/ingest.py
else
  echo "✅ Índice vectorial ya existe, se omite la ingesta."
fi

streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
