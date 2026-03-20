#!/usr/bin/env bash
set -euo pipefail

PIDS=()
CLEANED_UP=0

cleanup() {
    if [[ "$CLEANED_UP" -eq 1 ]]; then
        return
    fi

    CLEANED_UP=1
    echo "Shutting down all sandbox processes..."

    for pid in "${PIDS[@]:-}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    for pid in "${PIDS[@]:-}"; do
        if kill -0 "$pid" 2>/dev/null; then
            wait "$pid" 2>/dev/null || true
        fi
    done
}

trap cleanup EXIT INT TERM

if [[ -d /app ]]; then
    cd /app
fi

echo "Starting benchmark sandbox (servers + softwares)..."

start_process() {
    local name="$1"
    shift

    "$@" &
    local pid=$!
    PIDS+=("$pid")

    echo "$name started (PID: $pid)"
    sleep 1
}

# MCP servers (8000-8007)
start_process "MathServer" fastmcp run servers/math/app.py --transport http --port 8000
start_process "UnitServer" python -m servers.unit.app --port 8001
start_process "OsintServer" fastmcp run servers/osint/app.py --transport http --port 8002
start_process "TimeServer" fastmcp run servers/time/app.py --transport http --port 8003
start_process "LangServer" fastmcp run servers/lang/app.py --transport http --port 8004
start_process "CryptoServer" fastmcp run servers/crypto/app.py --transport http --port 8005
start_process "GraphsServer" fastmcp run servers/graphs/app.py --transport http --port 8006
start_process "ChemServer" fastmcp run servers/chem/app.py --transport http --port 8007

# Light softwares (9000-9006)
start_process "LightSystem" fastmcp run software/LightSystem/app.py --transport http --port 9000
start_process "LightTalk" fastmcp run software/LightTalk/app.py --transport http --port 9001
start_process "LightShop" fastmcp run software/LightShop/app.py --transport http --port 9002
start_process "LightWeather" fastmcp run software/LightWeather/app.py --transport http --port 9003
start_process "LightFlight" fastmcp run software/LightFlight/app.py --transport http --port 9004
start_process "LightStock" fastmcp run software/LightStock/app.py --transport http --port 9005
start_process "LightNews" fastmcp run software/LightNews/app.py --transport http --port 9006

echo "All sandbox services started."

# Wait all processes; if any exits non-zero, propagate the failure.
for pid in "${PIDS[@]}"; do
    if wait "$pid"; then
        :
    else
        exit $?
    fi
done
