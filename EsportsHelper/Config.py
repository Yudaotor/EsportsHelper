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
                self.maxRunHours = config.get("maxRunHours", -1)
                self.disWatchMatches = config.get("disWatchMatches", [])
                self.connectorDropsUrl = config.get("connectorDropsUrl", "")
                self.platForm = config.get("platForm", "windows")
                self.debug = config.get("debug", False)
                self.proxy = config.get("proxy", "")
                self.desktopNotify = config.get("desktopNotify", False)
                self.closeStream = config.get("closeStream", False)
                self.sleepPeriod = config.get("sleepPeriod", "")
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
            try:
                self.delay = int(self.delay)
            except ValueError:
                self.delay = 600

        if not isinstance(self.platForm, str):
            self.platForm = "windows"
        else:
            self.platForm = self.platForm.lower()
            if self.platForm not in ["windows", "linux"]:
                self.platForm = "windows"
        if isinstance(self.desktopNotify, str):
            if self.desktopNotify == "True" or self.desktopNotify == "true":
                self.desktopNotify = True
            elif self.desktopNotify == "False" or self.desktopNotify == "false":
                self.desktopNotify = False
            else:
                self.desktopNotify = False
        if isinstance(self.closeStream, str):
            if self.closeStream == "True" or self.closeStream == "true":
                self.closeStream = True
            elif self.closeStream == "False" or self.closeStream == "false":
                self.closeStream = False
            else:
                self.closeStream = False
        if isinstance(self.sleepPeriod, str):
            sleepPeriod = self.sleepPeriod.split("-")
            if len(sleepPeriod) != 2:
                self.sleepPeriod = ""
            else:
                if sleepPeriod[0] > sleepPeriod[1]:
                    self.sleepPeriod = ""
                elif sleepPeriod[0] < "0" or sleepPeriod[1] > "24":
                    self.sleepPeriod = ""
        else:
            self.sleepPeriod = ""
        if isinstance(self.maxRunHours, str):
            if self.maxRunHours == "":
                self.maxRunHours = -1
            else:
                try:
                    self.maxRunHours = int(self.maxRunHours)
                except ValueError:
                    self.maxRunHours = -1
        if isinstance(self.debug, str):
            if self.debug == "True" or self.debug == "true":
                self.debug = True
            elif self.debug == "False" or self.debug == "false":
                self.debug = False
            else:
                self.debug = False
        if not isinstance(self.proxy, str):
            self.proxy = ""

    def __findConfigFile(self, configPath):
        configPath = Path(configPath)
        if configPath.exists():
            return configPath


config = ""
