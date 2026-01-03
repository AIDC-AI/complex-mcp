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

echo "Starting Light application suite..."

# Start each application
fastmcp run software/LightSystem/app.py --transport http --port 9000 &
PIDS+=($!)
echo "LightSystem started (PID: $!, Port: 9000)"
sleep 1

fastmcp run software/LightTalk/app.py --transport http --port 9001 &
PIDS+=($!)
echo "LightTalk started (PID: $!, Port: 9001)"
sleep 1

fastmcp run software/LightShop/app.py --transport http --port 9002 &
PIDS+=($!)
echo "LightShop started (PID: $!, Port: 9002)"
sleep 1

fastmcp run software/LightWeather/app.py --transport http --port 9003 &
PIDS+=($!)
echo "LightWeather started (PID: $!, Port: 9003)"
sleep 1

fastmcp run software/LightFlight/app.py --transport http --port 9004 &
PIDS+=($!)
echo "LightFlight started (PID: $!, Port: 9004)"
sleep 1

fastmcp run software/LightStock/app.py --transport http --port 9005 &
PIDS+=($!)
echo "LightStock started (PID: $!, Port: 9005)"
sleep 1

echo "All applications started successfully. Press Ctrl+C to shut down all applications."

# Wait for all processes
for PID in "${PIDS[@]}"; do
    wait $PID
done