from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from collections import deque

# Enhanced in-memory data storage with history
latest_data = {
    "distance": "N/A",
    "velocity": "N/A",
    "rf_power": "N/A",
    "rf_stability": "N/A",
    "score": "N/A",
    "state": "UNKNOWN"
}

# Store historical data (last 100 records)
history = deque(maxlen=100)

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/update', methods=['POST'])
def update_data():
    global latest_data
    
    # Get the JSON data sent by the ESP32
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Received data: {data}")
    
    # Update latest data
    latest_data = data
    
    # Add to history with timestamp
    history_entry = {
        **data,
        "timestamp": datetime.now().isoformat()
    }
    history.append(history_entry)
    
    return jsonify({
        "status": "success", 
        "message": "Data received and stored",
        "records_stored": len(history)
    })

@app.route('/data', methods=['GET'])
def get_data():
    # Return the latest data to the frontend
    return jsonify(latest_data)

@app.route('/history', methods=['GET'])
def get_history():
    # Return historical data
    # Optionally support limit parameter
    limit = request.args.get('limit', type=int, default=50)
    
    # Convert deque to list and get last 'limit' items
    history_list = list(history)[-limit:]
    
    return jsonify({
        "history": history_list,
        "total_records": len(history),
        "returned_records": len(history_list)
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    # Calculate statistics from history
    if not history:
        return jsonify({
            "message": "No data available yet",
            "stats": {}
        })
    
    # Count states
    state_counts = {
        "SAFE": 0,
        "SUSPICIOUS": 0,
        "TRACKING": 0,
        "UNKNOWN": 0
    }
    
    distances = []
    scores = []
    
    for entry in history:
        state = entry.get("state", "UNKNOWN")
        if state in state_counts:
            state_counts[state] += 1
        
        try:
            if entry.get("distance") != "N/A":
                distances.append(float(entry.get("distance", 0)))
        except (ValueError, TypeError):
            pass
            
        try:
            if entry.get("score") != "N/A":
                scores.append(float(entry.get("score", 0)))
        except (ValueError, TypeError):
            pass
    
    stats = {
        "total_records": len(history),
        "state_counts": state_counts,
        "distance_stats": {
            "min": min(distances) if distances else 0,
            "max": max(distances) if distances else 0,
            "avg": sum(distances) / len(distances) if distances else 0
        },
        "score_stats": {
            "min": min(scores) if scores else 0,
            "max": max(scores) if scores else 0,
            "avg": sum(scores) / len(scores) if scores else 0
        }
    }
    
    return jsonify(stats)

@app.route('/clear', methods=['POST'])
def clear_history():
    # Clear all historical data (useful for testing)
    global history
    history.clear()
    
    return jsonify({
        "status": "success",
        "message": "History cleared"
    })

@app.route('/health', methods=['GET'])
def health_check():
    # Simple health check endpoint
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "records_in_memory": len(history)
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  DRONE DETECTION SERVER")
    print("=" * 60)
    print(f"  Starting server at: http://0.0.0.0:5000")
    print(f"  Dashboard URL: http://localhost:5000")
    print(f"  History endpoint: http://localhost:5000/history")
    print(f"  Stats endpoint: http://localhost:5000/stats")
    print("=" * 60)
    
    # Run the app on all available network interfaces on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)