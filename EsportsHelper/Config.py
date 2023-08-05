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
from EsportsHelper.Stats import stats

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


def formatBoolean(variable):
    if isinstance(variable, str):
        if variable.lower() == "true":
            variable = True
        elif variable == "false":
            variable = False
        else:
            variable = False
    return variable


class Config:
    def __init__(self, configPath: str) -> None:
        try:
            configPath = findConfigFile(configPath)
            if configPath is None:
                log.error(_log("找不到配置文件"))
                print(_("找不到配置文件", color="red"))
                stats.info.append(_("找不到配置文件", color="red"))
                stats.status = _("错误", color="red")
                input(_log("按回车键退出"))
                os.kill(os.getpid(), 9)
            with open(configPath, "r", encoding='utf-8') as f:
                configFile = yaml.safe_load(f)
            self.version = "2.2.0"
            self.headless = configFile.get("headless", False)
            self.username = configFile.get("username", "账号用户名")
            self.password = configFile.get("password", "密码")
            self.delay = configFile.get("delay", 600)
            self.maxRunHours = configFile.get("maxRunHours", -1)
            self.disWatchMatches = configFile.get("disWatchMatches", [])
            self.connectorDropsUrl = configFile.get("connectorDropsUrl", "")
            self.connectorTest = configFile.get("connectorTest", False)
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
            self.autoSleep = configFile.get("autoSleep", True)
            self.nickName = configFile.get("nickName", self.username)
            self.onlyWatchMatches = configFile.get("onlyWatchMatches", [])
            self.maxStream = configFile.get("maxStream", 4)
            self.exportDrops = configFile.get("exportDrops", False)
            self.briefLogLength = configFile.get("briefLogLength", 10)
            self.mode = configFile.get("mode", "safe")
            self.arm64 = configFile.get("arm64", False)
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
            stats.info.append(_("配置文件格式错误", color="red"))
            stats.info.append(_("请检查是否存在中文字符以及冒号后面应该有一个空格", color="red"))
            stats.info.append(_("配置路径如有单斜杠请改为双斜杠", color="red"))
            stats.status = _("错误", color="red")
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
            stats.info.append(_("配置文件错误", color="red"))
            stats.status = _("错误", color="red")
            input(_log("按回车键退出"))
            os.kill(os.getpid(), 9)

    def format(self):
        """
        Formats the instance variables according to certain rules.

        Raises:
        - ValueError: If an invalid format is given for certain variables.
        """
        if isinstance(self.language, str):
            if self.language not in ["zh_CN", "en_US", "zh_TW", "es_ES"]:
                self.language = "zh_CN"
                stats.info.append(_("语言配置错误,已恢复zh_CN默认值", color="red"))
                log.error(_log("语言配置错误,已恢复zh_CN默认值"))
        self.disWatchMatches = [match.lower() for match in self.disWatchMatches if match != ""]

        if self.userDataDir == "" and self.username == "账号用户名" or self.password == "密码":
            log.error(_log("配置文件中没有账号密码信息"))
            stats.info.append(_("配置文件中没有账号密码信息", color="red"))

        self.exportDrops = formatBoolean(self.exportDrops)
        self.headless = formatBoolean(self.headless)
        self.desktopNotify = formatBoolean(self.desktopNotify)
        self.closeStream = formatBoolean(self.closeStream)
        self.debug = formatBoolean(self.debug)
        self.countDrops = formatBoolean(self.countDrops)
        self.ignoreBroadCast = formatBoolean(self.ignoreBroadCast)
        self.autoSleep = formatBoolean(self.autoSleep)
        self.connectorTest = formatBoolean(self.connectorTest)
        self.arm64 = formatBoolean(self.arm64)

        if isinstance(self.delay, str):
            try:
                self.delay = int(self.delay)
            except ValueError:
                stats.info.append(_("检查间隔配置错误,已恢复默认值", color="red"))
                log.error(_log("检查间隔配置错误,已恢复默认值"))
                self.delay = 600

        if not isinstance(self.platForm, str):
            self.platForm = "windows"
        else:
            self.platForm = self.platForm.lower()
            if self.platForm not in ["windows", "linux"]:
                self.platForm = "windows"

        if self.sleepPeriod != [""]:
            if isinstance(self.sleepPeriod, list):
                afterFormat = []
                for period in self.sleepPeriod:
                    sleepPeriod = period.split("-")
                    if len(sleepPeriod) != 2:
                        stats.info.append(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                        log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                        afterFormat.append("")
                    else:
                        try:
                            if int(sleepPeriod[0]) > int(sleepPeriod[1]):
                                stats.info.append(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                                log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                                afterFormat.append("")
                            elif int(sleepPeriod[0]) < 0 or int(sleepPeriod[1]) > 24:
                                stats.info.append(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                                log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                                afterFormat.append("")
                            else:
                                afterFormat.append(period)
                        except ValueError:
                            stats.info.append(f'{period} {_("睡眠时间段配置错误,已恢复默认值", color="red")}')
                            log.error(_log(f'{period} {_log("睡眠时间段配置错误,已恢复默认值")}'))
                            afterFormat.append("")
                self.sleepPeriod = afterFormat
            else:
                stats.info.append(_("睡眠时间段配置错误,已恢复默认值", color="red"))
                log.error(_log("睡眠时间段配置错误,已恢复默认值"))
                self.sleepPeriod = [""]
        if isinstance(self.maxRunHours, str):
            if self.maxRunHours == "":
                self.maxRunHours = -1
            else:
                try:
                    self.maxRunHours = int(self.maxRunHours)
                except ValueError:
                    stats.info.append(_("最大运行时间配置错误,已恢复默认值", color="red"))
                    log.error(_log("最大运行时间配置错误,已恢复默认值"))
                    self.maxRunHours = -1
        if isinstance(self.maxStream, str):
            if self.maxRunHours == "":
                self.maxRunHours = 4
            else:
                try:
                    self.maxStream = int(self.maxStream)
                except ValueError:
                    stats.info.append(_("最大同时观看数配置错误,已恢复默认值4", color="red"))
                    log.error(_log("最大同时观看数配置错误,已恢复默认值4"))
                    self.maxStream = 4
        elif isinstance(self.maxStream, int):
            if self.maxStream < 1:
                stats.info.append(_("最大同时观看数配置错误,已恢复默认值4", color="red"))
                log.error(_log("最大同时观看数配置错误,已恢复默认值4"))
                self.maxStream = 4
        if isinstance(self.briefLogLength, str):
            if self.briefLogLength == "":
                self.briefLogLength = 10
            else:
                try:
                    self.briefLogLength = int(self.briefLogLength)
                except ValueError:
                    stats.info.append(_("简略日志长度配置错误,已恢复默认值10", color="red"))
                    log.error(_log("简略日志长度配置错误,已恢复默认值10"))
                    self.briefLogLength = 10
        elif isinstance(self.maxStream, int):
            if self.briefLogLength < 1:
                stats.info.append(_("简略日志长度配置错误,已恢复默认值10", color="red"))
                log.error(_log("简略日志长度配置错误,已恢复默认值10"))
                self.briefLogLength = 10
        if self.delay <= 120:
            stats.info.append(_("检查间隔过短,建议延长.", color="yellow"))
            log.error(_log("检查间隔过短,建议延长."))

        if not isinstance(self.proxy, str):
            stats.info.append(_("代理配置错误,已恢复默认值", color="red"))
            log.error(_log("代理配置错误,已恢复默认值"))
            stats.info.append(_("代理配置错误,已恢复默认值", color="red"))
            self.proxy = ""
        if not isinstance(self.chromePath, str):
            stats.info.append(_("chrome路径配置错误,已恢复默认值", color="red"))
            log.error(_log("chrome路径配置错误,已恢复默认值"))
            self.chromePath = ""
        if not isinstance(self.userDataDir, str):
            stats.info.append(_("用户数据userDataDir路径配置错误,已恢复默认值", color="red"))
            log.error(_log("用户数据userDataDir路径配置错误,已恢复默认值"))
            self.userDataDir = ""
        if isinstance(self.notifyType, str):
            if self.notifyType not in ["all", "drops", "error"]:
                stats.info.append(_("通知类型配置错误,已恢复默认值", color="red"))
                log.error(_log("通知类型配置错误,已恢复默认值"))
                self.notifyType = "all"
        else:
            stats.info.append(_("通知类型配置错误,已恢复默认值", color="red"))
            log.error(_log("通知类型配置错误,已恢复默认值"))
            self.notifyType = "all"
        if self.countDrops is False and self.connectorDropsUrl != "":
            stats.info.append(_("提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭", color="yellow"))
            log.warning(_log("提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭"))

        if self.nickName == "":
            self.nickName = self.username

        self.onlyWatchMatches = [match.lower() for match in self.onlyWatchMatches if match != ""]
        if self.onlyWatchMatches and self.disWatchMatches:
            self.disWatchMatches = []
            stats.info.append(_("只看模式已开启,已忽略不看模式配置", color="yellow"))
            log.warning(_log("只看模式已开启,已忽略不看模式配置"))

        if not isinstance(self.mode, str):
            self.mode = "normal"
            stats.info.append(_("模式配置错误,已恢复默认值normal", color="yellow"))
            log.error(_log("模式配置错误,已恢复默认值normal"))
        else:
            if self.mode not in ["normal", "safe"]:
                self.mode = "normal"
                stats.info.append(_("模式配置错误,已恢复默认值normal", color="yellow"))
                log.error(_log("模式配置错误,已恢复默认值normal"))
        if self.onlyWatchMatches or self.disWatchMatches:
            self.mode = "normal"
            log.info(_log("已配置观看赛区,模式切换成默认模式."))



parser = argparse.ArgumentParser(
    prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                    help='config file path')
args = parser.parse_args()
config = Config(args.configPath)
