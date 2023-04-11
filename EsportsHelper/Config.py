from pathlib import Path
from traceback import format_exc, print_exc

import yaml
from rich import print
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from EsportsHelper.Utils import sysQuit


class Config:
    def __init__(self, log, configPath: str) -> None:
        self.log = log
        try:
            configPath = self.__findConfigFile(configPath)
            with open(configPath, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.headless = config.get("headless", False)
                self.username = config.get("username", "账号用户名")
                self.password = config.get("password", "密码")
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
                self.countDrops = config.get("countDrops", False)
                self.chromePath = config.get("chromePath", "")
                self.format()

        except FileNotFoundError as ex:
            log.error("配置文件找不到")
            print("[red]配置文件找不到")
            input("按任意键退出")
            sysQuit(None, "配置文件找不到")
        except (ParserError, KeyError, ScannerError) as ex:
            log.error("配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格")
            log.error(format_exc())
            print("[red]配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格")
            input("按任意键退出")
            sysQuit(None, "配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格")
        except Exception as ex:
            input("按任意键退出")
            sysQuit(None, "读取config文件时发生错误")
            log.error(format_exc())

    def format(self):
        while "" in self.disWatchMatches:
            self.disWatchMatches.remove("")

        if self.username == "账号用户名" or self.password == "密码":
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
                print("[red]检查间隔配置错误,已恢复默认值")
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

        if self.sleepPeriod != "":
            if isinstance(self.sleepPeriod, str):
                sleepPeriod = self.sleepPeriod.split("-")
                if len(sleepPeriod) != 2:
                    print("[red]睡眠时间段配置错误,已恢复默认值")
                    self.sleepPeriod = ""
                else:
                    try:
                        if int(sleepPeriod[0]) > int(sleepPeriod[1]):
                            print("[red]睡眠时间段配置错误,已恢复默认值")
                            self.sleepPeriod = ""
                        elif sleepPeriod[0] < "0" or sleepPeriod[1] > "24":
                            print("[red]睡眠时间段配置错误,已恢复默认值")
                            self.sleepPeriod = ""
                    except ValueError:
                        print("[red]睡眠时间段配置错误,已恢复默认值")
                        self.sleepPeriod = ""
            else:
                print("[red]睡眠时间段配置错误,已恢复默认值")
                self.sleepPeriod = ""
        if isinstance(self.maxRunHours, str):
            if self.maxRunHours == "":
                self.maxRunHours = -1
            else:
                try:
                    self.maxRunHours = int(self.maxRunHours)
                except ValueError:
                    print("[red]最大运行时间配置错误,已恢复默认值")
                    self.maxRunHours = -1
        if isinstance(self.debug, str):
            if self.debug == "True" or self.debug == "true":
                self.debug = True
            elif self.debug == "False" or self.debug == "false":
                self.debug = False
            else:
                self.debug = False
        if not isinstance(self.proxy, str):
            print("[red]代理配置错误,已恢复默认值")
            self.proxy = ""
        if isinstance(self.countDrops, str):
            if self.countDrops == "True" or self.countDrops == "true":
                self.countDrops = True
            elif self.countDrops == "False" or self.countDrops == "false":
                self.countDrops = False
            else:
                self.countDrops = False
        if not isinstance(self.chromePath, str):
            print("[red]chrome路径配置错误,已恢复默认值")
            self.chromePath = ""

    def __findConfigFile(self, configPath):
        configPath = Path(configPath)
        if configPath.exists():
            return configPath


