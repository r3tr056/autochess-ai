

import os
import numpy as np

class PlayWithHumanConfig:
	def __init__(self):
		self.simulation_num_per_move = 1200
		self.threads_multiplier = 2
		self.c_puct = 1
		self.noise_eps = 0
		self.tau_decay_rate = 0
		self.resign_threshold = None

	def update_play_config(self, pc):
		pc.simulation_num_per_move = self.simulation_num_per_move
		pc.search_threads *= self.threads_multiplier
		pc.c_puct = self.c_puct
		pc.noise_eps = self.noise_eps
		pc.tau_decay_rate = self.tau_decay_rate
		pc.resign_threshold = self.resign_threshold
		pc.max_game_length = 999999

class Options:
	new = False

class ResourceConfig:

	def __init__(self):
		self.project_dir = os.environ.get("PROJECT_DIR", _project_dir())
		self.data_dir = os.environ.get("DATA_DIR", _data_dir())

		self.model_dir = os.environ.get("MODEL_DIR", os.path.join(self.data_dir, "model"))
		self.model_best_config_path = os.path.join(self.model_dir, "model_best_config.json")
		self.model_best_weight_path = os.path.join(self.model_dir, "model_best_weight.h5")

		self.model_best_distrubuted_ftp_server = "achessnet.autochess.net"
		self.model_best_distrubuted_ftp_user = "chessnet_service_acc"
		self.model_best_distrubuted_ftp_password = "chessnet_service_acc_pass"
		self.model_best_distrubuted_ftp_remote_path = "/achessnet.autochess.net/"

		self.next_gen_model_dir = os.path.join(self.model_dir, "next_gen")
		self.next_gen_model_dirname_tmpl = "model_%s"
		self.next_gen_model_config_filename = "model_config.json"
		self.next_gen_model_weight_filename = "model_weight.h5"

		self.play_data_dir = os.path.join(self.project_dir, "logs")
		self.main_log_path = os.path.join(self.log_dir, "main.log")

	def create_directories(self):
		dirs = [self.project_dir, self.data_dir, self.model_dir, self.play_data_dir, self.log_dir, self.next_gen_model_dir]
		for d in dirs:
			if not os.path.exists(d):
				os.makedirs(d)

def flipped_uci_labels():
	def repl(x):
		return "".join([(str(9 - int(a)) if a.isdigit() else a) for a in x])
	return [repl(x) for x in create_uci_labels()]

def create_uci_labels():
	labels_array = []
	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
	numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
	promoted_to = ['q', 'r', 'b', 'n']

	for l1 in range(8):
		for n1 in range(8):
			destinations = [(t, n1) for t in range(8)] + [(l1, t) for t in range(8)] + [(l1+t, n1+t) for t in range(-7, 8)] + [(l1+t, n1-t) for t in range(-7, 8)] + [(l1 + a, n1+b) for (a, b) in [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]

			for (l2, n2) in destinations:
				if (l1, n1) != (l2, n2) and l2 in range(8) and n2 in range(8):
					move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
					labels_array.append(move)