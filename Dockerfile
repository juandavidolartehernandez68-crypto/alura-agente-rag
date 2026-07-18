FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY docs/ ./docs/

# La base vectorial se genera en el primer arranque del contenedor (ver entrypoint.sh)
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
