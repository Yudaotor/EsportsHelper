import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

FILE_SIZE = 1024 * 1024 * 100
BACKUP_COUNT = 5
PROGRAM_NAME = "EsportsHelper"
GITHUB_ADDRESS = "https://github.com/Yudaotor/EsportsHelper"


class Logger:
    @staticmethod
    def createLogger(log_path=Path("./logs/programs")):
        """创建并返回一个Logger实例。

        Args:
            log_path (Path, optional): 日志文件保存路径. Defaults to Path("./logs/programs").

        Returns:
            logging.Logger: Logger实例.
        """
        log_path.mkdir(parents=True, exist_ok=True)
        Path("./logs/pics").mkdir(parents=True, exist_ok=True)
        level = logging.INFO
        fileHandler = RotatingFileHandler(
            log_path / f"{PROGRAM_NAME}{time.strftime('%b-%d-%H-%M')}.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )

        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=level,
            handlers=[fileHandler],
        )
        log = logging.getLogger(PROGRAM_NAME)
        log.info("-" * 50)
        log.info("----------- Program started   ---------------")
        log.info("----------- Open Source on github   ---------------")
        log.info(f"----- Address: {GITHUB_ADDRESS} -------")
        log.info("----------- Please give me a star,Thanks(*^_^*) ---------------")
        log.info("-" * 50)
        return log


log = Logger().createLogger()
