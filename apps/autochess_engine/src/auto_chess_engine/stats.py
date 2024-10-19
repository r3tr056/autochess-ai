class ActionStats:
	''' Holds the stats needed for the AGZ MCTS algo for a specific action taken from a specific state 

	Attributes:
		: int n : number of visits to this action by the algo
		: float w : every time a child of this action is visited by the algo, this accumulates the value of that child. This is modified by a virtual loss function which encourages the network to explore different nodes.
		: float q : mean action value (total value from all visits to this action divided by the total number of visits to this action, its just w/n)
		: float p : prior probablity of taking this action, given the policy network
	'''
	def __init__(self):
		self.n = 0
		self.w = 0
		self.q = 0
		self.p = 0

class VisitStats:
	def __init__(self):
		self.a = defaultdict(ActionStats)
		self.sum_n = 0


class ChessPlayer:

	def __init__(self, config: Config, pipes: List[Pipe]=None, play_config: Config=None, dummy:bool=False) -> None:
		self.moves = []

		self.tree = defaultdict(VisitStats)
		self.config = config
		self.play_config = play_config or self.config.play
		self.labels_n = config.n_labels
		self.labels = config.labels
		self.move_lookup = {chess.Move.from_uci(move) : i for move, i in zip(self.labels, range(self.labels_n))}
		if dummy:
			return

		self.pipe_pool = pipes
		self.node_lock = defaultdict(Lock)

	def reset(self) -> None:
		''' Reset the tree to begin a new exploration of states '''
		self.tree = defaultdict(VisitStats)

	def deboog(self, env: ChessEnv) -> None:
		print(env.testval())

		state = state_key(env)
		my_visit_stats = self.tree[state]
		stats = []
		for action, a_s in my_visit_stats.a.items():
			moi = self.move_lookup[action]
			stats.append(np.asarray([a_s.n, a_s.w, a_s.q, a_s.p, moi]))
		stats = np.asarray(stats)
		a = stats[stats[:, 0].argsort()[::-1]]

		for s in a:
			print(f'{self.labels[int(s[4])]:5}: '
				f'n: {s[0]:3.0f} '
				f'w: {s[1]:7.3f} '
				f'q: {s[2]:7.3f} '
				f'p: {s[3]:7.5f}'
			)

	def action(self, env:ChessEnv, can_stop:bool=True) -> Any:
		'''
		Figures out the next best move within the specified environment and returns a string describing the action to take 
		
		:param env: ChessEnv -> environment in which to figure out the action
		:param can_stop: bool -> whether we are allowed to take no action (return None)
		'''

		self.reset()

		# for tl in range(self.play_config.thinking_loop)
		root_value, naked_value = self.search_moves(env)
		policy = self.calc_policy(env)
		my_action = int(np.random.choice(range(self.labels_n), p = self.apply_temperature(policy, env.num_halfmoves)))


