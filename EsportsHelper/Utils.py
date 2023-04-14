import sys
from time import sleep, strftime
from traceback import format_exc, print_exc

import requests
from retrying import retry
from urllib3.exceptions import MaxRetryError

from EsportsHelper import Config
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from rich import print


class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, e):
        if self.config.desktopNotify:
            try:
                notification.notify(
                    title="小傻瓜，出事啦！",
                    message=f"错误信息：{e}",
                    timeout=30
                )
                print("错误提醒发送成功")
                log.info("错误提醒发送成功")
            except Exception as e:
                print("错误提醒发送失败")
                log.error("错误提醒发送失败")
                log.error(format_exc())
        if self.config.connectorDropsUrl != "":
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
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
                        "title": "发生错误 停止获取Drop",
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
                        "text": f"发生错误停止获取Drop{e}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                else:
                    params = {
                        "text": f"发生错误停止获取Drop{e}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                log.info(">_< 异常提醒成功")
                print("异常提醒成功")
            except Exception as e:
                print("异常提醒失败")
                log.error("异常提醒失败")
                log.error(format_exc())

    def debugScreen(self, driver, lint=""):
        try:
            if self.config.debug:
                log.info(f"DebugScreen: {lint}存储成功")
                driver.save_screenshot(f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
        except Exception:
            log.error("DebugScreen: 截图失败")
            log.error(format_exc())


def info():
    print("[green]=========================================================")
    print(
        f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
    print("[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
    print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
    print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
    print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
    print("[green]====[/green] 如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. [green]====[/green]")
    print("[green]=========================================================")
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
    log.info("------程序退出------")
    sys.exit()


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
        print(f"[red]〒.〒 获取重定向文件失败,请检查网络是否能连上github,稍后重试[/red]")
        input("按任意键退出")
        sysQuit(e="获取文件失败")


# 从url中获取比赛赛区名
def getMatchName(url) -> str:
    splitUrl = url.split('/')
    if splitUrl[-2] != "live":
        match = splitUrl[-2]
    else:
        match = splitUrl[-1]
    if "cblol-brazil" == match:
        match = "cblol"
    elif "ljl-japan" == match:
        match = "ljl"
    return match


# 重复尝试获取网页最多4次，等待时间以2分钟为基数，每次递增2分钟
@retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
def getLolesportsWeb(driver):
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    except Exception:
        print("[red]Q_Q 获取Lolesports网页失败,重试中...[/red]")
        log.error("Q_Q 获取Lolesports网页失败,重试中...")
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")