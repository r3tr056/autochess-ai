
import os
import re

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from logging import getLogger
from threading import Thread
from time import time

import chess.pgn

logger = getLogger(__name__)

TAG_REGEX = re.compile(r"^\[([A-Za-z0-9_]+)\s+\"(.*)\"\]\s*$")

def start(config: Config):
	return SupervisedLearningWorker(config).start()

class SupervisedLearningWorker:
	''' Worker which performs supervised learning on a recorded game '''

	def __init__(self, config: Config):
		self.config = config
		self.buffer = []

	def start(self):
		''' Start the actual training '''
		self.buffer = []
		self.idx = 0
		start_time = time()

		with ProcessPoolExecutor(max_workers=7) as executor:
			games = self.get_games_from_database()
			for res in as_completed([executor.submit(get_buffer, self.config, game) for game in games]):
				self.idx += 1
				env, data = res.result()
				self.save_data(data)
				end_time = time()
				logger.debug(f"game {self.idx:4} time={(end_time - start_time):.3f}s "
					f"halfmoves={env.num_halfmoves:3} {env.winner:12}"
					f"{'by resign ' if board.resigned else '      '}"
					f"{board.observation.split(' ')[0]}"
				)
				start_time = end_time
		if len(self.buffer) > 0:
			self.flush_buffer()

	
