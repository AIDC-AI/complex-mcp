#!/bin/zsh

# Signal handler function
cleanup() {
    echo -e "\nReceived interrupt signal, shutting down all child processes..."
    
    # Send SIGTERM to all child processes
    for PID in "${PIDS[@]}"; do
        if kill -0 $PID 2>/dev/null; then
            echo "Shutting down process $PID"
            kill $PID
        fi
    done
    
    # Wait for all processes to finish
    wait
    echo "All processes have been terminated"
    exit 0
}

# Set up signal traps
trap cleanup INT TERM

# Array to store process IDs
PIDS=()

echo "Starting Local MCP suite..."

# Start each servers
fastmcp run servers/math/app.py --transport http --host 0.0.0.0 --port 8000 &
PIDS+=($!)
sleep 1

python -m servers.unit.app --host 0.0.0.0 --port 8001 &
PIDS+=($!)
echo "Started UnitServer ..."
sleep 1

fastmcp run servers/osint/app.py --transport http --host 0.0.0.0 --port 8002 &
PIDS+=($!)
sleep 1

fastmcp run servers/time/app.py --transport http --host 0.0.0.0 --port 8003 &
PIDS+=($!)
sleep 1

fastmcp run servers/lang/app.py --transport http --host 0.0.0.0 --port 8004 &
PIDS+=($!)
sleep 1

fastmcp run servers/crypto/app.py --transport http --host 0.0.0.0 --port 8005 &
PIDS+=($!)
sleep 1

fastmcp run servers/graphs/app.py --transport http --host 0.0.0.0 --port 8006 &
PIDS+=($!)
sleep 1

fastmcp run servers/chem/app.py --transport http --host 0.0.0.0 --port 8007 &
PIDS+=($!)
sleep 1

echo "All MCP servers started successfully. Press Ctrl+C to shut down all servers."

# Wait for all processes
for PID in "${PIDS[@]}"; do
    wait $PID
done
