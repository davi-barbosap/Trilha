# trilha-api — núcleo testado chamado pelos fluxos do n8n (ADR-007)
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
COPY trilha ./trilha
RUN pip install --no-cache-dir . && useradd --create-home trilha
USER trilha
ENV TRILHA_CLIENTES_DIR=/clientes TRILHA_SIMULAR=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8080/saude')"
CMD ["python", "-m", "trilha", "servir", "--porta", "8080"]
