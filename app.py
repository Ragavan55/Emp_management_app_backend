from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/hello', methods=['GET'])
def hello():

    backend_message = {"message" : "Hello this is from backend"}
    return jsonify(backend_message), 200

if __name__ == '__main__':
    app.run(port=5000 , debug=True)