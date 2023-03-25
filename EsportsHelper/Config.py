import traceback
from pathlib import Path
from yaml.parser import ParserError
from rich import print
import yaml


class Config:
    def __init__(self, log, configPath: str) -> None:
        self.log = log
        try:
            configPath = self.__findConfig(configPath)
            with open(configPath, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.headless = config.get("headless", False)
                self.username = config.get("username", "NoUsername")
                self.password = config.get("password", "NoPassword")
                self.delay = config.get("delay", 600)
                self.disWatchMatches = config.get("disWatchMatches", [])
                if self.username == "NoUsername" or self.password == "NoPassword":
                    log.error("配置文件中没有账号密码")
                    print("[red]配置文件中没有账号密码")
                if isinstance(self.headless, str):
                    if self.headless == "True" or self.headless == "true":
                        self.headless = True
                    elif self.headless == "False" or self.headless == "false":
                        self.headless = False
                if isinstance(self.delay, str):
                    self.delay = int(self.delay)
        except FileNotFoundError as ex:
            log.error("配置文件找不到")
            print("[red]配置文件找不到")
            raise ex
        except (ParserError, KeyError) as ex:
            log.error("配置文件格式错误")
            print("[red]配置文件格式错误")
            raise ex
        except Exception as ex:
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            raise ex

    def __findConfig(self, configPath):
        configPath = Path(configPath)
        if configPath.exists():
            return configPath
