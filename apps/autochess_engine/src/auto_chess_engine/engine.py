# the Chess engine
# NOTE this file is incomplete, waiting for server and engine specs

import argparse

from logging import getLogger, disable
from .log.logger import setup_logger
from .config import Config

logger = getLogger(__name__)

CMD_LIST = ['self', 'opt', 'eval', 'sl', 'uci']

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", help="what to do", choices=CMD_LIST)
    parser.add_argument("--new", help="bootstrap the engine from new model", action="store_true")
    parser.add_argument("--type", help="use normal setting", default="mini");
    parser.add_argument("--total-step", help="set TrainerConfig.start_total_steps", type=int)

    return parser


def setup(config: Config, args):
    config.opts.new = args.new
    if args.total_step is not None:
        config.trainer.start_total_steps = args.total_step
    config.resource.create_directories()
    setup_logger(config.resource.main_log_path)


def start():
    # Starts the engine based on the command line args
    parser = create_parser()
    args = parser.parse_args()
    config_type = args.type

    if args.cmd == 'uci':
        disable(9999999)

    config = Config(config_type=config_type)
    setup(config, args)

    logger.info(f"config type : {config_type}")

    if args.cmd == 'self':
        from .worker import self_play
        return self_play.start(config)