# Utility methods for playing an actual game as a human against a
# model

import sys
from logging import getLogger

from auto_chess_engine.game.chess_player import ChessPlayer
from auto_chess_engine.config import Config, PlayWithHumanConfig
from auto_chess_engine.game.chessboard import ChessBoard

# module logger
logger = getLogger(__name__)

def start(config: Config):
	PlayWithHumanConfig().update_play_config(config.play)

	me_player = None
	env = ChessEnv().reset()

	while True:
		line = input()
		words = line.rstrip().split(" ", 1)
		if words[0] == "uci":
			print("id name AutoChess")
			print("id author AutoChess")
			print("uciok")
		elif words[0] == "isready":
			if not me_player:
				me_player = get_player(config)
			print("readyok")
		elif words[0] == "ucinewgame":
			env.reset()
		elif words[0] == "position":
			words = words[1].split(" ", 1)
			if words[0] == "startpos":
				env.reset()
			else:
				if words[0] == "fen":
					words = words[1].split(' ', 1)
				fen = words[0]
				for _ in range(5):
					words = words[1].split(' ', 1)
					fen += " " + words[0]
				env.update(fen)
			if len(words) > 1:
				words = words[1].split(" ", 1)
				if words[0] == "moves":
					for w in words[1].split(" "):
						env.step(w, False)
		elif words[0] == "go":
			if not me_player:
				me_player = get_player(config)
			action = me_player.action(env, False)
			print(f"bestmove { action }")
		elif words[0] == "stop":
			pass
		elif words[0] == "quit":
			break

def get_player(config):
	from auto_chess_engine.agent import ChessModel
	from auto_chess_engine.util import load_best_model_weight

	model = ChessModel(config)
	if not load_best_model_weight(model):
		raise RuntimeError("Best model not found!")
	return ChessPlayer(config, model.get_pipes(config.play.search_threads))

def info(depth, move, score):
	print(f"info score cp { int(score*100)} depth {depth} pv {move}")
	sys.stdout.flush()