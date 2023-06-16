import argparse
import os
from pathlib import Path
from traceback import format_exc
import yaml
from rich import print
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from EsportsHelper.I18n import i18n
from EsportsHelper.Logger import delimiterLine
from EsportsHelper.Logger import log
_ = i18n.getText
_log = i18n.getLog


def findConfigFile(configPath):
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


class Config:
    def __init__(self, configPath: str) -> None:
        try:
            configPath = findConfigFile(configPath)
            if configPath is None:
                log.error(_log("找不到配置文件"))
                print(_("找不到配置文件", color="red"))
                input(_log("按回车键退出"))
                os.kill(os.getpid(), 9)
            with open(configPath, "r", encoding='utf-8') as f:
                configFile = yaml.safe_load(f)
            self.version = "1.6.3"
            self.headless = configFile.get("headless", False)
            self.username = configFile.get("username", "账号用户名")
            self.password = configFile.get("password", "密码")
            self.delay = configFile.get("delay", 600)
            self.maxRunHours = configFile.get("maxRunHours", -1)
            self.disWatchMatches = configFile.get("disWatchMatches", [])
            self.connectorDropsUrl = configFile.get("connectorDropsUrl", "")
            self.platForm = configFile.get("platForm", "windows")
            self.debug = configFile.get("debug", False)
            self.proxy = configFile.get("proxy", "")
            self.desktopNotify = configFile.get("desktopNotify", False)
            self.closeStream = configFile.get("closeStream", False)
            self.sleepPeriod = configFile.get("sleepPeriod", [""])
            self.countDrops = configFile.get("countDrops", True)
            self.chromePath = configFile.get("chromePath", "")
            self.userDataDir = configFile.get("userDataDir", "")
            self.ignoreBroadCast = configFile.get("ignoreBroadCast", True)
            self.language = configFile.get("language", "zh_CN")
            self.notifyType = configFile.get("notifyType", "all")
            self.autoSleep = configFile.get("autoSleep", False)
            self.nickName = configFile.get("nickName", self.username)
            self.onlyWatchMatches = configFile.get("onlyWatchMatches", [])
            self.maxStream = configFile.get("maxStream", 3)
            self.exportDrops = configFile.get("exportDrops", False)
            self.format()
        except (ParserError, KeyError, ScannerError):
            log.error(_log('配置文件格式错误'))
            log.error(_log('请检查是否存在中文字符以及冒号后面应该有一个空格'))
            log.error(_log('配置路径如有单斜杠请改为双斜杠'))
            modifiedTrace = f"{50 * '+'}\n"
            lines = format_exc().splitlines()
            for line in lines:
                if "Stacktrace:" in line:
                    break
                modifiedTrace += line + '\n'
            log.error(modifiedTrace)
            print(_("配置文件格式错误", color="red"))
            print(_("请检查是否存在中文字符以及冒号后面应该有一个空格", color="red"))
            print(_("配置路径如有单斜杠请改为双斜杠", color="red"))
            input(_log("按回车键退出"))
            os.kill(os.getpid(), 9)
        except Exception:
            log.error(_log("配置文件错误"))
            modifiedTrace = f"{50 * '+'}\n"
            lines = format_exc().splitlines()
            for line in lines:
                if "Stacktrace:" in line:
                    break
                modifiedTrace += line + '\n'
            log.error(modifiedTrace)
            print(_("配置文件错误", color="red"))
            input(_log("按回车键退出"))
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
                print(_("语言配置错误,已恢复zh_CN默认值", color="red"))
                log.error(_log("语言配置错误,已恢复zh_CN默认值"))
                delimiterLine(color="red")
        self.disWatchMatches = [match.lower() for match in self.disWatchMatches if match != ""]

        if self.userDataDir == "" and self.username == "账号用户名" or self.password == "密码":
            log.error(_log("配置文件中没有账号密码信息"))
            print(_("配置文件中没有账号密码信息", color="red"))
            delimiterLine(color="red")

        if isinstance(self.headless, str):
            if self.headless == "True" or self.headless == "true":
                self.headless = True
            elif self.headless == "False" or self.headless == "false":
                self.headless = False
            else:
                self.headless = False

        if isinstance(self.exportDrops, str):
            if self.exportDrops == "True" or self.exportDrops == "true":
                self.exportDrops = True
            elif self.exportDrops == "False" or self.exportDrops == "false":
                self.exportDrops = False
            else:
                self.exportDrops = False

        if isinstance(self.delay, str):
            try:
                self.delay = int(self.delay)
            except ValueError:
                print(_("检查间隔配置错误,已恢复默认值", color="red"))
                log.error(_log("检查间隔配置错误,已恢复默认值"))
                delimiterLine(color="red")
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
                        print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                        log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                        delimiterLine(color="red")
                        afterFormat.append("")
                    else:
                        try:
                            if int(sleepPeriod[0]) > int(sleepPeriod[1]):
                                print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                                log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                                delimiterLine(color="red")
                                afterFormat.append("")
                            elif int(sleepPeriod[0]) < 0 or int(sleepPeriod[1]) > 24:
                                print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                                log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                                delimiterLine(color="red")
                                afterFormat.append("")
                            else:
                                afterFormat.append(period)
                        except ValueError:
                            print(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                            log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                            delimiterLine(color="red")
                            afterFormat.append("")
                self.sleepPeriod = afterFormat
            else:
                print(_("睡眠时间段配置错误,已恢复默认值", color="red"))
                log.error(_log("睡眠时间段配置错误,已恢复默认值"))
                delimiterLine(color="red")
                self.sleepPeriod = [""]
        if isinstance(self.maxRunHours, str):
            if self.maxRunHours == "":
                self.maxRunHours = -1
            else:
                try:
                    self.maxRunHours = int(self.maxRunHours)
                except ValueError:
                    print(_("最大运行时间配置错误,已恢复默认值", color="red"))
                    log.error(_log("最大运行时间配置错误,已恢复默认值"))
                    delimiterLine(color="red")
                    self.maxRunHours = -1
        if isinstance(self.maxStream, str):
            if self.maxRunHours == "":
                self.maxRunHours = 3
            else:
                try:
                    self.maxStream = int(self.maxStream)
                except ValueError:
                    print(_("最大同时观看数配置错误,已恢复默认值3", color="red"))
                    log.error(_log("最大同时观看数配置错误,已恢复默认值3"))
                    delimiterLine(color="red")
                    self.maxStream = 3
        elif isinstance(self.maxStream, int):
            if self.maxStream < 1:
                print(_("最大同时观看数配置错误,已恢复默认值3", color="red"))
                log.error(_log("最大同时观看数配置错误,已恢复默认值3"))
                delimiterLine(color="red")
                self.maxStream = 3
        if isinstance(self.debug, str):
            if self.debug == "True" or self.debug == "true":
                self.debug = True
            elif self.debug == "False" or self.debug == "false":
                self.debug = False
            else:
                self.debug = False
        if not isinstance(self.proxy, str):
            print(_("代理配置错误,已恢复默认值", color="red"))
            log.error(_log("代理配置错误,已恢复默认值"))
            delimiterLine(color="red")
            self.proxy = ""
        if isinstance(self.countDrops, str):
            if self.countDrops == "True" or self.countDrops == "true":
                self.countDrops = True
            elif self.countDrops == "False" or self.countDrops == "false":
                self.countDrops = False
            else:
                self.countDrops = False
        if not isinstance(self.chromePath, str):
            print(_("chrome路径配置错误,已恢复默认值", color="red"))
            log.error(_log("chrome路径配置错误,已恢复默认值"))
            delimiterLine(color="red")
            self.chromePath = ""
        if not isinstance(self.userDataDir, str):
            print(_("用户数据userDataDir路径配置错误,已恢复默认值", color="red"))
            log.error(_log("用户数据userDataDir路径配置错误,已恢复默认值"))
            delimiterLine(color="red")
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
                print(_("通知类型配置错误,已恢复默认值", color="red"))
                log.error(_log("通知类型配置错误,已恢复默认值"))
                delimiterLine(color="red")
                self.notifyType = "all"
        else:
            print(_("通知类型配置错误,已恢复默认值", color="red"))
            log.error(_log("通知类型配置错误,已恢复默认值"))
            delimiterLine(color="red")
            self.notifyType = "all"
        if isinstance(self.autoSleep, str):
            if self.autoSleep == "True" or self.autoSleep == "true":
                self.autoSleep = True
            elif self.autoSleep == "False" or self.autoSleep == "false":
                self.autoSleep = False
            else:
                self.autoSleep = False
        if self.countDrops is False and self.connectorDropsUrl != "":
            print(_("提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭", color="yellow"))
            log.warning(_log("提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭"))
            delimiterLine(color="red")

        if self.nickName == "":
            self.nickName = self.username

        self.onlyWatchMatches = [match.lower() for match in self.onlyWatchMatches if match != ""]
        if self.onlyWatchMatches and self.disWatchMatches:
            self.disWatchMatches = []
            print(_("只看模式已开启,已忽略不看模式配置", color="yellow"))
            log.warning(_log("只看模式已开启,已忽略不看模式配置"))
            delimiterLine(color="yellow")


parser = argparse.ArgumentParser(
    prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                    help='config file path')
args = parser.parse_args()
config = Config(args.configPath)
