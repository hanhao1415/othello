# -*- coding: utf-8 -*-
import sys
sys.path.append("../")

import os

from flask import Flask, request, send_from_directory, jsonify
import json
from othello import Board
from value import ModelScorer, ScorerWrapper
from ai import Bot

board = Board()
model_file = "../model/model.cpt.npy.4"
scorer = ModelScorer(model_file)
black_bot = Bot(scorer, 4, 7, Board.BLACK)
white_bot = Bot(scorer, 4, 7, Board.WHITE)

role_mapping = { "black": (black_bot, Board.BLACK), "white": (white_bot, Board.WHITE) }

def _opponent(role):
    if role == Board.BLACK:
        return Board.WHITE, "white"
    else:
        return Board.BLACK, "black"

app = Flask(__name__, static_folder="./ui/build/", static_url_path="")

@app.route("/othello")
def index():
    return send_from_directory("./ui/build/", "index.html")

@app.route("/othello/new")
def new_game():
    board.init_board()
    ret = { "board": board.board.tolist(),
            "options": board.feasible_pos(Board.BLACK),
            "blackScore": 2,
            "whiteScore": 2,
            "turn": "black" }

    return jsonify(**ret)

@app.route("/othello/play", methods=["POST"])
def play():
    data = json.loads(request.form["data"])

    player, role = role_mapping[data["player"]]

    board.set_board(data["board"])

    if "action" in data:
        r, c = data["action"]
    else:
        r, c = player.play(board)

    board.flip(r, c, role)

    next_role, next_role_name = _opponent(role)
    options = board.feasible_pos(next_role)
    if len(options) == 0:
        next_role, next_role_name = role, data["player"]
        options = board.feasible_pos(next_role)
    if len(options) == 0:
        next_role_name = "none"

    black_score = board.score(Board.BLACK)
    white_score = board.score(Board.WHITE)
    ret = { "action": [r, c],
            "board": board.board.tolist(),
            "turn": next_role_name,
            "blackScore": black_score,
            "whiteScore": white_score,
            "options": options }

    return jsonify(**ret)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9199, passthrough_errors=True)