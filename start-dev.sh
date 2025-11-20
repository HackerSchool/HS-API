#!/bin/bash
# Start Flask API in development mode accessible from network
echo "Starting Flask API on all network interfaces..."
echo "API will be accessible at: http://localhost:8080 and http://YOUR_IP:8080"
python -m flask run --host=0.0.0.0 --port 8080

