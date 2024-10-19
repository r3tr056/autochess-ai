
import math
import yaml

from django.db import models
from chess_server.apps.authentication.models import User
from chess_server.apps.autochess_engine import ChessUtils
from utils import data_utils

class PersistentJSONObject(models.Model):
	data = models.TextField(default='{}')

	def __str__(self):
		return str(self.id)

	def get_data(self, path=None):
		''' loads data, from a given key if specified '''
		data = json.loads(self.data)
		if path:
			return data_utils.access(data, path)
		else:
			return data

	def set_data(self, path, new_data):
		''' writes data, at given path if specified '''
		if path:
			data = json.loads(self.data)
			utils.access(data, path, new_data)
			self.data = json.dumps(data, seperators=(',', ':'), cls=Encoder)
		else:
			self.data = json.dumps(new_data, seperators=(',', ':'), cls=Encoder)
		self.save()
		return True

	def pop_data(self, path, key):
		''' pops item using designed path '''
		item = self.get_data(path)
		if item:
			result = dict()
			for k, v in item.items():
				if k != key:
					result[k] = v
			self.set_data(path, result)
			return True
		return False

	def add_item(self, path, key, data, rule='%02d'):
		items = self.get_data('%s/%s' % (path, key))
		if not items:
			items = dict()
		new_key = rule % (len(items) + 1)
		items[new_key] = data
		self.set_data('%s/%s' % (path, key), items)
		return True

