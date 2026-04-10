FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir build hatchling \
    && pip install --no-cache-dir .

EXPOSE 8152

ENTRYPOINT ["zotero-mcp", "serve", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8152"]
