from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from LLM import answer_question
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # Enable Cross-Origin Resource Sharing

@app.route('/')
def index():
    """Serve the index.html file as the main page."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint to handle chat messages.
    Accepts a JSON payload with 'query' and an optional 'session_id'.
    Returns a JSON response with the answer and the session_id.
    """
    data = request.json
    user_query = data.get('query')
    session_id = data.get('session_id') # Can be None for the first message

    if not user_query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        # Call your core logic from LLM.py
        result = answer_question(session_id, user_query)
        
        # Prepare the response
        response = {
            "answer": result.get("answer"),
            "session_id": result.get("session_id")
        }
        return jsonify(response)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible from outside the container
    app.run(host='0.0.0.0', port=5001, debug=True)