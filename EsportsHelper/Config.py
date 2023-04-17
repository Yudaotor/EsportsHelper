from pathlib import Path
from traceback import format_exc, print_exc

import yaml
from rich import print
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from EsportsHelper.Utils import _, _log


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
                self.countDrops = config.get("countDrops", True)
                self.chromePath = config.get("chromePath", "")
                self.userDataDir = config.get("userDataDir", "")
                self.ignoreBoardCast = config.get("ignoreBoardCast", True)
                self.language = config.get("language", "zh_CN")
                self.format()

        except FileNotFoundError:
            log.error(_log("配置文件找不到", lang=self.language))
            print(_("配置文件找不到", color="red", lang=self.language))
            input(_log("按任意键退出", lang=self.language))
        except (ParserError, KeyError, ScannerError):
            log.error(_log("配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠", lang=self.language))
            log.error(format_exc())
            print(_("配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠", color="red", lang=config.language))
            input(_log("按任意键退出", lang=self.language))
        except Exception:
            input(_log("按任意键退出", lang=self.language))
            log.error(format_exc())

    def format(self):
        if isinstance(self.language, str):
            if self.language not in ["zh_CN", "en_US"]:
                self.language = "zh_CN"
                print(_("语言配置错误,已恢复zh_CN默认值", color="red", lang=self.language))
        while "" in self.disWatchMatches:
            self.disWatchMatches.remove("")

        if self.userDataDir == "" and self.username == "账号用户名" or self.password == "密码":
            self.log.error(_log("配置文件中没有账号密码信息", lang=self.language))
            print(_("配置文件中没有账号密码信息", color="red", lang=self.language))

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
                print(_("检查间隔配置错误,已恢复默认值", color="red", lang=self.language))
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
                    print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                    self.sleepPeriod = ""
                else:
                    try:
                        if int(sleepPeriod[0]) > int(sleepPeriod[1]):
                            print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                            self.sleepPeriod = ""
                        elif sleepPeriod[0] < "0" or sleepPeriod[1] > "24":
                            print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                            self.sleepPeriod = ""
                    except ValueError:
                        print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                        self.sleepPeriod = ""
            else:
                print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                self.sleepPeriod = ""
        if isinstance(self.maxRunHours, str):
            if self.maxRunHours == "":
                self.maxRunHours = -1
            else:
                try:
                    self.maxRunHours = int(self.maxRunHours)
                except ValueError:
                    print(_("最大运行时间配置错误,已恢复默认值", color="red", lang=self.language))
                    self.maxRunHours = -1
        if isinstance(self.debug, str):
            if self.debug == "True" or self.debug == "true":
                self.debug = True
            elif self.debug == "False" or self.debug == "false":
                self.debug = False
            else:
                self.debug = False
        if not isinstance(self.proxy, str):
            print(_("代理配置错误,已恢复默认值", color="red", lang=self.language))
            self.proxy = ""
        if isinstance(self.countDrops, str):
            if self.countDrops == "True" or self.countDrops == "true":
                self.countDrops = True
            elif self.countDrops == "False" or self.countDrops == "false":
                self.countDrops = False
            else:
                self.countDrops = False
        if not isinstance(self.chromePath, str):
            print(_("chrome路径配置错误,已恢复默认值", color="red", lang=self.language))
            self.chromePath = ""
        if not isinstance(self.userDataDir, str):
            print(_("用户数据userDataDir路径配置错误,已恢复默认值", color="red", lang=self.language))
            self.userDataDir = ""
        if isinstance(self.ignoreBoardCast, str):
            if self.ignoreBoardCast == "True" or self.ignoreBoardCast == "true":
                self.ignoreBoardCast = True
            elif self.ignoreBoardCast == "False" or self.ignoreBoardCast == "false":
                self.ignoreBoardCast = False
            else:
                self.ignoreBoardCast = True

    def __findConfigFile(self, configPath):
        configPath = Path(configPath)
        if configPath.exists():
            return configPath


