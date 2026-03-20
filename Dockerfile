FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install uv \
    && uv pip install --system -r requirements.txt

COPY . .
RUN chmod +x docker/start_benchmark_sandbox.sh start_servers.sh start_softwares.sh

EXPOSE 8000 8001 8002 8003 8004 8005 8006 8007 9000 9001 9002 9003 9004 9005 9006

CMD ["./docker/start_benchmark_sandbox.sh"]
