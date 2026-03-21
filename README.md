# ComplexMCP Benchmark

ComplexMCP is a benchmark for evaluating model performance in complex software workflows and large API tool ecosystems.

## 1) Build Docker Image

```bash
docker build -t complexmcp:latest .
```

## 2) Start Container

```bash
docker rm -f complexmcp 2>/dev/null || true
docker run -d --name complexmcp \
  -p 8000-8007:8000-8007 \
  -p 9000-9006:9000-9006 \
  complexmcp:latest
```

## 3) Create `.env`

Create a `.env` file in the project root, following `.env.example` format.

```bash
cp .env.example .env
```

Then fill values in `.env` as needed.

## 4) Run Benchmark

```bash
python run_benchmark.py --tool-config config/general.yaml \
  --model [model_name]
```
