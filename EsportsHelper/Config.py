import os
from pathlib import Path
from traceback import format_exc

import yaml
from EsportsHelper.Utils import _, _log
from rich import print
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class Config:
    def __init__(self, log, configPath: str) -> None:
        self.log = log
        try:
            configPath = self.__findConfigFile(configPath)
            if configPath is None:
                log.error("Can't find config file")
                print("Can't find config file")
                input("Press Enter to exit")
                os.kill(os.getpid(), 9)
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
            self.sleepPeriod = config.get("sleepPeriod", [""])
            self.countDrops = config.get("countDrops", True)
            self.chromePath = config.get("chromePath", "")
            self.userDataDir = config.get("userDataDir", "")
            self.ignoreBroadCast = config.get("ignoreBroadCast", True)
            self.language = config.get("language", "zh_CN")
            self.notifyType = config.get("notifyType", "all")
            self.autoSleep = config.get("autoSleep", False)
            self.nickName = config.get("nickName", self.username)
            self.format()
        except (ParserError, KeyError, ScannerError):
            log.error("Configuration file format error.\nPlease check if there is single space after colons.\nChange single slash to double in configuration path if there are any.")
            log.error(format_exc())
            print("Configuration file format error.\nPlease check if there is single space after colons.\nChange single slash to double in configuration path if there are any.")
            input("Press Enter to exit")
            os.kill(os.getpid(), 9)
        except Exception:
            log.error("Config file error")
            log.error(format_exc())
            print("Config file error")
            input("Press Enter to exit")
            os.kill(os.getpid(), 9)

    def format(self):
        """
        Formats the instance variables according to certain rules.

        Raises:
        - ValueError: If an invalid format is given for certain variables.
        """
        if isinstance(self.language, str):
            if self.language not in ["zh_CN", "en_US", "zh_TW"]:
                self.language = "zh_CN"
                print(_("语言配置错误,已恢复zh_CN默认值", color="red", lang=self.language))
        self.disWatchMatches = [match.lower() for match in self.disWatchMatches if match != ""]

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

        if self.sleepPeriod != [""]:
            if isinstance(self.sleepPeriod, list):
                afterFormat = []
                for period in self.sleepPeriod:
                    sleepPeriod = period.split("-")
                    if len(sleepPeriod) != 2:
                        print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language)}')
                        afterFormat.append("")
                    else:
                        try:
                            if int(sleepPeriod[0]) > int(sleepPeriod[1]):
                                print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language)}')
                                afterFormat.append("")
                            elif int(sleepPeriod[0]) < 0 or int(sleepPeriod[1]) > 24:
                                print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language)}')
                                afterFormat.append("")
                            else:
                                afterFormat.append(period)
                        except ValueError:
                            print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language)}')
                            afterFormat.append("")
                self.sleepPeriod = afterFormat
            else:
                print(_("睡眠时间段配置错误,已恢复默认值", color="red", lang=self.language))
                self.sleepPeriod = [""]
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
            print(_("用户数据userDataDir路径配置错误,已恢复默认值",
                    color="red", lang=self.language))
            self.userDataDir = ""
        if isinstance(self.ignoreBroadCast, str):
            if self.ignoreBroadCast == "True" or self.ignoreBroadCast == "true":
                self.ignoreBroadCast = True
            elif self.ignoreBroadCast == "False" or self.ignoreBroadCast == "false":
                self.ignoreBroadCast = False
            else:
                self.ignoreBroadCast = True
        if isinstance(self.notifyType, str):
            if self.notifyType not in ["all", "drops", "error"]:
                print(_("通知类型配置错误,已恢复默认值", color="red", lang=self.language))
                self.notifyType = "all"
        else:
            print(_("通知类型配置错误,已恢复默认值", color="red", lang=self.language))
            self.notifyType = "all"
        if isinstance(self.autoSleep, str):
            if self.autoSleep == "True" or self.autoSleep == "true":
                self.autoSleep = True
            elif self.autoSleep == "False" or self.autoSleep == "false":
                self.autoSleep = False
            else:
                self.autoSleep = False
        if self.countDrops is False and self.connectorDropsUrl != "":
            print(_("提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭", color="yellow", lang=self.language))

        if self.nickName == "":
            self.nickName = self.username

    def __findConfigFile(self, configPath):
        """Find the configuration file at the given path.

        Args:
            configPath (str): The path to the configuration file.

        Returns:
            Optional[Path]: The path to the configuration file if it exists, else None.
        """
        configPath = Path(configPath)
        if configPath.exists():
            return configPath
        else:
            return None
