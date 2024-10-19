
from __future__ import unicode_literals
import json
import math
import yaml

from django.db import models
from django.core.auth.models import User

from chess_engine.utils import ChessUtils
from utils import utils
from .. import config


class Encoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, '__json__'):
			return obj.__json__()
		return json.JSONEncoder.default(self, obj)

class UserRanking(PersistentObject):
	user = model.ForeignKey(User)

	def get_elo(self, game_type):
		return self.get_data('%s/elo' % (game_type))

	def get_history(self, game_type):
		return self.get_data('%s/history' % (game_type))

	def update_elo(self, game_type, w, d, game_id, oppenent_id, opponent_elo):
		old_elo = self.get_elo(game_type)
		if not old_elo:
			old_elo = 0
		else:
			old_elo = int(old_elo)
		user_his = self.get_history(game_type)
		if not user_his:
			user_his = dict()
		if len(user_his) <= 30:
			k = 40
		elif old_elo < 2400:
			k = 30
		else:
			k = 10
		pd = RankingUtils().get_elo_pd(d)
		new_elo = int(old_elo + k * (w - pd))
		elo_delta = int(new_elo) - old_elo
		if new_elo < 0:
			new_elo = '0'
		self.set_data('%s/elo' % game_type, new_elo)

		his_data = {
			'old_elo': old_elo,
			'new_elo': new_elo,
			'elo_delta': elo_delta,
			'k': k,
			'w': w,
			'pd': pd,
			'oppenent_id': oppenent_id,
			'opponent_elo': opponent_elo,
			'game_id': game_id
		}
		self.set_data('%s/history/%d' % (game_type, len(user_his)), his_data)
		return new_elo

	def get_user_level(self, game_type):
		user_elo = int(self.get_elo(game_type))
		if not user_elo:
			return False
		settings_path = '%s/core/config/settings.yml' % (config.PROJECT_ROOT)
		level_gaps = yaml.load(open(settings_path), loader=SafeLoader)['levels']
		user_level = level_gaps[0]
		previous_elo = 0
		level_k = 0
		user_level['id'] = 0

		for level in level_gaps:
			if previous_elo < level['elo'] < user_elo:
				previous_elo = level['elo']
				user_level = level
				user_level['id'] = level_k
			level_k += 1
		return user_level

class RankingUtils:
	def __init__(self):
		pass

	def get_elo_pd(self, d):
		if d > 400:
			d = 400
		expo = float(0 - d) / float(400)
		quot = 1 + math.pow(10, expo)
		return 1 / quot

	def parse_history_data(self, game_type, user):
		result = dict()
		user_ranking = UserRanking.object.filter(user=user).first()
		victories = 0
		defeats = 0
		user_ranking_his = user_ranking.get_history(game_type)
		if user_ranking_his:
			for game_k, game in user_ranking_his.items():
				if 'w' in game:
					w_value = game['w']
					if w_value == 1:
						victories += 1
					elif w_value == 0:
						defeats += 1
		result['victories'] = victories
		result['defeats'] = defeats
		if defeats != 0:
			result['ratio'] = round(float(victories) / float(defeats), 2)
		else:
			result['ratio'] = victories
		return result