from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# This dictionary will act as our simple in-memory "database"
latest_data = {
    "distance": "N/A",
    "velocity": "N/A",
    "rf_power": "N/A",
    "rf_stability": "N/A",
    "score": "N/A",
    "state": "UNKNOWN"
}

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app) # Allow cross-origin requests

@app.route('/')
def root():
    # Serve the index.html file from the same directory
    return send_from_directory('.', 'index.html')

@app.route('/update', methods=['POST'])
def update_data():
    global latest_data
    # Get the JSON data sent by the ESP32
    data = request.get_json()
    print(f"Received data: {data}")
    # Update our global variable
    latest_data = data
    return jsonify({"status": "success", "message": "Data received"})

@app.route('/data', methods=['GET'])
def get_data():
    # Provide the latest data to the frontend
    return jsonify(latest_data)

if __name__ == '__main__':
    # Run the app on all available network interfaces on port 5000
    # This makes it accessible from other devices on your local network
    app.run(host='0.0.0.0', port=5000)