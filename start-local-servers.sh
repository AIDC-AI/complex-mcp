PROJ_HOME=$PWD

PIDS=()

cd servers/math
PIDS+=($!)
sh start.sh 8000 &
cd $PROJ_HOME

cd servers/time
sh start.sh 8001 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/weather
sh start.sh 8002 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/car
sh start.sh 8003 &
PIDS+=($!)
cd $PROJ_HOME

cd servers
sh unit_start.sh &
PIDS+=($!)
cd $PROJ_HOME

cd servers/bibliomantic
sh start.sh 8005&
PIDS+=($!)
cd $PROJ_HOME

cd servers/bio
sh bio_start.sh 8006&
PIDS+=($!)
cd $PROJ_HOME

cd servers/call
sh start.sh 8007 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/fruit
sh start.sh 8008 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/game
sh start.sh 8009 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/nixos
sh start.sh 8010 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/osint
sh start.sh 8011 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/reddit
sh start.sh 8012 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/medcalc
sh start.sh 8013 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/movie
sh start.sh 8014 &
PIDS+=($!)
cd $PROJ_HOME

cd servers/nasa
sh start.sh 8015 &
PIDS+=($!)
cd $PROJ_HOME

cd servers
sh paper_start.sh &
PIDS+=($!)
cd $PROJ_HOME

cd servers/scientific
sh start.sh 8017 &
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