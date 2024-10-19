
''' Defines the process which will listen on the pipe for
and observation of the game state and return a prediction from
the policy and value network '''

from multiprocessing import wait, Pipe
from threading import Thread

import numpy as np

from auto_chess_engine.config import Config

class ChessModelAPI:
    ''' The API for listening to the pipe '''
    def __init__(self, agent_model):
        self.agent_model = agent_model
        self.batch_size = batch_size
        self.pipes = []

    def start(self):
        # Start a thread, listen on the api and make predictions
        prediction_worker = Thread(target=self._predict_batch_worker, name='prediction_worker')
        prediction_worker.daemon = True
        prediction_worker.start()

    def create_pipe(self):
        p_in, p_out = Pipe()
        self.pipes.append(p_in)
        return p_out

    def _predict_batch_worker(self):
        while True:
            ready = wait(self.pipes, timeout=0.001)
            if not ready:
                continue

            data, result_pipes = [], []
            for pipe in ready:
                while pipe.poll():
                    data.append(pipe.recv())
                    result_pipes.append(pipe)

            if data:
                data = np.asarray(data, dtype=np.float32)
                num_batches = (len(data) + self.batch_size - 1) // self.batch_size

                for i in range(num_batches):
                    start_idx = i * self.batch_size
                    end_idx = (i + 1) * self.batch_size
                    batch_data = data[start_idx:end_idx]

                    policy_array, value_array = self.agent_model.model.predict_on_batch(batch_data)
                    for pipe, p, v in zip(result_pipes, policy_array, value_array):
                        pipe.send((p, float(v)))