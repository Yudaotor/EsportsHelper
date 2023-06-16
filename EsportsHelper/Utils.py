import os
from functools import wraps
from time import sleep, strftime
from traceback import format_exc
import requests
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from EsportsHelper.Config import config
from EsportsHelper.VersionManager import VersionManager, checkVersion
from plyer import notification
from retrying import retry
from rich import print
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n

_ = i18n.getText
_log = i18n.getLog


def getGithubFile():
    try:
        overrides = {}
        championTeam = ""
        scheduleUrl = ""
        defaultScheduleUrl = "https://lolesports.com/schedule?" \
                             "leagues=lcs,north_american_challenger_league," \
                             "lcs_challengers_qualifiers,college_championship," \
                             "cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs," \
                             "turkiye-sampiyonluk-ligi,vcs,msi,worlds,all-star," \
                             "emea_masters,lfl,nlc,elite_series,liga_portuguesa," \
                             "pg_nationals,ultraliga,superliga,primeleague," \
                             "hitpoint_masters,esports_balkan_league," \
                             "greek_legends,arabian_league,lck_academy," \
                             "ljl_academy,lck_challengers_league,cblol_academy," \
                             "north_regional_league,south_regional_league,tft_esports"
        req = requests.session()
        headers = {'Content-Type': 'text/plain; charset=utf-8',
                   'Connection': 'close'}
        try:
            remoteGithubFile = req.get(
                "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
        except Exception:
            log.error(_log("从Github获取参数文件失败, 将尝试从Gitee获取"))
            log.error(formatExc(format_exc()))
            print(_("从Github获取参数文件失败, 将尝试从Gitee获取", color="red"))
            remoteGithubFile = req.get(
                "https://gitee.com/yudaotor/EsportsHelper/raw/main/override.txt", headers=headers)
        if remoteGithubFile.status_code == 200:
            infos = remoteGithubFile.text.split(",")
            for line in infos:
                urls = line.split("|")
                if len(urls) == 2:
                    urls[0] = urls[0][1:]
                    overrides[urls[0]] = urls[1]
                elif "championTeam: " in line:
                    championTeam = line[14:]
                elif "scheduleUrl: " in line:
                    scheduleUrl = line[14:]
            log.info(_log("获取参数文件成功"))
            if championTeam == "":
                log.info(_log("获取冠军队伍失败"))
            if scheduleUrl == "":
                scheduleUrl = defaultScheduleUrl
                log.info(_log("获取地址URL失败"))
            if scheduleUrl:
                scheduleUrl = scheduleUrl.replace("!", ",")
            req.close()
            return overrides, championTeam, scheduleUrl
        else:
            print(_("获取参数文件失败", color="red"))
            log.error(_log("获取参数文件失败"))
            input(_log("按回车键退出"))
            req.close()
            sysQuit(e=_log("获取参数文件失败"))
    except Exception:
        log.error(_log("获取参数文件失败"))
        print(_("获取参数文件失败", color="red"))
        input(_log("按回车键退出"))
        sysQuit(e=_log("获取参数文件失败"))


class Utils:
    def __init__(self):
        self.config = config

    def errorNotify(self, error):
        """
        Sends error notifications to selected channels based on the user's configuration settings.

        Args:
            error (str): The error message to be included in the notification.

        """
        notifyType = self.config.notifyType
        needDesktopNotify = self.config.desktopNotify
        connectorUrl = self.config.connectorDropsUrl
        if notifyType in ["all", "error"]:
            if needDesktopNotify:
                try:
                    notification.notify(
                        title=_log("小傻瓜，出事啦"),
                        message=f"Error Message: {error}",
                        timeout=30
                    )
                    print(_("错误提醒发送成功", color="green"))
                    log.info(_log("错误提醒发送成功"))
                except Exception:
                    print(_("错误提醒发送失败", color="red"))
                    log.error(_log("错误提醒发送失败"))
                    log.error(formatExc(format_exc()))

            if connectorUrl != "":
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                try:
                    if "https://oapi.dingtalk.com" in connectorUrl:
                        data = {
                            "msgtype": "link",
                            "link": {
                                "text": "Alert: Drop farming stopped",
                                "title": error,
                                "picUrl": "",
                                "messageUrl": ""
                            }
                        }
                        s.post(connectorUrl, json=data)

                    elif "https://discord.com/api/webhooks" in connectorUrl:
                        embed = {
                            "title": "Alert: Drop farming stopped",
                            "description": f"{error}",
                            "image": {"url": f""},
                            "thumbnail": {"url": f""},
                            "color": 6676471,
                        }
                        params = {
                            "username": "EsportsHelper",
                            "embeds": [embed]
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    else:
                        params = {
                            "text": f"发生错误停止获取Drop{error}",
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    log.info(_log("异常提醒成功"))
                    print(_("异常提醒成功", color="green"))
                except Exception:
                    print(_("异常提醒失败", color="red"))
                    log.error(_log("异常提醒失败"))
                    log.error(formatExc(format_exc()))

    def debugScreen(self, driver, lint="normal"):
        """
        Function Name: debugScreen
        Input:
            - driver: webdriver object
            - lint: string (default: "")
        Output: None
        Purpose: Saves a screenshot of the current webpage for debugging purposes.
                 The screenshot is saved to ./logs/pics/ directory with a timestamp and a lint identifier.
                 If the lint parameter is not specified, an empty string will be used as the identifier.
        """
        try:
            if self.config.debug:
                sleep(3)
                driver.save_screenshot(f"./logs/pics/{strftime('%m.%d_%H-%M')}-{lint}.png")
                log.info(f'{lint}-{_log("调试截图成功")}')
        except Exception:
            log.error(f'{lint}-{_log("调试截图失败")}')
            log.error(formatExc(format_exc()))

    def info(self):
        """
        Print program information based on the selected language.
        """
        version = VersionManager.getVersion()
        githubUrl = "https://github.com/Yudaotor/EsportsHelper"
        checkVersion()
        if self.config.language == "zh_CN":
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感谢使用 [cyan]电竞助手[/cyan] v {version}!       "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程序开源于github链接地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如觉得不错的话可以进上面链接请我喝杯咖啡支持下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print()
        elif self.config.language == "en_US":
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow] "
                  f"Thanks for using [cyan]EsportsHelper[/cyan] v {version}! "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]   "
                  f"The program is open source at GitHub  "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]    "
                  f"{githubUrl}    [bold yellow]{'=' * 4}"
                  f">_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]      "
                  f"If you like it, please give me a star      "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print()
        elif self.config.language == "zh_TW":
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感謝使用 [cyan]電競助手[/cyan] v {version}!       "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程式開源於github連結地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如覺得不錯的話可以進上面連結請我喝杯咖啡支援下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"請在使用前[red]閱讀教程檔案[/red], 以確保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需關閉請勿直接右上角X關閉，請按Ctrl+C來關閉. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f">_<"
                f"[bold yellow]{CHAMPION_TEAM}[/bold yellow]"
                f"{'=' * (27 - len(CHAMPION_TEAM))}"
                f">_<[/bold yellow]"
            )
            print()


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg, dropLocale, todayDrops):
    """
    Desktop notification function that sends a notification to the user's desktop.

    Args:
    poweredByImg (str): The image URL of the company that powers the event.
    productImg (str): The image URL of the product being dropped.
    unlockedDate (str): The date and time when the drop will be unlocked.
    eventTitle (str): The title of the event.
    dropItem (str): The name of the dropped item.
    dropItemImg (str): The image URL of the dropped item.
    dropLocale (str): The location where the drop will occur.
    todayDrops (str): The number of drops for the day.
    """
    try:
        notification.notify(
            title=f"{_log('新的掉落!')}{_log('今日: ')}{todayDrops}",
            message=f"{_log('通过')} {eventTitle} {_log('获得')} {dropItem} {_log('于')} {dropLocale} {unlockedDate}",
            timeout=30
        )
        log.info(_log("桌面提醒成功发送"))
    except Exception:
        log.error(_log("桌面提醒发送失败"))
        log.error(formatExc(format_exc()))


def sysQuit(driver=None, e=None):
    """
    Function: sysQuit
    Description: Safely quits the webdriver and exits the program.
    Input:
        - driver: Webdriver instance to be quit
        - e: Exception that occurred (optional)
    Output: None
    """
    sleep(1)
    if driver:
        driver.quit()
    if e:
        log.error(e)
    log.info(_log("程序退出"))
    os.kill(os.getpid(), 9)


def getMatchName(url: str) -> str:
    """
    Returns the name of the match corresponding to the given URL.

    Args:
        url (str): A string that represents a URL.

    Returns:
        str: A string that represents the name of the match.
    """
    match = url.split('/')[-2] if url.split('/')[-2] != "live" else url.split('/')[-1]
    match = "cblol" if match == "cblol-brazil" else match
    match = "ljl" if match == "ljl-japan" else match
    match = "tft" if match == "tft_esports" else match
    match = match.upper()
    return match


# Repeat the attempt to fetch the page up to 4 times,
# and the wait time is based on 2 minutes, each time incremented by 2 minutes
@retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
def getLolesportsWeb(driver) -> None:
    """
    Retrieves the Lolesports website using the provided driver. If an exception occurs while accessing the website,
    it retries for a maximum of four times, incrementing the wait time between each attempt by two minutes.

    Args:
    - driver (selenium.webdriver.remote.webdriver.WebDriver): The driver to use for accessing the Lolesports website
    """
    try:
        driver.get(SCHEDULE_URL)

    except Exception:
        print(_("获取LoLEsports网站失败，正在重试...", color="red"))
        log.error(_log("获取LoLEsports网站失败，正在重试..."))
        log.error(formatExc(format_exc()))
        driver.get(SCHEDULE_URL)


def getSleepPeriod():
    """
    Get sleep period from config file
    """
    return [int(period.split("-")[0]) for period in config.sleepPeriod if period], \
           [int(period.split("-")[1]) for period in config.sleepPeriod if period]


@retry(stop_max_attempt_number=4, wait_incrementing_increment=10000, wait_incrementing_start=10000)
def checkRewardPage(driver):
    """
    Check if the reward page exists.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        - None if the reward page does not exist.
        - Returns without any value if the reward page exists.
    """
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.name")))
    except Exception:
        try:
            # Special cases where there is no drop ---- new account
            wait.until(ec.presence_of_element_located(
                (By.XPATH, "//div[text()='NO DROPS YET']")))
        except Exception:
            utils = Utils()
            utils.debugScreen(driver, "rewardError")
            if len(driver.find_elements(By.CSS_SELECTOR, "div.InformBubble.error")) > 0:
                print(f'--{_("Riot原因,reward页面出现异常无法正常加载", color="red")}')
                log.error(_log("Riot原因,该页面出现异常无法正常加载"))
            else:
                driver.refresh()
                print(f'--{_("获取reward网站失败，正在重试...", color="red")}')
                log.error(_log("获取reward网站失败，正在重试..."))
                log.error(formatExc(format_exc()))
                wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.name")))
        else:
            return


def getMatchTitle(teams):
    """
    Get match teams from stream title
    """
    teams = teams.replace("│", "|")
    if not teams or ("|" not in teams and "-" not in teams and "vs" not in teams.lower()):
        return _log("出错, 未知")

    delimiter = "|" if "|" in teams else "-"
    words = teams.split(delimiter)
    teamNames = [word for word in words if "vs" in word.lower()]
    if teamNames:
        return "-".join(teamNames)
    else:
        return words[0]


def acceptCookies(driver):
    try:
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.osano-cm-accept-all"))).click()
        log.info(_log("接受cookies"))
        return True
    except TimeoutException:
        log.info(_log("未找到cookies按钮(正常情况)"))
        return True
    except Exception:
        log.error(_log("接受cookies失败"))
        log.error(formatExc(format_exc()))
        return False


def mouthTrans(mouth):
    trans = {"jan": "1月", "feb": "2月", "mar": "3月", "apr": "4月",
             "may": "5月", "jun": "6月", "jul": "7月", "aug": "8月",
             "sep": "9月", "oct": "10月", "nov": "11月", "dec": "12月"}
    try:
        if i18n.language == "zh_CN" or i18n.language == "zh_TW":
            return trans.get(mouth.lower()[:3], mouth)
        else:
            return mouth
    except Exception:
        log.error(formatExc(format_exc()))
        return mouth


def timeTrans(time):
    try:
        if i18n.language == "zh_CN" or i18n.language == "zh_TW":
            if time[-2:] == "AM" and time[:-2] != "12":
                return log("上午") + time[:-2] + log("点")
            elif time[-2:] == "AM" and time[:-2] == "12":
                return log("凌晨") + time[:-2] + log("点")
            elif time[-2:] == "PM":
                return log("下午") + time[:-2] + log("点")
        else:
            return time
    except Exception:
        log.error(formatExc(format_exc()))
        return time


def formatExc(error):
    modifiedTrace = f"{50 * '+'}\n"
    lines = error.splitlines()
    for line in lines:
        if "Stacktrace:" in line:
            break
        modifiedTrace += line + '\n'
    return modifiedTrace


OVERRIDES, CHAMPION_TEAM, SCHEDULE_URL = getGithubFile()
