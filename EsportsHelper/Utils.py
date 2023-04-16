import sys
from time import sleep, strftime
from traceback import format_exc, print_exc

import requests
from retrying import retry
from urllib3.exceptions import MaxRetryError
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from rich import print

i18n = {"눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开\n按任意键退出...": "1",
        "눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试\n按任意键退出...": "2",
        "눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用\n按任意键退出...": "3",
        "Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...": "4",
        "눈_눈 自动登录失败,检查网络和账号密码": "5",
        "∩_∩ 好嘞 登录成功": "6",
        "∩_∩ 使用系统数据 自动登录成功": "7",
        "观看结束～": "8",
        "切换语言成功": "9",
        "切换语言失败": "10",
        "无法登陆，账号密码可能错误或者网络出现问题": "11",
        "눈_눈 开始重试": "12",
        "配置文件找不到": "13",
        "按任意键退出": "14",
        "配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠": "1",
        "配置文件中没有账号密码信息": "1",
        "检查间隔配置错误,已恢复默认值": "1",
        "睡眠时间段配置错误,已恢复默认值": "1",
        "最大运行时间配置错误,已恢复默认值": "1",
        "代理配置错误,已恢复默认值": "1",
        "用户数据userDataDir路径配置错误,已恢复默认值": "1",
        "语言配置错误,已恢复zh_CN默认值": "1",
        '正常观看 可获取奖励': "1",
        "观看异常 重试中...": "1",
        "观看异常": "1",
        "〒.〒 检查掉落失败": "1",
        "〒.〒 掉落提醒失败": "1",
        "Π——Π 无法打开Lolesports网页，网络问题": "1",
        "눈_눈 登录中...": "1",
        "∩_∩ 账密 提交成功": "1",
        "×_× 网络问题 登录超时": "1",
        "请输入二级验证代码:": "1",
        "二级验证代码提交成功": "1",
        "免密登录失败,请去浏览器手动登录后再行尝试": "1",
        "检查掉落数失败": "1",
        "●_● 开始检查...": "1",
        "$_$ 本次运行掉落总和:": "1",
        "生涯总掉落:": "1",
        "〒.〒 没有赛区正在直播": "1",
        "赛区正在直播中": "1",
        "处于休眠时间，检查时间间隔为1小时": "1",
        "下一次检查在:": "1",
        "预计结束程序时间:": "1",
        "Q_Q 对应窗口找不到": "1",
        "Q_Q 发生错误": "1",
        "Q_Q 获取比赛列表失败": "1",
        "比赛结束": "1",
        "Q_Q 关闭已结束的比赛时发生错误": "1",
        "比赛跳过": "1",
        "°D° 关闭 Twitch 流失败.": "1",
        ">_< Twitch 160p清晰度设置成功": "1",
        ">_< Twitch 流关闭成功": "1",
        "°D° Twitch 清晰度设置失败": "1",
        "°D° 无法设置 Twitch 清晰度.": "1",
        "°D° 关闭 Youtube 流失败.": "1",
        ">_< Youtube 流关闭成功": "1",
        ">_< Youtube 144p清晰度设置成功": "1",
        "°D° Youtube 清晰度设置失败": "1",
        "°D° 无法设置 Youtube 清晰度.": "1",
        "下一场比赛时间:": "1",
        "Q_Q 获取下一场比赛时间失败": "1",
        "Q_Q 获取掉落数失败": "1",
        "$_$ 本次运行掉落详细:": "1",
        "QAQ 统计掉落失败": "1",
        "QAQ 初始化掉落数失败": "1",
        "小傻瓜，出事啦": "1",
        "错误提醒发送成功": "1",
        "错误提醒发送失败": "1",
        ">_< 异常提醒成功": "1",
        "异常提醒失败": "1",
        "下载override文件失败": "1",
        "ㅍ_ㅍ 正在准备中...": "1",
        "不支持的操作系统": "1",
        }


class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, error):
        error = ""
        if self.config.desktopNotify:
            try:
                notification.notify(
                    title=_log("小傻瓜，出事啦", lang=self.config.language),
                    message=f"Error Message: {error}",
                    timeout=30
                )
                print(_("错误提醒发送成功", color="green", lang=self.config.language))
                log.info(_log("错误提醒发送成功", lang=self.config.language))
            except Exception as e:
                print(_("错误提醒发送失败", color="red", lang=self.config.language))
                log.error(_log("错误提醒发送失败", lang=self.config.language))
                log.error(format_exc())
        if self.config.connectorDropsUrl != "":
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            try:
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Stop Farming Drop",
                            "title": error,
                            "picUrl": "",
                            "messageUrl": ""
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "Stop Farming Drop",
                        "description": f"{error}",
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
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                else:
                    params = {
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                log.info(_log(">_< 异常提醒成功", lang=self.config.language))
                print(_("异常提醒成功", color="green", lang=self.config.language))
            except Exception as e:
                print(_("异常提醒失败", color="red", lang=self.config.language))
                log.error(_("异常提醒失败", lang=self.config.language))
                log.error(format_exc())

    def debugScreen(self, driver, lint=""):
        try:
            if self.config.debug:
                log.info(f"DebugScreen: {lint} Successful")
                driver.save_screenshot(f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
        except Exception:
            log.error("DebugScreen: Failed")
            log.error(format_exc())

    def info(self):
        if self.config.language == "zh_CN":
            print("[green]=========================================================")
            print(
                f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
            print("[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
            print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
            print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
            print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
            print("[green]====[/green]  如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. [green]====[/green]")
            print("[green]=========================================================")
            print()
            VersionManager.checkVersion()
        elif self.config.language == "en_US":
            print("[green]=========================================================")
            print(
                f"[green]========[/green] Thanks for using [blue]EsportsHelper[/blue] v{VersionManager.getVersion()}!  [green]========[/green]")
            print("[green]=========[/green]  The program is open source at github  [green]=========[/green]")
            print("[green]====[/green]    https://github.com/Yudaotor/EsportsHelper[green]    ====[/green]")
            print("[green]====[/green]      If you like it, please give me a star      [green]====[/green]")
            print("[green]=========================================================")


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg):
    try:
        notification.notify(
            title="Get Drop!",
            message=f"BY {eventTitle} GET{dropItem} {unlockedDate}",
            timeout=30
        )
        log.info("Desktop Notify Successful")
    except Exception as e:
        log.error("Desktop Notify Failed")
        log.error(format_exc())


def sysQuit(driver=None, e=None):
    sleep(3)
    if driver:
        driver.quit()
    log.error(e)
    log.info("------Quit------")
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
            log.error("get overrides file failed")
            input("Press any key to exit...")
            sys.exit()
    except MaxRetryError:
        log.error("get overrides file failed")
        print(f"[red]〒.〒 get overrides file failed, Try later[/red]")
        input("Press any key to exit...")
        sysQuit(e="get overrides file failed")
    except Exception as ex:
        print_exc()
        log.error("get overrides file failed")
        print(f"[red]〒.〒 get overrides file failed, Try later[/red]")
        input("Press any key to exit...")
        sysQuit(e="get overrides file failed")


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
        print("[red]Q_Q Get LoLesports Web Page Failed,Retrying...[/red]")
        log.error("Q_Q Get LoLesports Web Page Failed,Retrying...")
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")


def _(text, color, lang="zh_CN"):
    if lang == "zh_CN":
        return f"[{color}]{text}"
    elif lang == "en_US":
        return f"[{color}]{i18n.get(text)}"


def _log(text, lang="zh_CN"):
    if lang == "zh_CN":
        return f"{text}"
    elif lang == "en_US":
        return f"{i18n.get(text)}"
