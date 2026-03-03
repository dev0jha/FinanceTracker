from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rag_engine import query_docs, index_docs
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    if not os.path.exists(".chroma"):
        return jsonify({"error": "Search index not found. Please run indexing first."}), 400

    try:
        response = query_docs(user_query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/index", methods=["POST"])
def reindex():
    try:
        index_docs()
        return jsonify({"message": "Indexing complete!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
