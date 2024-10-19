def pretty_print(env, colors):
	new_pgn = open("test3.pgn", "at")
	game = chess.pgn.Game.from_board(env.board)
	game.headers["Result"] = evn.result
	game.headers["White"], game.headers["Black"] = colors
	game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
	new_pgn.write(str(game) + "\n\n")
	pyperclip.copy(evn.board.fen())

def find_pgn_files(directory, pattern='*.pgn'):
	dir_pattern = os.path.join(directory, pattern)
	files = list(sorted(glob(dir_pattern)))
	return files

def get_game_data_filenames(directory, pattern='*.pgn'):
	pattern = os.path.join(rc.play_data_dir, rc.play_data_filename_tmpl % "*")
	files = list(sorted(glob(pattern)))
	return files

def get_next_generation_model_dirs(rc: ResourceConfig):
	dir_pattern = os.path.join(rc.get_next_generation_model_dirs, rc.get_next_generation_model_dirname_tmpl % "*")
	dirs = list(sorted(glob(dir_pattern)))
	return dirs

def write_game_data_to_files(path, data):
	try:
		with open(path, "wt") as f:
			json.dumps(data, f)
	except Exception as e:
		print(e)

def read_game_data_from_file(path):
	try:
		with open(path, "rt") as f:
			return json.load(f)
	except Exception as e:
		print(e)