FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir rembg==2.0.61 onnxruntime==1.20.1 pillow fastapi==0.115.6 uvicorn==0.34.0
ENV U2NET_HOME=/models/u2net
RUN python -c "from rembg import new_session; new_session('isnet-general-use')"
WORKDIR /app
COPY server.py /app/server.py
ENV PORT=5000 PYTHONUNBUFFERED=1
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT:-5000}/healthz" || exit 1
CMD ["python", "server.py"]
