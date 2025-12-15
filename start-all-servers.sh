PROJ_HOME=$PWD

PIDS=()

cd server/math
PIDS+=($!)
sh start.sh 8000 &
cd $PROJ_HOME

cd server/time
sh start.sh 8001 &
PIDS+=($!)
cd $PROJ_HOME

cd server/weather
sh start.sh 8002 &
PIDS+=($!)
cd $PROJ_HOME

echo "Type ':exit' to stop all services."

while true; do
    read -r input
    if [[ "$input" == ":exit" ]]; then
        echo "Stopping all fastmcp services..."
        for pid in "${PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo "Terminated process $pid"
            else
                echo "Process $pid already stopped"
            fi
        done
        wait "${PIDS[@]}" 2>/dev/null
        echo "All services stopped. Exiting."
        break
    else
        echo "Unknown command. Type ':exit' to quit."
    fi
done