import os
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import firestore

app = Flask(__name__)
CORS(app)

WORD_BANK = ["google", "cloud", "serverless", "container", "kubernetes", "developer"]

# Initialize Firestore Client
db = firestore.Client()

@app.route('/api/start', methods=['POST'])
def start_game():
    secret_word = random.choice(WORD_BANK)
    
    # Create a new document in the 'games' collection with an auto-generated ID
    game_ref = db.collection("games").document()
    game_id = game_ref.id
    
    game_ref.set({
        "word": secret_word,
        "guessed": [],
        "lives": 6
    })
    
    display = ["_" for _ in secret_word]
    return jsonify({"game_id": game_id, "display": display, "lives": 6})

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.json or {}
    game_id = data.get("game_id")
    letter = data.get("letter", "").lower()
    
    if not game_id:
        return jsonify({"error": "game_id is required"}), 400
        
    game_ref = db.collection("games").document(str(game_id))
    game_doc = game_ref.get()
    
    if not game_doc.exists:
        return jsonify({"error": "Game not found"}), 404
        
    game = game_doc.to_dict()
    word = game.get("word", "")
    guessed = game.get("guessed", [])
    lives = game.get("lives", 6)
    
    if letter and letter not in guessed:
        guessed.append(letter)
        if letter not in word:
            lives -= 1
        # Update the state in Firestore
        game_ref.update({
            "guessed": guessed,
            "lives": lives
        })

    # Calculate current state
    display = [char if char in guessed else "_" for char in word]
    
    status = "playing"
    if "_" not in display:
        status = "win"
    elif lives <= 0:
        status = "lose"
        
    return jsonify({
        "display": display,
        "lives": lives,
        "status": status,
        "secret_word": word if status == "lose" else ""
    })

if __name__ == "__main__":
    # Cloud Run passes the port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)