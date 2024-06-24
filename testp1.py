import os
from flask import Flask, jsonify, request
import requests
from collections import deque

app = Flask(__name__)

# Global variables (single-letter names)
w = 10  # Size of the sliding window
n = deque(maxlen=w)  # Deque to store numbers in the window
q = {
    "p": "primes",
    "f": "fibo",
    "e": "even",
    "r": "rand"
}
u = "http://20.244.56.144/test/{}"  # URL for fetching numbers from the test server

# Access token for authorization
a = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."  # Your access token here

# Route to handle GET requests for fetching numbers based on qualifier
@app.route('/numbers/<qualifier>', methods=['GET'])
def averagecaculator(qualifier):
    app.logger.debug(f"Received request for qualifier: {qualifier}")
    
    # Check if the qualifier is valid
    if qualifier not in q:
        app.logger.error(f"Invalid qualifier: {qualifier}")
        return jsonify({"error": "Invalid qualifier"}), 400
    
    # Determine the endpoint based on the qualifier
    e = q[qualifier]
    url = u.format(e)
    headers = {"Authorization": f"Bearer {a}"}
    
    try:
        # Make a GET request to the test server endpoint
        r = requests.get(url, headers=headers, timeout=0.5)
        
        # Handle non-200 status codes
        if r.status_code != 200:
            app.logger.error(f"Failed to fetch numbers from test server, status: {r.status_code}")
            return jsonify({"error": "Failed to fetch numbers from test server"}), 500
        
        # Extract numbers from the JSON response
        m = r.json().get("numbers", [])
        app.logger.debug(f"Fetched numbers: {m}")
        
        # Update the sliding window with unique numbers from the fetched list
        p = list(n)
        for number in m:
            if number not in n:
                n.append(number)
        
        c = list(n)
        
        # Calculate the average of numbers in the current window state
        v = sum(c) / len(c) if c else 0
        
        # Log debug information
        app.logger.debug(f"Previous window state: {p}")
        app.logger.debug(f"Current window state: {c}")
        app.logger.debug(f"Average: {v}")
        
        # Return JSON response with fetched numbers, previous window state, current window state, and average
        return jsonify({
            "numbers": m,
            "windowPrevState": p,
            "windowCurrState": c,
            "avg": round(v, 2)
        })
    
    except requests.exceptions.RequestException as e:
        # Handle request exceptions (e.g., timeout, connection error)
        app.logger.error(f"Request to test server failed: {e}")
        return jsonify({"error": "Request to test server failed"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(port=9876, debug=True)
