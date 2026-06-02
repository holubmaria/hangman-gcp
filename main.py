import os
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

WORD_BANK = ["google", "cloud", "serverless", "container", "kubernetes", "developer"]

# Simple in-memory game session tracker (For a production multi-user setup, use Firestore)
games = {}

@app.route('/api/start', methods=['POST'])
def start_game():
    game_id = str(random.randint(1000, 9999))
    secret_word = random.choice(WORD_BANK)
    
    games[game_id] = {
        "word": secret_word,
        "guessed": [],
        "lives": 6
    }
    
    display = ["_" for _ in secret_word]
    return jsonify({"game_id": game_id, "display": display, "lives": 6})

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.json
    game_id = data.get("game_id")
    letter = data.get("letter", "").lower()
    
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
        
    game = games[game_id]
    if letter and letter not in game["guessed"]:
        game["guessed"].append(letter)
        if letter not in game["word"]:
            game["lives"] -= 1

    # Calculate current state
    display = [char if char in game["guessed"] else "_" for char in game["word"]]
    
    status = "playing"
    if "_" not in display:
        status = "win"
    elif game["lives"] <= 0:
        status = "lose"
        
    return jsonify({
        "display": display,
        "lives": game["lives"],
        "status": status,
        "secret_word": game["word"] if status == "lose" else ""
    })

if __name__ == "__main__":
    # Cloud Run passes the port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
