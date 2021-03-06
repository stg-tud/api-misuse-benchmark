#!/usr/bin/env python3
import calendar
import logging.handlers
import platform
import sys
from datetime import datetime
from os import makedirs
from os.path import join, exists

from requirements import RequirementsCheck
from tasks.configurations.configurations import get_task_configuration
from tasks.task_runner import TaskRunner
from utils import config_util, logging_colorization
from utils.data_entity_lists import DataEntityLists
from utils.dataset_util import get_white_list


class Benchmark:
    def __init__(self, config):
        self.config = config

        white_list = []
        black_list = []
        if 'white_list' in config:
            white_list.extend(config.white_list)
        if 'black_list' in config:
            black_list.extend(config.black_list)

        if 'datasets' in config:
            for dataset in config.datasets:
                white_list.extend(get_white_list(config.datasets_file_path, dataset))

        self.data_entity_lists = DataEntityLists(white_list, black_list)

    def run(self) -> None:
        RequirementsCheck()
        task_configuration = get_task_configuration(self.config)
        initial_parameters = [self.data_entity_lists]
        runner = TaskRunner(task_configuration)
        runner.run(*initial_parameters)


config = config_util.get_config(sys.argv)
now = datetime.utcnow()
config.run_timestamp = calendar.timegm(now.timetuple())

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logging_colorization.register_levelcolor_replacement_field(handler)
formatter = logging.Formatter("[%(levelcolor)s%(levelname)-7s%(resetcolor)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

LOG_DIR = "logs"
if not exists(LOG_DIR):
    makedirs(LOG_DIR)
log_name = datetime.now().strftime("run_%Y%m%d_%H%M%S") + ".log"
handler = logging.FileHandler(join(LOG_DIR, log_name), encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("Starting benchmark...")
logger.debug("- Arguments           = %r", sys.argv)
logger.debug("- Configuration       :")
for key in config.__dict__:
    logger.debug("    - %s = %r", key.ljust(15), config.__dict__[key])

benchmark = Benchmark(config)
try:
    benchmark.run()
except BaseException as e:
    logger.error("{}: {}".format(type(e).__name__, str(e)))
    logger.debug("Full exception: ", exc_info=True)
    exit(1)
