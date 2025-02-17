echo ""

echo "LOCAL Start Mosquitto in the background"
echo ""
mosquitto -p 1884 -d
MOSQUITTO_PID=$!

echo "Hello Kehua"
echo "---"

python3 -m src.app data/options.yaml

echo "LOCAL Stop Mosquitto"
echo ""
kill $MOSQUITTO_PID