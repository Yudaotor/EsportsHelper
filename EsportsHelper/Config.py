from pathlib import Path
from traceback import format_exc, print_exc

import yaml
from rich import print
from yaml.parser import ParserError


class Config:
    def __init__(self, log, configPath: str) -> None:
        self.log = log
        try:
            configPath = self.__findConfigFile(configPath)
            with open(configPath, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.headless = config.get("headless", False)
                self.username = config.get("username", "NoUsername")
                self.password = config.get("password", "NoPassword")
                self.delay = config.get("delay", 600)
                self.maxRunHours = config.get("runHours", -1)
                self.disWatchMatches = config.get("disWatchMatches", [])
                self.connectorDropsUrl = config.get("connectorDropsUrl", "")
                self.platForm = config.get("platForm", "windows")
                self.debug = config.get("debug", False)
                self.proxy = config.get("proxy", "")
                self.format()

        except FileNotFoundError as ex:
            log.error("配置文件找不到")
            print("[red]配置文件找不到")
        except (ParserError, KeyError) as ex:
            log.error("配置文件格式错误")
            print("[red]配置文件格式错误")
        except Exception as ex:
            print_exc()
            self.log.error(format_exc())

    def format(self):
        while "" in self.disWatchMatches:
            self.disWatchMatches.remove("")
        if self.username == "NoUsername" or self.password == "NoPassword":
            self.log.error("配置文件中没有账号密码信息")
            print("[red]配置文件中没有账号密码信息")
        if isinstance(self.headless, str):
            if self.headless == "True" or self.headless == "true":
                self.headless = True
            elif self.headless == "False" or self.headless == "false":
                self.headless = False
            else:
                self.headless = False
        if isinstance(self.delay, str):
            self.delay = int(self.delay)
        if not isinstance(self.platForm, str):
            self.platForm = "windows"
        else:
            self.platForm = self.platForm.lower()
            if self.platForm not in ["windows", "linux"]:
                self.platForm = "windows"

    def __findConfigFile(self, configPath):
        configPath = Path(configPath)
        if configPath.exists():
            return configPath
