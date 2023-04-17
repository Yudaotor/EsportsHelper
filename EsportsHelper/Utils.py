import sys
from time import sleep, strftime
from traceback import format_exc, print_exc

import requests
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from retrying import retry
from rich import print
from urllib3.exceptions import MaxRetryError

i18n = {"WebDriver generation failure!\nThe latest version of Google Chrome is not found.\nPlease check if Chrome downloaded or has the latest version.\nYou can also try to launch the program as an administrator.\nExit the program by pressing any key...",
        "WebDriver generation failure!\nIs Google Chrome installed?\nIs Google Chrome currently open? Please close it and try again.\nExit the program by pressing any key...",
        "WebDriver generation failure!\nIs Google Chrome installed?\nIs there a network problem? Check VPN availability if one connected.\nExit the program by pressing any key...",
        "Network problem: cannot open LolEsports website. Exiting in 3 seconds...",
        "Automatic login failed. Please check the network availability and account credentials.",
        "Logged in successfully.",
        "Using system data. Auto-login success.",
        "Watch finished.",
        "Language switched successfully.",
        "The language switch failed.",
        "Login failed: wrong credentials or network problem.",
        "Restarting.",
        "Configuration file not found.",
        "Exit the program by pressing any key.",
        "Configuration file format error.\nPlease check if there are Chinese characters and single spaces after colons.\nChange single slash to double in configuration path if there are any.",
        "There are no account credentials in the configuration file.",
        "Incorrect interval configuration. The default value has been restored.",
        "Incorrect sleep time preiod. The default value has been restored.",
        "The maximum runtime set incorrectly. The default value has been restored.",
        "Incorrect proxy configuration. The default setting has been restored.",
        "Incorrect UserDataDirectory path configuration. The default setting has been restored.",
        "Incorrect language configuration. The default language zh_CN has been restored.",
        "Watch system operational. Drops available.",
        "Watch system work anomaly. Retrying...",
        "Watch system work anomaly.",
        "Drops check failed.",
        "Drop alert failed.",
        "Network error. Cannot open LolEsports website.",
        "Logging in...",
        "Account credentials sent successfully.",
        "Network error. Login timeout.",
        "Please enter 2FA code:",
        "2FA code submitted successfully.",
        "Authentication failure. Please log in manually using browser and try again.",
        "Failed to check drop count.",
        "Checking...",
        "Session drops:",
        "Lifetime drops:",
        "No live broadcasts.",
        "The match is currently live.",
        "During the sleep period, the check interval is 1 hour.",
        "Next check in:",
        "Time left until the program will auto-close:",
        "The corresponding window cannot be found.",
        "An error has occurred.",
        "Failed to get live broadcasts list.",
        "Broadcast ended.",
        "An error occurred while closing finished broadcast.",
        " match skipped.",
        "Failed to close Twitch stream.",
        "Twitch stream resolution successfully set to 160p.",
        "Twitch stream closed successfully.",
        "Failed to set Twitch stream resolution.",
        "Unable to set Twitch stream resolution.",
        "Failed to close YouTube stream.",
        "YouTube stream closed successfully.",
        "YouTube stream resolution successfully set to 144p.",
        "Failed to set YouTube stream resolution.",
        "Unable to set YouTube stream resolution.",
        "Time of the next broadcast:",
        "Failed to get next broadcast time.",
        "Failed to get drops count.",
        "Details of this session drops:",
        "Failed to count drops.",
        "Failed to initialize drop count.",
        "Hey, something is wrong.",
        "Error alert sent successfully.",
        "Failed to send error alert.",
        "Exception error alert successful.",
        "Exception error alert failed.",
        "Failed to import override file.",
        "Preparing...",
        "Unsupported OS.",
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
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                else:
                    params = {
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
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
                driver.save_screenshot(
                    f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
        except Exception:
            log.error("DebugScreen: Failed")
            log.error(format_exc())

    def info(self):
        if self.config.language == "zh_CN":
            print("[green]=========================================================")
            print(
                f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
            print(
                "[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
            print(
                "[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
            print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
            print(
                "[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
            print(
                "[green]====[/green]  如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. [green]====[/green]")
            print("[green]=========================================================")
            print()
            VersionManager.checkVersion()
        elif self.config.language == "en_US":
            print("[green]=========================================================")
            print(
                f"[green]========[/green] Thanks for using [blue]EsportsHelper[/blue] v{VersionManager.getVersion()}!  [green]========[/green]")
            print(
                "[green]=========[/green]  The program is open source at github  [green]=========[/green]")
            print(
                "[green]====[/green]    https://github.com/Yudaotor/EsportsHelper[green]    ====[/green]")
            print(
                "[green]====[/green]      If you like it, please give me a star      [green]====[/green]")
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
        print(f"[red]get overrides file failed, Try later[/red]")
        input("Press any key to exit...")
        sysQuit(e="get overrides file failed")
    except Exception as ex:
        print_exc()
        log.error("get overrides file failed")
        print(f"[red]get overrides file failed, Try later[/red]")
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
        print("[red]Get LoLesports Web Page Failed,Retrying...[/red]")
        log.error("Get LoLesports Web Page Failed,Retrying...")
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
