import sys
from time import sleep, strftime
from traceback import format_exc, print_exc
import requests
from urllib3.exceptions import MaxRetryError

from EsportsHelper import Config
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from rich import print

def print_green(text):
    print("\033[32m{}\033[0m".format(text))

def print_red(text):
    print("\033[31m{}\033[0m".format(text))

def print_yellow(text):
    print("\033[33m{}\033[0m".format(text))
class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, e):
        if self.config.desktopNotify:
            try:
                notification.notify(
                    title="Something happaned",
                    message=f"Error{e}",
                    timeout=30
                )
                print("Notification sent sucessfully")
                log.info("Notification sent sucessfully")
            except Exception as e:
                print("Failed to send notification")
                log.error("Failed to send notification")
                log.error(format_exc())
        if self.config.connectorDropsUrl != "":
            s = requests.session()
            s.keep_alive = False  # Turn off excess connection
            try:
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "发生错误停止获取Drop",
                            "title": f"{e}",
                            "picUrl": f"",
                            "messageUrl": ""
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "An error occurred. Work stopped.",
                        "description": f"{e}",
                        "image": {"url": f""},
                        "thumbnail": {"url": f""},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"An error occurred. Work stopped. {e}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                else:
                    params = {
                        "text": f"An error occurred. Work stopped. {e}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                log.info(">_< 异常提醒成功")
                print("异常提醒成功")
            except Exception as e:
                print("异常提醒失败")
                log.error("异常提醒失败")
                log.error(format_exc())


def info():
    print_green("=========================================================")
    print(
        f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
    print_green("============ 本程序开源于github链接地址如下: [green]============[/green]")
    print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
    print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
    print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
    print("[green]====[/green] 如需关闭请勿直接右上角×关闭，请按Ctrl+C来关闭. [green]====[/green]")
    print_green("[green]=========================================================")
    print()
    VersionManager.checkVersion()


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg):
    try:
        notification.notify(
            title="小傻瓜，掉寶啦！",
            message=f"通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
            timeout=30
        )
        log.info("桌面提醒成功！")
    except Exception as e:
        log.error("桌面提醒失败！")
        log.error(format_exc())


def sysQuit(driver=None, e=None):
    sleep(3)
    if driver:
        driver.quit()
    log.error(e)
    log.info("[red]------程序退出------")
    sys.exit()


def debugScreen(driver, lint=""):
    try:
        if Config.config.debug:
            log.info(f"DebugScreen: {lint}存储成功")
            driver.save_screenshot(f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
    except Exception as e:
        log.error("DebugScreen: 截图失败")
        log.error(format_exc())


def downloadOverrideFile():
    try:
        OVERRIDES = {}
        req = requests.session()
        headers = {'Content-Type': 'text/plain; charset=utf-8',
                   'Connection': 'close'}
        remoteOverrideFile = req.get(
            "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
        if remoteOverrideFile.status_code == 200:
            override = remoteOverrideFile.text.split(",")
            first = True
            for o in override:
                temp = o.split("|")
                if len(temp) == 2:
                    if first:
                        first = False
                    else:
                        temp[0] = temp[0][1:]
                    OVERRIDES[temp[0]] = temp[1]
            return OVERRIDES
        else:
            log.error("下载override文件失败")
            input("按任意键退出")
            sys.exit()
    except MaxRetryError:
        log.error("获取文件失败, 请稍等再试")
        print(f"[red]〒.〒 获取文件失败, 请稍等再试[/red]")
        input("按任意键退出")
        sysQuit(e="获取文件失败")
    except Exception as ex:
        print_exc()
        log.error("获取文件失败")
        print(f"[red]〒.〒 获取文件失败,请检查网络是否能连上github[/red]")
        input("按任意键退出")
        sysQuit(e="获取文件失败")
