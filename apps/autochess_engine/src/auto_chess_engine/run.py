# the command line entry point

import os
import sys
import multiprocessing as mp

__PATH__ = os.path.dirname(os.path.dirname(__file__))

if __PATH__ not in sys.path:
    sys.path.append(__PATH__)

if __name__ == "__main__":
    mp.set_start_method('spawn')
    sys.setrecursionlimit(10000)
    from auto_chess_engine import engine
    manager.start()